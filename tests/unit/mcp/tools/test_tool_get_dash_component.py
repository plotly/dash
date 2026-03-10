"""Tests for the get_dash_component built-in tool."""

from dash import Dash, Input, Output, dcc, html

from tests.unit.mcp.conftest import _call_tool, _make_app, _tools_list


class TestGetDashComponent:
    def test_present_in_tools_list(self):
        app = _make_app()
        tool_names = [t["name"] for t in _tools_list(app)]
        assert "get_dash_component" in tool_names

    def test_returns_structured_output_with_prop(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="my-dd", options=["a", "b"], value="b"),
            ]
        )

        result = _call_tool(
            app,
            "get_dash_component",
            {
                "component_id": "my-dd",
                "property": "value",
            },
        )
        sc = result["result"]["structuredContent"]
        assert sc["component_id"] == "my-dd"
        assert sc["component_type"] == "Dropdown"
        assert "value" in sc["properties"]
        assert sc["properties"]["value"]["initial_value"] == "b"
        assert "options" not in sc["properties"]

    def test_returns_all_props_without_property(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="my-dd", options=["a", "b"], value="b"),
            ]
        )

        result = _call_tool(
            app,
            "get_dash_component",
            {
                "component_id": "my-dd",
            },
        )
        sc = result["result"]["structuredContent"]
        assert "options" in sc["properties"]
        assert "value" in sc["properties"]
        assert sc["properties"]["value"]["initial_value"] == "b"

    def test_includes_label(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Label("Pick one", htmlFor="my-dd"),
                dcc.Dropdown(id="my-dd", options=["a", "b"], value="a"),
            ]
        )

        @app.callback(Output("my-dd", "value"), Input("my-dd", "options"))
        def noop(o):
            return "a"

        result = _call_tool(
            app,
            "get_dash_component",
            {
                "component_id": "my-dd",
            },
        )
        sc = result["result"]["structuredContent"]
        assert sc["label"] == ["Pick one"]

    def test_includes_tool_references(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="dd", options=["a", "b"], value="a"),
                html.Div(id="out"),
            ]
        )

        @app.callback(Output("out", "children"), Input("dd", "value"))
        def update(val):
            return val

        result = _call_tool(
            app,
            "get_dash_component",
            {
                "component_id": "dd",
                "property": "value",
            },
        )
        prop_info = result["result"]["structuredContent"]["properties"]["value"]
        assert "update" in prop_info["input_to_tool"]

    def test_missing_id_returns_hint(self):
        app = _make_app()
        result = _call_tool(
            app,
            "get_dash_component",
            {
                "component_id": "nonexistent",
                "property": "value",
            },
        )
        text = result["result"]["content"][0]["text"]
        assert "nonexistent" in text
        assert "not found" in text
        assert "dash://components" in text
