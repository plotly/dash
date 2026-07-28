"""Unit tests for the @mcp_enabled decorator and its tool integration."""

from typing import Optional

from dash import Dash, html
from dash.mcp import mcp_enabled

from tests.unit.mcp.conftest import _setup_mcp, _tools_list, _call_tool

BUILTINS = {"get_dash_component"}


def _make_app_with_decorated():
    app = Dash(__name__)
    app.layout = html.Div(id="root")
    return _setup_mcp(app)


def _user_tools(app):
    return [t for t in _tools_list(app) if t.name not in BUILTINS]


def test_mcpd001_bare_decorator_preserves_function():
    @mcp_enabled
    def double(x: int) -> int:
        return x * 2

    assert double(5) == 10


def test_mcpd002_parameterised_decorator_preserves_function():
    @mcp_enabled(name="doubler")
    def double(x: int) -> int:
        return x * 2

    assert double(5) == 10


def test_mcpd003_bare_decorator_appears_as_tool():
    @mcp_enabled
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = _make_app_with_decorated()
    names = {t.name for t in _user_tools(app)}
    assert "add_numbers" in names


def test_mcpd004_custom_name_overrides_function_name():
    @mcp_enabled(name="sum_values")
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = _make_app_with_decorated()
    names = {t.name for t in _user_tools(app)}
    assert "sum_values" in names
    assert "add_numbers" not in names


def test_mcpd005_docstring_hidden_by_default():
    @mcp_enabled
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = _make_app_with_decorated()
    tool = next(t for t in _user_tools(app) if t.name == "add_numbers")
    assert "Add two numbers" not in tool.description


def test_mcpd006_docstring_exposed_when_opted_in():
    @mcp_enabled(expose_docstring=True)
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b

    app = _make_app_with_decorated()
    tool = next(t for t in _user_tools(app) if t.name == "add_numbers")
    assert "Add two numbers together" in tool.description


def test_mcpd007_typed_params_produce_schema():
    @mcp_enabled
    def greet(name: str, times: int) -> str:
        """Greet someone."""
        return name * times

    app = _make_app_with_decorated()
    tool = next(t for t in _user_tools(app) if t.name == "greet")
    schema = tool.inputSchema
    assert schema["type"] == "object"
    assert schema["properties"]["name"]["type"] == "string"
    assert schema["properties"]["times"]["type"] == "integer"
    assert set(schema["required"]) == {"name", "times"}


def test_mcpd008_optional_param_not_required():
    @mcp_enabled
    def search(query: str, limit: Optional[int] = None) -> str:
        """Search for things."""
        return query

    app = _make_app_with_decorated()
    tool = next(t for t in _user_tools(app) if t.name == "search")
    schema = tool.inputSchema
    assert "query" in schema["required"]
    assert "limit" not in schema["required"]


def test_mcpd009_typed_param_with_default_not_required():
    @mcp_enabled
    def filter_range(min_val: float = -180.0, max_val: float = 180.0) -> list[str]:
        """Filter by range."""
        return []

    app = _make_app_with_decorated()
    tool = next(t for t in _user_tools(app) if t.name == "filter_range")
    schema = tool.inputSchema
    assert "required" not in schema or "min_val" not in schema.get("required", [])
    assert "required" not in schema or "max_val" not in schema.get("required", [])


def test_mcpd010_return_annotation_becomes_output_schema():
    @mcp_enabled
    def compute(x: int) -> str:
        """Compute something."""
        return str(x)

    app = _make_app_with_decorated()
    tool = next(t for t in _user_tools(app) if t.name == "compute")
    assert tool.outputSchema["type"] == "object"
    assert tool.outputSchema["properties"]["result"]["type"] == "string"


def test_mcpd011_call_returns_result():
    @mcp_enabled
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    app = _make_app_with_decorated()
    result = _call_tool(app, "multiply", {"a": 3, "b": 7})
    assert result.isError is not True
    assert result.structuredContent["result"] == 21


def test_mcpd012_call_with_custom_name():
    @mcp_enabled(name="product")
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    app = _make_app_with_decorated()
    result = _call_tool(app, "product", {"a": 4, "b": 5})
    assert result.isError is not True
    assert result.structuredContent["result"] == 20


def test_mcpd013_call_error_returns_is_error():
    @mcp_enabled
    def fail_hard(x: int) -> str:
        """Always fails."""
        raise ValueError("boom")

    app = _make_app_with_decorated()
    result = _call_tool(app, "fail_hard", {"x": 1})
    assert result.isError is True
    assert "boom" in result.content[0].text
