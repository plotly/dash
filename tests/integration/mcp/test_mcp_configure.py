"""Integration tests for configure_mcp()."""

from dash import Dash, Input, Output, dcc, html
from dash.mcp import configure_mcp_server, mcp_enabled

from tests.integration.mcp.conftest import _mcp_method, _mcp_tools


def test_mcpcfg001_disable_everything_decorated_function_still_appears(dash_duo):
    """configure_mcp with all content disabled: layout/callback/page resources and
    tools are absent, but an @mcp_enabled decorated function still appears."""

    @mcp_enabled
    def my_tool(x: int) -> int:
        return x * 2

    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val):
        return val

    configure_mcp_server(
        include_layout=False,
        include_callbacks=False,
        include_clientside_callbacks=False,
        include_pages=False,
    )
    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    tool_names = [t["name"] for t in tools]
    assert "update" not in tool_names
    assert "get_dash_component" not in tool_names
    assert tool_names == ["my_tool"]

    resources = _mcp_method(dash_duo.server.url, "resources/list")
    uris = [r["uri"] for r in resources["result"]["resources"]]
    assert "dash://layout" not in uris
    assert "dash://components" not in uris
    assert "dash://clientside-callbacks" not in uris


def test_mcpcfg002_disable_layout_callbacks_still_appear(dash_duo):
    """configure_mcp(include_layout=False): callback tools are present,
    get_dash_component is absent, layout resources are absent."""
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val):
        return val

    configure_mcp_server(include_layout=False)
    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    tool_names = [t["name"] for t in tools]
    assert "update" in tool_names
    assert "get_dash_component" not in tool_names

    resources = _mcp_method(dash_duo.server.url, "resources/list")
    uris = [r["uri"] for r in resources["result"]["resources"]]
    assert "dash://layout" not in uris
    assert "dash://components" not in uris


def test_mcpcfg003_disable_callbacks_single_opt_in_layout_queryable(dash_duo):
    """configure_mcp(include_callbacks=False) with one explicit mcp_enabled=True
    callback: only that callback appears as a tool, layout is queryable."""
    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Input(id="inp"), html.Div(id="out"), html.Div(id="out2")]
    )

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def excluded(val):
        return val

    @app.callback(Output("out2", "children"), Input("inp", "value"), mcp_enabled=True)
    def included(val):
        return val

    configure_mcp_server(include_callbacks=False)
    dash_duo.start_server(app)

    tools = _mcp_tools(dash_duo.server.url)
    tool_names = [t["name"] for t in tools]
    assert "included" in tool_names
    assert "excluded" not in tool_names

    resources = _mcp_method(dash_duo.server.url, "resources/list")
    uris = [r["uri"] for r in resources["result"]["resources"]]
    assert "dash://layout" in uris
