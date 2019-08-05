import pytest
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


@pytest.fixture(scope="module")
def ninput_app():
    app = dash.Dash(__name__)
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
    app = dash.Dash(__name__)
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
