"""Tests for CallbackAdapterCollection."""

from dash import Dash, Input, Output, dcc, html
from dash._get_app import app_context

from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)


def _setup(app):
    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)


class TestToolNameCollisions:
    @staticmethod
    def _make_duplicate_cb_app(n=3):
        ids = [f"dd{i + 1}" for i in range(n)]
        app = Dash(__name__)
        app.layout = html.Div(
            [
                item
                for i in ids
                for item in [
                    dcc.Dropdown(
                        id=i, options=[chr(97 + j) for j in range(1)], value="a"
                    ),
                    html.Div(id=f"{i}-output"),
                ]
            ]
        )
        for idx, dd_id in enumerate(ids):

            @app.callback(Output(f"{dd_id}-output", "children"), Input(dd_id, "value"))
            def cb(value, _id=dd_id):  # noqa: F811
                return f"{_id}: {value}"

        return app

    def test_duplicate_func_names_get_unique_tools(self):
        app = self._make_duplicate_cb_app(3)
        _setup(app)
        tool_names = [a.tool_name for a in app.mcp_callback_map]
        assert len(tool_names) == 3
        assert len(set(tool_names)) == 3, f"Tool names are not unique: {tool_names}"
        for name in tool_names:
            assert "dd" in name, f"Expected output ID in tool name: {name}"

    def test_unique_func_names_use_func_name(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="in1"),
                html.Div(id="out1"),
                html.Div(id="in2"),
                html.Div(id="out2"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("in1", "children"))
        def alpha_handler(value):
            return value

        @app.callback(Output("out2", "children"), Input("in2", "children"))
        def beta_handler(value):
            return value

        _setup(app)
        tool_names = [a.tool_name for a in app.mcp_callback_map]
        assert "alpha_handler" in tool_names
        assert "beta_handler" in tool_names

    def test_duplicate_func_names_use_output_id(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="out1"),
                html.Div(id="out2"),
                html.Div(id="out3"),
                html.Div(id="in1"),
                html.Div(id="in2"),
                html.Div(id="in3"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("in1", "children"))
        def unique_func(v):
            return v

        @app.callback(Output("out2", "children"), Input("in2", "children"))
        def cb(v):
            return v

        @app.callback(Output("out3", "children"), Input("in3", "children"))
        def cb(v):  # noqa: F811
            return v

        _setup(app)
        tool_names = [a.tool_name for a in app.mcp_callback_map]
        assert "unique_func" in tool_names
        non_unique = [n for n in tool_names if n != "unique_func"]
        assert len(non_unique) == 2
        assert non_unique[0] != non_unique[1]


class TestAllCallbacksVisibleByDefault:
    def test_all_callbacks_visible_by_default(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="in1"),
                html.Div(id="out1"),
                html.Div(id="in2"),
                html.Div(id="out2"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("in1", "children"))
        def cb_one(value):
            return value

        @app.callback(Output("out2", "children"), Input("in2", "children"))
        def cb_two(value):
            return value

        _setup(app)
        tool_names = [a.tool_name for a in app.mcp_callback_map]
        assert "cb_one" in tool_names
        assert "cb_two" in tool_names


class TestAdapterCollection:
    def test_adapter_has_expected_properties(self):
        app = Dash(__name__)
        app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("inp", "value"))
        def update(val):
            return val

        _setup(app)
        adapter = app.mcp_callback_map[0]
        assert adapter.tool_name == "update"
        assert adapter.output_id == "out.children"
