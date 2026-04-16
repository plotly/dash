"""Tests for CallbackAdapter."""

import pytest
from dash import Dash, Input, Output, dcc, html
from dash._get_app import app_context

from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Your Name", htmlFor="inp"),
            dcc.Input(id="inp", type="text"),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val):
        """Update output."""
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def duplicate_names_app():
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
    def cb(v):
        return v

    @app.callback(Output("out2", "children"), Input("in2", "children"))
    def cb(v):  # noqa: F811
        return v

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFromApp:
    def test_returns_list(self, simple_app):
        assert len(app_context.get().mcp_callback_map) == 1

    def test_excludes_clientside(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Button(id="btn"),
                html.Div(id="cs-out"),
                html.Div(id="srv-out"),
            ]
        )
        app.clientside_callback(
            "function(n) { return n; }",
            Output("cs-out", "children"),
            Input("btn", "n_clicks"),
        )

        @app.callback(Output("srv-out", "children"), Input("btn", "n_clicks"))
        def server_cb(n):
            return str(n)

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)

        names = [a.tool_name for a in app.mcp_callback_map]
        assert names == ["server_cb"]

    def test_excludes_mcp_disabled(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="inp"),
                html.Div(id="out1"),
                html.Div(id="out2"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("inp", "value"))
        def visible(val):
            return val

        @app.callback(
            Output("out2", "children"), Input("inp", "value"), mcp_enabled=False
        )
        def hidden(val):
            return val

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)
        names = [a.tool_name for a in app.mcp_callback_map]
        assert "visible" in names
        assert "hidden" not in names


class TestToolName:
    def test_uses_func_name(self, simple_app):
        assert app_context.get().mcp_callback_map[0].tool_name == "update"

    def test_duplicates_get_unique_names(self, duplicate_names_app):
        names = [a.tool_name for a in app_context.get().mcp_callback_map]
        assert len(names) == 2
        assert names[0] != names[1]


class TestGetInitialValue:
    def test_returns_layout_value(self, simple_app):
        callback_map = app_context.get().mcp_callback_map
        # Input with no value set — returns None (layout default for dcc.Input)
        assert callback_map.get_initial_value("inp.value") is None

    def test_returns_set_value(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="dd", options=["a", "b"], value="a"),
                html.Div(id="out"),
            ]
        )

        @app.callback(Output("out", "children"), Input("dd", "value"))
        def update(selected):
            return selected

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)
        assert app.mcp_callback_map.get_initial_value("dd.value") == "a"

    def test_initial_callback_makes_param_required(self):
        """A param with None in layout but set by an initial callback is required."""
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(
                    id="country", options=["France", "Germany"], value="France"
                ),
                dcc.Dropdown(id="city"),  # value=None in layout
                html.Div(id="out"),
            ]
        )

        @app.callback(
            Output("city", "options"),
            Output("city", "value"),
            Input("country", "value"),
        )
        def update_cities(country):
            return [{"label": "Paris", "value": "Paris"}], "Paris"

        @app.callback(Output("out", "children"), Input("city", "value"))
        def show_city(city):
            return f"Selected: {city}"

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)

        # city.value is None in layout but "Paris" after initial callback
        with app.server.test_request_context():
            show_city_cb = app.mcp_callback_map.find_by_tool_name("show_city")
            city_param = show_city_cb.inputs[0]
            assert city_param["name"] == "city"
            assert city_param["required"] is True  # not optional despite None in layout


class TestIsValid:
    def test_valid_when_inputs_in_layout(self, simple_app):
        assert app_context.get().mcp_callback_map[0].is_valid

    def test_invalid_when_input_not_in_layout(self):
        app = Dash(__name__)
        app.layout = html.Div([html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("nonexistent", "value"))
        def update(val):
            return val

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)
        assert not app.mcp_callback_map[0].is_valid

    def test_pattern_matching_ids_always_valid(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id={"type": "field", "index": 0}, value="a"),
                html.Div(id="out"),
            ]
        )

        @app.callback(
            Output("out", "children"),
            Input({"type": "field", "index": 0}, "value"),
        )
        def update(val):
            return val

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)
        assert app.mcp_callback_map[0].is_valid
