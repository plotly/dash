"""Integration tests for @mcp_enabled decorated function tools."""

import json
from typing import Optional

from dash import Dash, html
from dash.mcp import mcp_enabled

from tests.integration.mcp.conftest import _mcp_call_tool, _mcp_tools

BUILTINS = {"get_dash_component"}


def test_mcpd001_bare_decorator_appears_as_tool(dash_duo):
    @mcp_enabled
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    names = [t["name"] for t in tools]
    assert "add_numbers" in names

    tool = next(t for t in tools if t["name"] == "add_numbers")
    assert "Add two numbers" not in tool["description"]


def test_mcpd002_expose_docstring(dash_duo):
    @mcp_enabled(expose_docstring=True)
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    tool = next(
        t for t in _mcp_tools(dash_duo.server.url) if t["name"] == "add_numbers"
    )
    assert "Add two numbers together" in tool["description"]


def test_mcpd003_custom_name_overrides_function_name(dash_duo):
    @mcp_enabled(name="sum_values")
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    names = [t["name"] for t in tools]
    assert "sum_values" in names
    assert "add_numbers" not in names


def test_mcpd004_typed_params_produce_schema(dash_duo):
    @mcp_enabled
    def greet(name: str, times: int) -> str:
        """Greet someone."""
        return name * times

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    tool = next(t for t in _mcp_tools(dash_duo.server.url) if t["name"] == "greet")
    schema = tool["inputSchema"]
    assert schema["type"] == "object"
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["times"]["type"] == "integer"
    assert set(schema["required"]) == {"name", "times"}


def test_mcpd005_optional_param_not_required(dash_duo):
    @mcp_enabled
    def search(query: str, limit: Optional[int] = None) -> str:
        """Search for things."""
        return query

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    tool = next(t for t in _mcp_tools(dash_duo.server.url) if t["name"] == "search")
    schema = tool["inputSchema"]
    assert "query" in schema["required"]
    assert "limit" not in schema["required"]


def test_mcpd006_return_annotation_becomes_output_schema(dash_duo):
    @mcp_enabled
    def compute(x: int) -> str:
        """Compute something."""
        return str(x)

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    tool = next(t for t in _mcp_tools(dash_duo.server.url) if t["name"] == "compute")
    assert tool["outputSchema"]["type"] == "object"
    assert tool["outputSchema"]["properties"]["result"]["type"] == "string"


def test_mcpd007_call_returns_result(dash_duo):
    @mcp_enabled
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    resp = _mcp_call_tool(dash_duo.server.url, "multiply", {"a": 3, "b": 7})
    result = resp["result"]
    assert result["isError"] is not True
    text = result["content"][0]["text"]
    assert json.loads(text) == 21


def test_mcpd008_call_with_custom_name(dash_duo):
    @mcp_enabled(name="product")
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    resp = _mcp_call_tool(dash_duo.server.url, "product", {"a": 4, "b": 5})
    result = resp["result"]
    assert result["isError"] is not True
    text = result["content"][0]["text"]
    assert json.loads(text) == 20


def test_mcpd009_call_error_returns_is_error(dash_duo):
    @mcp_enabled
    def fail_hard(x: int) -> str:
        """Always fails."""
        raise ValueError("boom")

    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    resp = _mcp_call_tool(dash_duo.server.url, "fail_hard", {"x": 1})
    result = resp["result"]
    assert result["isError"] is True
    assert "boom" in result["content"][0]["text"]
