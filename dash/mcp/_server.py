"""Flask route setup, Streamable HTTP transport, and MCP message handling."""

# pylint: disable=cyclic-import
# The MCP server imports dash primitives to dispatch callbacks, and dash
# lazy-imports this module to wire the MCP endpoint. Cycle is managed here.

from __future__ import annotations

import json
import logging
import uuid
from typing import TYPE_CHECKING, Any

from flask import Response, request
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

from dash import get_app
from dash._get_app import with_app_context_factory
from dash.mcp._decorator import MCP_DECORATED_FUNCTIONS
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
from dash.mcp.types import MCPError
from dash.version import __version__

if TYPE_CHECKING:
    from dash import Dash

logger = logging.getLogger(__name__)


def enable_mcp_server(app: Dash, mcp_path: str) -> None:
    """Add MCP routes to a Dash/Flask app."""

    app.mcp_decorated_functions = dict(MCP_DECORATED_FUNCTIONS)
    MCP_DECORATED_FUNCTIONS.clear()

    _session_id: str | None = None

    def _get_or_create_session_id() -> str:
        """Read the hot-reload hash or generate a stable fallback."""
        # pylint: disable=protected-access
        reload_hash = app._hot_reload.hash
        return reload_hash if reload_hash is not None else uuid.uuid4().hex

    def _is_session_stale(client_session_id: str | None) -> bool:
        """True when the client's session doesn't match or the hash changed."""
        if client_session_id != _session_id:
            return True
        # pylint: disable=protected-access
        reload_hash = app._hot_reload.hash
        if reload_hash is None:
            return False
        return reload_hash != _session_id

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
        # MCP spec allows servers to opt out of GET-initiated SSE streams
        # by returning 405. We don't push server-initiated events.
        return Response(
            json.dumps({"error": "Method not allowed"}),
            content_type="application/json",
            status=405,
        )

    def _check_session(method: str) -> bool:
        """Validate the session header.

        Raises ``ValueError`` when the header is missing.
        Returns ``True`` when the session was stale and transparently
        recovered, or ``False`` when the session is valid.
        """
        nonlocal _session_id
        if method == "initialize":
            _session_id = _get_or_create_session_id()
            return False
        client_session_id = request.headers.get("Mcp-Session-Id")
        if _session_id is not None and not client_session_id:
            raise ValueError("Missing Mcp-Session-Id header")
        if _is_session_stale(client_session_id):
            _session_id = _get_or_create_session_id()
            logger.debug("MCP session recovered: %s", _session_id)
            return True
        return False

    def _json_response(*messages: dict) -> Response:
        """Wrap one or more JSON-RPC messages in a Flask Response.

        A single message is serialised as a JSON object; multiple
        messages are serialised as a JSON array.
        """
        body = messages[0] if len(messages) == 1 else list(messages)
        resp = Response(
            json.dumps(body),
            content_type="application/json",
            status=200,
        )
        if _session_id is not None:
            resp.headers["Mcp-Session-Id"] = _session_id
        return resp

    def _handle_post() -> Response:
        content_type = request.content_type or ""
        if "application/json" not in content_type:
            return Response(
                json.dumps({"error": "Content-Type must be application/json"}),
                content_type="application/json",
                status=415,
            )

        data = request.get_json(silent=True)
        if data is None:
            return Response(
                json.dumps({"error": "Invalid JSON"}),
                content_type="application/json",
                status=400,
            )

        method = data.get("method", "")

        try:
            is_stale_session = _check_session(method)
        except ValueError as err:
            return Response(
                json.dumps({"error": str(err)}),
                content_type="application/json",
                status=400,
            )

        response_data = _process_mcp_message(data)

        if response_data is None:
            return Response("", status=202)

        if is_stale_session:
            return _json_response(
                {"jsonrpc": "2.0", "method": "notifications/tools/list_changed"},
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/resources/list_changed",
                },
                response_data,
            )

        return _json_response(response_data)

    def _handle_delete() -> Response:
        # No sessions to terminate — server is stateless.
        return Response(
            json.dumps({"error": "Method not allowed"}),
            content_type="application/json",
            status=405,
        )

    # -- Register routes -----------------------------------------------------

    # pylint: disable-next=protected-access
    app._add_url(
        mcp_path, with_app_context_factory(mcp_handler, app), ["GET", "POST", "DELETE"]
    )

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
            resources=ResourcesCapability(listChanged=True),
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
    _id = data.get("id")
    request_id: str | int = _id if isinstance(_id, (str, int)) else ""

    app = get_app()
    if not hasattr(app, "mcp_callback_map"):
        app.mcp_callback_map = CallbackAdapterCollection(app)

    mcp_methods = {
        "initialize": _handle_initialize,
        "tools/list": list_tools,
        "tools/call": lambda: call_tool(
            params.get("name", ""), params.get("arguments", {})
        ),
        "resources/list": list_resources,
        "resources/templates/list": list_resource_templates,
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
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("MCP error: %s", e, exc_info=True)
        return JSONRPCError(
            jsonrpc="2.0",
            id=request_id,
            error=ErrorData(code=-32603, message=f"{type(e).__name__}: {e}"),
        ).model_dump(exclude_none=True)
