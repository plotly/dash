import pytest
import dash_html_components as html
import dash_core_components as dcc

from dash import Dash, callback_context

from dash.dependencies import Input, Output

from dash.exceptions import PreventUpdate, MissingCallbackContextException


def test_cbcx001_modified_response(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Input(id="input", value="ab"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), [Input("input", "value")])
    def update_output(value):
        callback_context.response.set_cookie(
            "dash cookie", value + " - cookie"
        )
        return value + " - output"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "ab - output")
    input1 = dash_duo.find_element("#input")

    input1.send_keys("cd")

    dash_duo.wait_for_text_to_equal("#output", "abcd - output")
    cookie = dash_duo.driver.get_cookie("dash cookie")
    # cookie gets json encoded
    assert cookie["value"] == '"abcd - cookie"'

    assert not dash_duo.get_logs()


def test_cbcx002_triggered(dash_duo):
    app = Dash(__name__)

    btns = ["btn-{}".format(x) for x in range(1, 6)]

    app.layout = html.Div(
        [
            html.Div([html.Button(btn, id=btn) for btn in btns]),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"), [Input(x, "n_clicks") for x in btns]
    )
    def on_click(*args):
        if not callback_context.triggered:
            raise PreventUpdate
        trigger = callback_context.triggered[0]
        return "Just clicked {} for the {} time!".format(
            trigger["prop_id"].split(".")[0], trigger["value"]
        )

    dash_duo.start_server(app)

    for i in range(1, 5):
        for btn in btns:
            dash_duo.find_element("#" + btn).click()
            dash_duo.wait_for_text_to_equal(
                "#output", "Just clicked {} for the {} time!".format(btn, i)
            )


def test_cbcx003_no_callback_context():
    for attr in ["inputs", "states", "triggered", "response"]:
        with pytest.raises(MissingCallbackContextException):
            getattr(callback_context, attr)


def test_cbcx004_triggered_backward_compat(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([
        html.Button("click!", id="btn"),
        html.Div(id="out")
    ])

    @app.callback(Output("out", "children"), [Input("btn", "n_clicks")])
    def report_triggered(n):
        triggered = callback_context.triggered
        bool_val = "truthy" if triggered else "falsy"
        split_propid = repr(triggered[0]["prop_id"].split("."))
        full_val = repr(triggered)
        return "triggered is {}, has prop/id {}, and full value {}".format(
            bool_val, split_propid, full_val
        )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#out",
        "triggered is falsy, has prop/id ['', ''], and full value "
        "[{'prop_id': '.', 'value': None}]"
    )

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(
        "#out",
        "triggered is truthy, has prop/id ['btn', 'n_clicks'], and full value "
        "[{'prop_id': 'btn.n_clicks', 'value': 1}]"
    )
