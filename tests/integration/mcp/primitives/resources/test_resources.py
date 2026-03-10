"""Integration tests for MCP resources."""

import json

from dash import Dash, dcc, html

from tests.integration.mcp.conftest import _mcp_method


def test_resources_list_includes_layout(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a"], value="a"),
            html.Div(id="out"),
        ]
    )

    dash_duo.start_server(app)
    result = _mcp_method(dash_duo.server.url, "resources/list")

    assert "result" in result
    uris = [r["uri"] for r in result["result"]["resources"]]
    assert "dash://layout" in uris


def test_read_layout_resource(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="res-dd", options=["x", "y"], value="x"),
            html.Div(id="out"),
        ]
    )

    dash_duo.start_server(app)
    result = _mcp_method(
        dash_duo.server.url,
        "resources/read",
        {"uri": "dash://layout"},
    )

    assert "result" in result
    layout = json.loads(result["result"]["contents"][0]["text"])
    assert layout["type"] == "Div"
    children = layout["props"]["children"]
    dd = next(
        c for c in children if isinstance(c, dict) and c.get("type") == "Dropdown"
    )
    assert dd["props"]["id"] == "res-dd"
    assert dd["props"]["options"] == ["x", "y"]
