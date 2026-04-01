"""Integration test for duplicate callback outputs.

Multiple callbacks can output to the same component.property
when using ``allow_duplicate=True``. The MCP server must handle
this correctly — both callbacks should appear as tools, and
calling either should work.
"""

from dash import Dash, Input, Output, dcc, html

from tests.integration.mcp.conftest import _mcp_call_tool, _mcp_tools


def _find_tool(tools, name):
    return next((t for t in tools if t["name"] == name), None)


def _get_response(result):
    return result["result"]["structuredContent"]["response"]


def test_duplicate_outputs_both_tools_listed(dash_duo):
    """Both callbacks outputting to the same component appear as tools."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="first-name", value="Jane"),
            dcc.Input(id="last-name", value="Doe"),
            html.Div(id="greeting"),
        ]
    )

    @app.callback(
        Output("greeting", "children"),
        Input("first-name", "value"),
    )
    def greet_by_first(first):
        return f"Hello, {first}!"

    @app.callback(
        Output("greeting", "children", allow_duplicate=True),
        Input("last-name", "value"),
        prevent_initial_call=True,
    )
    def greet_by_last(last):
        return f"Hi, {last}!"

    dash_duo.start_server(app)
    tools = _mcp_tools(dash_duo.server.url)

    first_tool = _find_tool(tools, "greet_by_first")
    last_tool = _find_tool(tools, "greet_by_last")

    assert first_tool is not None, "greet_by_first should be listed"
    assert last_tool is not None, "greet_by_last should be listed"


def test_duplicate_outputs_both_callable(dash_duo):
    """Both callbacks can be called and produce correct results."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="first-name", value="Jane"),
            dcc.Input(id="last-name", value="Doe"),
            html.Div(id="greeting"),
        ]
    )

    @app.callback(
        Output("greeting", "children"),
        Input("first-name", "value"),
    )
    def greet_by_first(first):
        return f"Hello, {first}!"

    @app.callback(
        Output("greeting", "children", allow_duplicate=True),
        Input("last-name", "value"),
        prevent_initial_call=True,
    )
    def greet_by_last(last):
        return f"Hi, {last}!"

    dash_duo.start_server(app)

    result1 = _mcp_call_tool(dash_duo.server.url, "greet_by_first", {"first": "Alice"})
    assert _get_response(result1)["greeting"]["children"] == "Hello, Alice!"

    result2 = _mcp_call_tool(dash_duo.server.url, "greet_by_last", {"last": "Smith"})
    assert _get_response(result2)["greeting"]["children"] == "Hi, Smith!"


def test_duplicate_outputs_find_by_output_returns_primary(dash_duo):
    """find_by_output returns the primary (non-duplicate) callback."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="first-name", value="Jane"),
            dcc.Input(id="last-name", value="Doe"),
            html.Div(id="greeting"),
        ]
    )

    @app.callback(
        Output("greeting", "children"),
        Input("first-name", "value"),
    )
    def greet_by_first(first):
        return f"Hello, {first}!"

    @app.callback(
        Output("greeting", "children", allow_duplicate=True),
        Input("last-name", "value"),
        prevent_initial_call=True,
    )
    def greet_by_last(last):
        return f"Hi, {last}!"

    dash_duo.start_server(app)

    # Query the component — should reflect initial callback (greet_by_first)
    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "greeting", "property": "children"},
    )
    structured = result["result"]["structuredContent"]
    assert structured["properties"]["children"]["initial_value"] == "Hello, Jane!"
