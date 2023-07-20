import pytest
from dash import Dash, Input, Output, dcc, html


@pytest.fixture(scope="module")
def ninput_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(
                id="input_false",
                type="number",
                debounce=False,
                placeholder="debounce=False",
            ),
            html.Div(id="div_false"),
            html.Hr(id="silent-break-line"),
            dcc.Input(
                id="input_true",
                type="number",
                debounce=True,
                placeholder="debounce=True",
            ),
            html.Div(id="div_true"),
        ]
    )

    @app.callback(
        [Output("div_false", "children"), Output("div_true", "children")],
        [Input("input_false", "value"), Input("input_true", "value")],
    )
    def render(fval, tval):
        return fval, tval

    yield app


@pytest.fixture(scope="module")
def input_range_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(
                id="range",
                type="number",
                min=10,
                max=10000,
                step=3,
                placeholder="input with range",
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), [Input("range", "value")])
    def range_out(val):
        return val

    yield app


@pytest.fixture(scope="module")
def debounce_text_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(
                id="input-slow",
                debounce=3,
                placeholder="long wait",
            ),
            html.Div(id="div-slow"),
            dcc.Input(
                id="input-fast",
                debounce=0.25,
                placeholder="short wait",
            ),
            html.Div(id="div-fast"),
        ]
    )

    @app.callback(
        [Output("div-slow", "children"), Output("div-fast", "children")],
        [Input("input-slow", "value"), Input("input-fast", "value")],
    )
    def render(slow_val, fast_val):
        return [slow_val, fast_val]

    yield app


@pytest.fixture(scope="module")
def debounce_number_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(
                id="input-slow",
                debounce=3,
                type="number",
                placeholder="long wait",
            ),
            html.Div(id="div-slow"),
            dcc.Input(
                id="input-fast",
                debounce=0.25,
                type="number",
                min=10,
                max=10000,
                step=3,
                placeholder="short wait",
            ),
            html.Div(id="div-fast"),
        ]
    )

    @app.callback(
        [Output("div-slow", "children"), Output("div-fast", "children")],
        [Input("input-slow", "value"), Input("input-fast", "value")],
    )
    def render(slow_val, fast_val):
        return [slow_val, fast_val]

    yield app
