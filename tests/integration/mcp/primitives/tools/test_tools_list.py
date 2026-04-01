"""Integration tests for tools/list — naming, dedup, and spec compliance."""

from dash import Dash, Input, Output, dcc, html

from tests.integration.mcp.conftest import _mcp_tools


def test_tool_names_within_64_chars(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a"], value="a"),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("dd", "value"))
    def update(val):
        return val

    dash_duo.start_server(app)
    for tool in _mcp_tools(dash_duo.server.url):
        assert len(tool["name"]) <= 64, f"Tool name exceeds 64 chars: {tool['name']}"
        for param_name in tool.get("inputSchema", {}).get("properties", {}):
            assert len(param_name) <= 64, f"Param name exceeds 64 chars: {param_name}"


def test_long_callback_ids_within_64_chars(dash_duo):
    app = Dash(__name__)
    long_id = "a" * 120
    app.layout = html.Div(
        [
            dcc.Input(id=long_id, value="test"),
            html.Div(id=f"{long_id}-output"),
        ]
    )

    @app.callback(Output(f"{long_id}-output", "children"), Input(long_id, "value"))
    def process(val):
        return val

    dash_duo.start_server(app)
    for tool in _mcp_tools(dash_duo.server.url):
        assert len(tool["name"]) <= 64, f"Tool name exceeds 64 chars: {tool['name']}"


def test_pattern_matching_ids_within_64_chars(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Input(
                        id={"type": "filter-input", "index": i, "category": "primary"},
                        value=f"val-{i}",
                    )
                    for i in range(3)
                ]
            ),
            html.Div(id="pm-output"),
        ]
    )

    @app.callback(
        Output("pm-output", "children"),
        Input({"type": "filter-input", "index": 0, "category": "primary"}, "value"),
    )
    def filter_update(v0):
        return str(v0)

    dash_duo.start_server(app)
    for tool in _mcp_tools(dash_duo.server.url):
        assert len(tool["name"]) <= 64, f"Tool name exceeds 64 chars: {tool['name']}"


def test_duplicate_func_names_produce_unique_tools(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd1", options=["a"], value="a"),
            html.Div(id="dd1-output"),
            dcc.Dropdown(id="dd2", options=["b"], value="b"),
            html.Div(id="dd2-output"),
            dcc.Dropdown(id="dd3", options=["c"], value="c"),
            html.Div(id="dd3-output"),
        ]
    )

    @app.callback(Output("dd1-output", "children"), Input("dd1", "value"))
    def cb(value):
        return f"first: {value}"

    @app.callback(Output("dd2-output", "children"), Input("dd2", "value"))
    def cb(value):  # noqa: F811
        return f"second: {value}"

    @app.callback(Output("dd3-output", "children"), Input("dd3", "value"))
    def cb(value):  # noqa: F811
        return f"third: {value}"

    dash_duo.start_server(app)
    tools = _mcp_tools(dash_duo.server.url)
    cb_tools = [t for t in tools if t["name"] not in ("get_dash_component",)]
    tool_names = [t["name"] for t in cb_tools]

    assert (
        len(tool_names) == 3
    ), f"Expected 3 callback tools, got {len(tool_names)}: {tool_names}"
    assert len(set(tool_names)) == 3, f"Tool names not unique: {tool_names}"


def test_builtin_tools_always_present(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(id="root")

    dash_duo.start_server(app)
    tool_names = [t["name"] for t in _mcp_tools(dash_duo.server.url)]
    assert "get_dash_component" in tool_names
