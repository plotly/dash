"""Tests for CallbackAdapter."""

import pytest
from dash import Dash, Input, Output, State, dcc, html
from dash._get_app import app_context
from mcp.types import Tool

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
def multi_output_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a", "b"], value="a"),
            dcc.Dropdown(id="dd2"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("dd2", "options"),
        Output("out", "children"),
        Input("dd", "value"),
    )
    def update(val):
        return [], val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def state_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="inp"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        State("inp", "value"),
    )
    def update(clicks, val):
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def typed_app():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val: str):
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


class TestTool:
    def test_returns_tool_instance(self, simple_app):
        with simple_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        assert isinstance(tool, Tool)
        assert tool.name == "update"

    def test_description_includes_docstring(self, simple_app):
        with simple_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        assert "Update output." in tool.description

    def test_description_includes_output_target(self, simple_app):
        with simple_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        assert "out.children" in tool.description

    def test_param_name_from_function_signature(self, simple_app):
        with simple_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        assert "val" in tool.inputSchema["properties"]

    def test_param_has_label_description(self, simple_app):
        with simple_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        desc = tool.inputSchema["properties"]["val"].get("description", "")
        assert "Your Name" in desc

    def test_state_params_included(self, state_app):
        with state_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        props = tool.inputSchema["properties"]
        assert set(props.keys()) == {"clicks", "val"}

    def test_multi_output_description(self, multi_output_app):
        with multi_output_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        assert "dd2.options" in tool.description
        assert "out.children" in tool.description

    def test_typed_annotation_narrows_schema(self, typed_app):
        with typed_app.server.test_request_context():
            tool = app_context.get().mcp_callback_map[0].as_mcp_tool
        assert tool.inputSchema["properties"]["val"]["type"] == "string"


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


class TestNoInfiniteLoop:
    @pytest.mark.timeout(5)
    def test_initial_output_does_not_loop(self):
        """Building a tool must not trigger infinite re-entry in _initial_output."""
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Slider(id="sl", min=0, max=10, value=5),
                html.Div(id="out"),
            ]
        )

        @app.callback(Output("out", "children"), Input("sl", "value"))
        def show(value):
            return f"Value: {value}"

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)

        with app.server.test_request_context():
            tool = app.mcp_callback_map[0].as_mcp_tool
        assert tool.name == "show"

    @pytest.mark.timeout(5)
    def test_chained_callbacks_do_not_loop(self):
        """Chained callbacks with initial value resolution must not loop."""
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Slider(id="sl", min=0, max=10, value=5),
                dcc.Slider(id="sl2", min=0, max=10),
                html.Div(id="out"),
            ]
        )

        @app.callback(Output("sl2", "value"), Input("sl", "value"))
        def sync(v):
            return v

        @app.callback(
            Output("out", "children"),
            Input("sl", "value"),
            Input("sl2", "value"),
        )
        def show(v1, v2):
            return f"{v1} + {v2}"

        app_context.set(app)
        app.mcp_callback_map = CallbackAdapterCollection(app)

        with app.server.test_request_context():
            for cb in app.mcp_callback_map:
                tool = cb.as_mcp_tool
                assert tool.name is not None
