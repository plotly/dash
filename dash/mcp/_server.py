"""Flask route setup, Streamable HTTP transport, and MCP message handling."""

from __future__ import annotations

import atexit
import json
import logging
import uuid
from typing import TYPE_CHECKING, Any

from flask import Response, request

from dash.mcp.types import MCPError

if TYPE_CHECKING:
    from dash import Dash

from dash import get_app

from mcp.types import (
    LATEST_PROTOCOL_VERSION,
    ErrorData,
    Implementation,
    InitializeResult,
    JSONRPCError,
    JSONRPCResponse,
    ResourcesCapability,
    ServerCapabilities,
    ToolsCapability,
)

from dash.version import __version__
from dash.mcp._sse import (
    close_sse_stream,
    create_sse_stream,
    shutdown_all_streams,
)
from dash.mcp.primitives import (
    call_tool,
    list_resource_templates,
    list_resources,
    list_tools,
    read_resource,
)
from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)

logger = logging.getLogger(__name__)


def enable_mcp_server(app: Dash, mcp_path: str) -> None:
    """
    Add MCP routes to a Dash/Flask app.

    Registers a single Streamable HTTP endpoint for the MCP protocol.
    Uses ``app._add_url()`` so that ``routes_pathname_prefix`` is applied
    automatically.

    Args:
        app: The Dash application instance.
        mcp_path: Route prefix for MCP endpoints.
    """
    # Session storage: session_id -> metadata
    sessions: dict[str, dict[str, Any]] = {}

    def _create_session() -> str:
        sid = str(uuid.uuid4())
        sessions[sid] = {}
        return sid

    # -- Streamable HTTP endpoint --------------------------------------------

    def mcp_handler() -> Response:
        if request.method == "POST":
            return _handle_post()
        if request.method == "GET":
            return _handle_get()
        if request.method == "DELETE":
            return _handle_delete()
        return Response(
            json.dumps({"error": "Method not allowed"}),
            content_type="application/json",
            status=405,
        )

    def _handle_get() -> Response:
        session_id = request.headers.get("mcp-session-id")
        if not session_id or session_id not in sessions:
            return Response(
                json.dumps({"error": "Session not found"}),
                content_type="application/json",
                status=404,
            )
        return create_sse_stream(sessions, session_id)

    def _handle_post() -> Response:
        content_type = request.content_type or ""
        if "application/json" not in content_type:
            return Response(
                json.dumps({"error": "Content-Type must be application/json"}),
                content_type="application/json",
                status=415,
            )

        try:
            data = request.get_json()
        except Exception:
            return Response(
                json.dumps({"error": "Invalid JSON"}),
                content_type="application/json",
                status=400,
            )

        method = data.get("method", "")
        request_id = data.get("id")
        session_id = request.headers.get("mcp-session-id")

        if method == "initialize":
            session_id = _create_session()
        elif session_id and session_id not in sessions:
            return Response(
                json.dumps({"error": "Session not found. Please reinitialize."}),
                content_type="application/json",
                status=404,
            )
        elif not session_id:
            return Response(
                json.dumps(
                    {"error": "Missing session ID. Send an initialize request first."}
                ),
                content_type="application/json",
                status=400,
            )

        response_data = _process_mcp_message(data)

        if response_data is None:
            return Response("", status=202)

        return Response(
            json.dumps(response_data),
            content_type="application/json",
            status=200,
            headers={"mcp-session-id": session_id},
        )

    def _handle_delete() -> Response:
        session_id = request.headers.get("mcp-session-id")
        if not session_id or session_id not in sessions:
            return Response(
                json.dumps({"error": "Session not found"}),
                content_type="application/json",
                status=404,
            )
        close_sse_stream(sessions[session_id])
        del sessions[session_id]
        logger.info("MCP session terminated: %s", session_id)
        return Response("", status=204)

    # -- Register routes -----------------------------------------------------

    from dash._get_app import with_app_context_factory

    app._add_url(
        mcp_path, with_app_context_factory(mcp_handler, app), ["GET", "POST", "DELETE"]
    )

    # Close all SSE streams on server shutdown so MCP clients see a
    # clean stream end and can reconnect promptly.
    atexit.register(shutdown_all_streams, sessions)

    logger.info(
        "MCP routes registered at %s%s",
        app.config.routes_pathname_prefix,
        mcp_path,
    )


def _handle_initialize() -> InitializeResult:
    return InitializeResult(
        protocolVersion=LATEST_PROTOCOL_VERSION,
        capabilities=ServerCapabilities(
            tools=ToolsCapability(listChanged=True),
            resources=ResourcesCapability(),
        ),
        serverInfo=Implementation(name="Plotly Dash", version=__version__),
        instructions=(
            "This is a Dash web application. "
            "Dash apps are stateless: calling a tool executes "
            "a callback and returns its result to you, but does "
            "NOT update the user's browser. "
            "Use tool results to answer questions about what "
            "the app would produce for given inputs."
        ),
    )


def _process_mcp_message(data: dict[str, Any]) -> dict[str, Any] | None:
    """
    Process an MCP JSON-RPC message and return the response dict.

    Returns ``None`` for notifications (no ``id`` field).
    """
    method = data.get("method", "")
    params = data.get("params", {}) or {}
    request_id = data.get("id")

    app = get_app()
    if not hasattr(app, "mcp_callback_map"):
        app.mcp_callback_map = CallbackAdapterCollection(app)

    mcp_methods = {
        "initialize": _handle_initialize,
        "tools/list": lambda: list_tools(),
        "tools/call": lambda: call_tool(
            params.get("name", ""), params.get("arguments", {})
        ),
        "resources/list": lambda: list_resources(),
        "resources/templates/list": lambda: list_resource_templates(),
        "resources/read": lambda: read_resource(params.get("uri", "")),
    }

    try:
        handler = mcp_methods.get(method)
        if handler is None:
            if method.startswith("notifications/"):
                return None
            raise ValueError(f"Unknown method: {method}")

        result = handler()

        response = JSONRPCResponse(
            jsonrpc="2.0",
            id=request_id,
            result=result.model_dump(exclude_none=True, mode="json"),
        )
        return response.model_dump(exclude_none=True, mode="json")

    except MCPError as e:
        logger.error("MCP error: %s", e)
        return JSONRPCError(
            jsonrpc="2.0",
            id=request_id,
            error=ErrorData(code=e.code, message=str(e)),
        ).model_dump(exclude_none=True)
    except Exception as e:
        logger.error("MCP error: %s", e, exc_info=True)
        return JSONRPCError(
            jsonrpc="2.0",
            id=request_id,
            error=ErrorData(code=-32603, message=f"{type(e).__name__}: {e}"),
        ).model_dump(exclude_none=True)
