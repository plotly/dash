"""Tests for MCP server (_server.py) — JSON-RPC message processing."""

from dash._get_app import app_context
from dash.mcp._server import _process_mcp_message
from mcp.types import LATEST_PROTOCOL_VERSION

from tests.unit.mcp.conftest import (
    _make_app,
    _mcp,
    _tools_list,
    _call_tool,
    _call_tool_output,
)


class TestProcessMCPMessage:
    def test_initialize(self):
        app = _make_app()
        result = _mcp(app, "initialize")

        assert result is not None
        assert result["id"] == 1
        assert result["jsonrpc"] == "2.0"
        assert result["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION
        assert "serverInfo" in result["result"]

    def test_initialize_advertises_list_changed(self):
        app = _make_app()
        result = _mcp(app, "initialize")
        caps = result["result"]["capabilities"]
        assert caps["tools"]["listChanged"] is True

    def test_tools_call(self):
        app = _make_app()
        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "update_output" in t["name"])

        result = _call_tool(app, tool_name, {"value": "hello"}, request_id=2)

        assert result is not None
        assert result["id"] == 2
        assert _call_tool_output(app, tool_name, {"value": "hello"}) == "echo: hello"

    def test_tools_call_unknown_tool_returns_error(self):
        app = _make_app()
        result = _call_tool(app, "nonexistent_tool")

        assert result is not None
        assert "error" in result
        assert result["error"]["code"] == -32601

    def test_unknown_method_returns_error(self):
        app = _make_app()
        result = _mcp(app, "unknown/method")

        assert result is not None
        assert "error" in result

    def test_notification_returns_none(self):
        app = _make_app()
        data = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        with app.server.test_request_context():
            app_context.set(app)
            result = _process_mcp_message(data)
        assert result is None
