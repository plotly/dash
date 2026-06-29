"""MCP server JSON-RPC message processing (``_process_mcp_message``)."""

from dash._get_app import app_context
from dash.mcp._server import _process_mcp_message
from dash.mcp.types import LATEST_PROTOCOL_VERSION

from tests.unit.mcp.conftest import _make_app, _setup_mcp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _msg(method, params=None, request_id=1):
    d = {"jsonrpc": "2.0", "method": method, "id": request_id}
    d["params"] = params if params is not None else {}
    return d


def _mcp(app, method, params=None, request_id=1):
    with app.server.test_request_context():
        _setup_mcp(app)
        return _process_mcp_message(_msg(method, params, request_id))


def _tools_list(app):
    return _mcp(app, "tools/list")["result"]["tools"]


def _call_tool(app, tool_name, arguments=None, request_id=1):
    return _mcp(
        app, "tools/call", {"name": tool_name, "arguments": arguments or {}}, request_id
    )


def _call_tool_output(
    app, tool_name, arguments=None, component_id=None, prop="children"
):
    result = _call_tool(app, tool_name, arguments)
    structured = result["result"]["structuredContent"]
    response = structured["response"]
    if component_id is None:
        component_id = next(iter(response))
    return response[component_id][prop]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_mcps001_initialize():
    app = _make_app()
    result = _mcp(app, "initialize")

    assert result is not None
    assert result["id"] == 1
    assert result["jsonrpc"] == "2.0"
    assert result["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION
    assert "serverInfo" in result["result"]


def test_mcps002_tools_call():
    app = _make_app()
    tools = _tools_list(app)
    tool_name = next(t["name"] for t in tools if "update_output" in t["name"])

    result = _call_tool(app, tool_name, {"value": "hello"}, request_id=2)

    assert result is not None
    assert result["id"] == 2
    assert _call_tool_output(app, tool_name, {"value": "hello"}) == "echo: hello"


def test_mcps003_tools_call_unknown_tool_returns_error():
    app = _make_app()
    result = _call_tool(app, "nonexistent_tool")

    assert result is not None
    assert "error" in result
    assert result["error"]["code"] == -32601


def test_mcps004_unknown_method_returns_error():
    app = _make_app()
    result = _mcp(app, "unknown/method")

    assert result is not None
    assert "error" in result


def test_mcps005_notification_returns_none():
    app = _make_app()
    data = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    with app.server.test_request_context():
        app_context.set(app)
        result = _process_mcp_message(data)
    assert result is None
