import itertools
import time
import flask
import pytest

from dash import Dash, html, dcc, Input, Output

DELAY_TIME = 0.2

routes = [
    "layout",
    "dependencies",
    "update-component",
    "_config"
    # routes and component-suites
    # are other endpoints but are excluded to speed up tests
]

permuted_strs = [
    ",".join(endpoints) for endpoints in itertools.permutations(routes, len(routes))
]


@pytest.mark.parametrize("permuted_str", permuted_strs)
def test_rdrc001_race_conditions(dash_duo, permuted_str):
    endpoints = permuted_str.split(",")
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div("Hello world", id="output"),
            dcc.Input(id="input", value="initial value"),
        ]
    )

    @app.callback(Output("output", "children"), Input("input", "value"))
    def update(value):
        return value

    def delay():
        for i, route in enumerate(endpoints):
            if route in flask.request.path:
                time.sleep((DELAY_TIME * i) + DELAY_TIME)

    app.server.before_request(delay)
    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#output", "initial value", timeout=DELAY_TIME * (len(endpoints) + 3) + 3
    )

    assert not dash_duo.get_logs()
