"""Flask route setup, Streamable HTTP transport, and MCP message handling."""

# pylint: disable=cyclic-import
# The MCP server imports dash primitives to dispatch callbacks, and dash
# lazy-imports this module to wire the MCP endpoint. Cycle is managed here.

from __future__ import annotations

import hashlib
import inspect
import json
import logging
import os
from typing import TYPE_CHECKING, Any

from dash.mcp.types import (
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
from dash.mcp._decorator import MCP_DECORATED_FUNCTIONS
from dash.mcp.primitives import (
    call_tool,
    list_resource_templates,
    list_resources,
    list_tools,
    read_resource,
)
from dash.mcp.tasks import get_task, get_task_result, cancel_task
from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)
from dash.mcp.types import MCPError
from dash.version import __version__

if TYPE_CHECKING:
    from dash import Dash

logger = logging.getLogger(__name__)


def enable_mcp_server(app: Dash, mcp_path: str) -> None:
    """Add MCP routes to a Dash app."""

    def _get_or_create_session_id() -> str:
        """
        Creates a shared session ID shared across all clients. The session is
        used to notify clients of app restarts so they can refresh their view
        of the app.
        When hot-reloading is enabled, the reload_hash is used
        Otherwise, the parent PID is used because it is a stable identifier
        across different worker processes.
        """
        # pylint: disable=protected-access
        reload_hash = app._hot_reload.hash
        if reload_hash is not None:
            return reload_hash
        return hashlib.sha256(f"dash-mcp-{os.getppid()}".encode()).hexdigest()[:32]

    _session_id: str = _get_or_create_session_id()

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

    def _check_session(method: str) -> bool:
        """Validate the session header.

        Raises ``ValueError`` when the header is missing.
        Returns ``True`` when the session was stale and transparently
        recovered, or ``False`` when the session is valid.
        """
        nonlocal _session_id
        adapter = app.backend.request_adapter()
        if method == "initialize":
            _session_id = _get_or_create_session_id()
            return False
        client_session_id = adapter.headers.get("Mcp-Session-Id")
        if client_session_id and _is_session_stale(client_session_id):
            _session_id = _get_or_create_session_id()
            logger.debug("MCP session recovered: %s", _session_id)
            return True
        return False

    def _json_response(*messages: dict):
        """Wrap one or more JSON-RPC messages in a response.

        A single message is serialised as a JSON object; multiple
        messages are serialised as a JSON array.
        """
        body = messages[0] if len(messages) == 1 else list(messages)
        resp = app.backend.make_response(
            json.dumps(body),
            content_type="application/json",
            status=200,
        )
        if _session_id is not None:
            resp.headers["Mcp-Session-Id"] = _session_id
        return resp

    def _handle_post() -> Any:
        adapter = app.backend.request_adapter()
        return _handle_mcp_request(adapter.get_json())

    async def _handle_post_async() -> Any:
        adapter = app.backend.request_adapter()
        return _handle_mcp_request(await adapter.get_json())

    def _handle_mcp_request(data) -> Any:
        adapter = app.backend.request_adapter()
        content_type = adapter.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            return app.backend.make_response(
                json.dumps({"error": "Content-Type must be application/json"}),
                content_type="application/json",
                status=415,
            )

        if data is None:
            return app.backend.make_response(
                json.dumps({"error": "Invalid JSON"}),
                content_type="application/json",
                status=400,
            )

        method = data.get("method", "")

        try:
            is_stale_session = _check_session(method)
        except ValueError as err:
            return app.backend.make_response(
                json.dumps({"error": str(err)}),
                content_type="application/json",
                status=400,
            )

        response_data = _process_mcp_message(data)

        if response_data is None:
            return app.backend.make_response("", status=202)

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

    def _handle_get():
        """
        Accept GET requests for SSE streams with an empty, immediately-completed
        stream. This used to be a 405 "Method Not Allowed", but that caused the
        dev server to close the connection, introducing intermittent Claude
        connectivity timeouts.
        """
        resp = app.backend.make_response(
            ": mcp stream open\n\n",
            content_type="text/event-stream",
            status=200,
        )
        resp.headers["Cache-Control"] = "no-cache, no-transform"
        if _session_id is not None:
            resp.headers["Mcp-Session-Id"] = _session_id
        return resp

    def _handle_delete():
        """Return 405 for DELETE; the spec allows refusing session teardown."""
        return app.backend.make_response(
            json.dumps({"error": "Method not allowed"}),
            content_type="application/json",
            status=405,
        )

    # -- Register routes -----------------------------------------------------
    # Separate registrations per HTTP method so the handler never needs to
    # inspect the request method.  Distinct endpoint names are required by
    # Flask / Werkzeug when the same URL rule is registered more than once.
    if inspect.iscoroutinefunction(app.backend.request_adapter.get_json):
        post_handler = _handle_post_async
    else:
        post_handler = _handle_post
    mcp_url = app.config.routes_pathname_prefix + mcp_path
    app.backend.add_url_rule(
        mcp_url,
        view_func=post_handler,
        endpoint=f"{mcp_url}:POST",
        methods=["POST"],
    )
    app.backend.add_url_rule(
        mcp_url,
        view_func=_handle_get,
        endpoint=f"{mcp_url}:GET",
        methods=["GET"],
    )
    app.backend.add_url_rule(
        mcp_url,
        view_func=_handle_delete,
        endpoint=f"{mcp_url}:DELETE",
        methods=["DELETE"],
    )
    app.routes.append(mcp_url)

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
    if app.mcp_callback_map is None:
        app.mcp_callback_map = CallbackAdapterCollection(app)
        app.mcp_decorated_functions = dict(MCP_DECORATED_FUNCTIONS)

    mcp_methods = {
        "initialize": _handle_initialize,
        "tools/list": list_tools,
        "tools/call": lambda: call_tool(
            tool_name=params.get("name", ""),
            arguments=params.get("arguments", {}),
            task=params.get("task"),
        ),
        "resources/list": list_resources,
        "resources/templates/list": list_resource_templates,
        "resources/read": lambda: read_resource(params.get("uri", "")),
        "tasks/get": lambda: get_task(task_id=params.get("taskId", "")),
        "tasks/result": lambda: get_task_result(task_id=params.get("taskId", "")),
        "tasks/cancel": lambda: cancel_task(task_id=params.get("taskId", "")),
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
