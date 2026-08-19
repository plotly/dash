"""CallbackAdapter behavior: initial value resolution, validation, loop prevention."""

import pytest
from dash import Dash, Input, Output, dcc, html
from dash._get_app import app_context

from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)


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


def test_mcpc001_returns_layout_value(simple_app):
    callback_map = app_context.get().mcp_callback_map
    # Input with no value set — returns None (layout default for dcc.Input)
    assert callback_map.get_initial_value("inp.value") is None


def test_mcpc002_returns_set_value():
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


def test_mcpc003_initial_callback_makes_param_required():
    """A param with None in layout but set by an initial callback is required."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="country", options=["France", "Germany"], value="France"),
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


def test_mcpc004_valid_when_inputs_in_layout(simple_app):
    assert app_context.get().mcp_callback_map[0].is_valid


def test_mcpc005_invalid_when_input_not_in_layout():
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("nonexistent", "value"))
    def update(val):
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    assert not app.mcp_callback_map[0].is_valid


def test_mcpc006_pattern_matching_ids_always_valid():
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


@pytest.mark.timeout(5)
def test_mcpc007_initial_output_does_not_loop():
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
def test_mcpc008_chained_callbacks_do_not_loop():
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
