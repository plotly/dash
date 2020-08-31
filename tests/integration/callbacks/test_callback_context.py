import json
import operator
import pytest
import dash_html_components as html
import dash_core_components as dcc

from dash import Dash, callback_context

from dash.dependencies import Input, Output

from dash.exceptions import PreventUpdate, MissingCallbackContextException

from selenium.webdriver.common.action_chains import ActionChains


def test_cbcx001_modified_response(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="input", value="ab"), html.Div(id="output")])

    @app.callback(Output("output", "children"), [Input("input", "value")])
    def update_output(value):
        callback_context.response.set_cookie("dash_cookie", value + " - cookie")
        return value + " - output"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "ab - output")
    input1 = dash_duo.find_element("#input")

    input1.send_keys("cd")

    dash_duo.wait_for_text_to_equal("#output", "abcd - output")
    cookie = dash_duo.driver.get_cookie("dash_cookie")
    # cookie gets json encoded
    assert cookie["value"] == '"abcd - cookie"'

    assert not dash_duo.get_logs()


def test_cbcx002_triggered(dash_duo):
    app = Dash(__name__)

    btns = ["btn-{}".format(x) for x in range(1, 6)]

    app.layout = html.Div(
        [html.Div([html.Button(btn, id=btn) for btn in btns]), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), [Input(x, "n_clicks") for x in btns])
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
    app.layout = html.Div([html.Button("click!", id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), [Input("btn", "n_clicks")])
    def report_triggered(n):
        triggered = callback_context.triggered
        bool_val = "truthy" if triggered else "falsy"
        split_propid = json.dumps(triggered[0]["prop_id"].split("."))
        full_val = json.dumps(triggered)
        return "triggered is {}, has prop/id {}, and full value {}".format(
            bool_val, split_propid, full_val
        )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#out",
        'triggered is falsy, has prop/id ["", ""], and full value '
        '[{"prop_id": ".", "value": null}]',
    )

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(
        "#out",
        'triggered is truthy, has prop/id ["btn", "n_clicks"], and full value '
        '[{"prop_id": "btn.n_clicks", "value": 1}]',
    )


@pytest.mark.DASH1350
def test_cbcx005_grouped_clicks(dash_duo):
    calls = 0
    callback_contexts = []
    clicks = dict()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Button 0", id="btn0"),
            html.Div(
                [
                    html.Button("Button 1", id="btn1"),
                    html.Div(
                        [html.Div(id="div3"), html.Button("Button 2", id="btn2")],
                        id="div2",
                        style=dict(backgroundColor="yellow", padding="50px"),
                    ),
                ],
                id="div1",
                style=dict(backgroundColor="blue", padding="50px"),
            ),
        ],
        id="div0",
        style=dict(backgroundColor="red", padding="50px"),
    )

    @app.callback(
        Output("div3", "children"),
        [
            Input("div1", "n_clicks"),
            Input("div2", "n_clicks"),
            Input("btn0", "n_clicks"),
            Input("btn1", "n_clicks"),
            Input("btn2", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update(div1, div2, btn0, btn1, btn2):
        nonlocal calls
        nonlocal callback_contexts
        nonlocal clicks

        calls = calls + 1
        callback_contexts.append(callback_context.triggered)
        clicks["div1"] = div1
        clicks["div2"] = div2
        clicks["btn0"] = btn0
        clicks["btn1"] = btn1
        clicks["btn2"] = btn2

    def click(target):
        ActionChains(dash_duo.driver).move_to_element_with_offset(
            target, 5, 5
        ).click().perform()

    dash_duo.start_server(app)
    click(dash_duo.find_element("#btn0"))
    assert calls == 1
    keys = list(map(operator.itemgetter("prop_id"), callback_contexts[-1:][0]))
    assert len(keys) == 1
    assert "btn0.n_clicks" in keys

    assert clicks.get("btn0") == 1
    assert clicks.get("btn1") is None
    assert clicks.get("btn2") is None
    assert clicks.get("div1") is None
    assert clicks.get("div2") is None

    click(dash_duo.find_element("#div1"))
    assert calls == 2
    keys = list(map(operator.itemgetter("prop_id"), callback_contexts[-1:][0]))
    assert len(keys) == 1
    assert "div1.n_clicks" in keys

    assert clicks.get("btn0") == 1
    assert clicks.get("btn1") is None
    assert clicks.get("btn2") is None
    assert clicks.get("div1") == 1
    assert clicks.get("div2") is None

    click(dash_duo.find_element("#btn1"))
    assert calls == 3
    keys = list(map(operator.itemgetter("prop_id"), callback_contexts[-1:][0]))
    assert len(keys) == 2
    assert "btn1.n_clicks" in keys
    assert "div1.n_clicks" in keys

    assert clicks.get("btn0") == 1
    assert clicks.get("btn1") == 1
    assert clicks.get("btn2") is None
    assert clicks.get("div1") == 2
    assert clicks.get("div2") is None

    click(dash_duo.find_element("#div2"))
    assert calls == 4
    keys = list(map(operator.itemgetter("prop_id"), callback_contexts[-1:][0]))
    assert len(keys) == 2
    assert "div1.n_clicks" in keys
    assert "div2.n_clicks" in keys

    assert clicks.get("btn0") == 1
    assert clicks.get("btn1") == 1
    assert clicks.get("btn2") is None
    assert clicks.get("div1") == 3
    assert clicks.get("div2") == 1

    click(dash_duo.find_element("#btn2"))
    assert calls == 5
    keys = list(map(operator.itemgetter("prop_id"), callback_contexts[-1:][0]))
    assert len(keys) == 3
    assert "btn2.n_clicks" in keys
    assert "div1.n_clicks" in keys
    assert "div2.n_clicks" in keys

    assert clicks.get("btn0") == 1
    assert clicks.get("btn1") == 1
    assert clicks.get("btn2") == 1
    assert clicks.get("div1") == 4
    assert clicks.get("div2") == 2
