"""Tests for pattern-matching schema and description generation."""

from dash import Dash, html, Input, Output, ALL, MATCH

from tests.unit.mcp.conftest import _tools_list, _user_tool, _schema_for, _desc_for


class TestPatternMatchingSchema:
    def test_all_produces_array_schema(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id={"type": "item", "index": 0}, children="A"),
                html.Div(id={"type": "item", "index": 1}, children="B"),
                html.Div(id="result"),
            ]
        )

        @app.callback(
            Output("result", "children"),
            Input({"type": "item", "index": ALL}, "children"),
        )
        def combine(values):
            return ", ".join(values)

        tool = _user_tool(_tools_list(app))
        schema = _schema_for(tool)
        assert schema["type"] == "array"
        assert schema["items"]["type"] == "object"
        assert "value" in schema["items"]["properties"]

    def test_match_produces_object_schema(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id={"type": "item", "index": 0}, children="A"),
                html.Div(id="result"),
            ]
        )

        @app.callback(
            Output("result", "children"),
            Input({"type": "item", "index": MATCH}, "children"),
        )
        def echo(value):
            return value

        tool = _user_tool(_tools_list(app))
        schema = _schema_for(tool)
        assert schema["type"] == "object"
        assert "value" in schema["properties"]

    def test_annotation_narrows_value_schema(self):
        from dash import dcc

        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id={"type": "filter", "index": 0}, options=["a", "b"]),
                dcc.Dropdown(id={"type": "filter", "index": 1}, options=["c", "d"]),
                html.Div(id="result"),
            ]
        )

        @app.callback(
            Output("result", "children"),
            Input({"type": "filter", "index": ALL}, "options"),
        )
        def combine(options: list[str]):
            return str(options)

        tool = _user_tool(_tools_list(app))
        schema = _schema_for(tool)
        assert schema["type"] == "array"
        value_schema = schema["items"]["properties"]["value"]
        # Annotation narrows value to list[str] instead of the broad introspected type
        assert value_schema == {"items": {"type": "string"}, "type": "array"}


class TestPatternMatchingDescription:
    def test_all_description(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id={"type": "item", "index": 0}),
                html.Div(id="result"),
            ]
        )

        @app.callback(
            Output("result", "children"),
            Input({"type": "item", "index": ALL}, "children"),
        )
        def combine(values):
            return str(values)

        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool)
        assert "Pattern-matching input (ALL)" in desc
        assert 'type="item"' in desc

    def test_match_description(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id={"type": "item", "index": 0}),
                html.Div(id="result"),
            ]
        )

        @app.callback(
            Output("result", "children"),
            Input({"type": "item", "index": MATCH}, "children"),
        )
        def echo(value):
            return value

        tool = _user_tool(_tools_list(app))
        desc = _desc_for(tool)
        assert "Pattern-matching input (MATCH)" in desc
        assert 'type="item"' in desc
