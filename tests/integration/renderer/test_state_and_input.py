from multiprocessing import Value
import time
from dash import Dash, Input, Output, State, html, dcc
import dash.testing.wait as wait


def test_rdsi001_state_and_inputs(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(value="Initial Input", id="input"),
            dcc.Input(value="Initial State", id="state"),
            html.Div(id="output"),
        ]
    )

    call_count = Value("i", 0)

    @app.callback(
        Output("output", "children"),
        [Input("input", "value")],
        [State("state", "value")],
    )
    def update_output(input, state):
        call_count.value += 1
        return 'input="{}", state="{}"'.format(input, state)

    dash_duo.start_server(app)

    def input_():
        return dash_duo.find_element("#input")

    def output_():
        return dash_duo.find_element("#output")

    assert (
        output_().text == 'input="Initial Input", state="Initial State"'
    ), "callback gets called with initial input"

    input_().send_keys("x")
    wait.until(lambda: call_count.value == 2, timeout=1)
    assert (
        output_().text == 'input="Initial Inputx", state="Initial State"'
    ), "output get updated with key `x`"

    dash_duo.find_element("#state").send_keys("z")
    time.sleep(0.5)
    assert call_count.value == 2, "state not trigger callback with 0.5 wait"
    assert (
        output_().text == 'input="Initial Inputx", state="Initial State"'
    ), "output remains the same as last step"

    input_().send_keys("y")
    wait.until(lambda: call_count.value == 3, timeout=1)
    assert (
        output_().text == 'input="Initial Inputxy", state="Initial Statez"'
    ), "both input and state value get updated by input callback"


def test_rdsi002_event_properties_state_and_inputs(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Click Me", id="button"),
            dcc.Input(value="Initial Input", id="input"),
            dcc.Input(value="Initial State", id="state"),
            html.Div(id="output"),
        ]
    )

    call_count = Value("i", 0)

    @app.callback(
        Output("output", "children"),
        [Input("input", "value"), Input("button", "n_clicks")],
        [State("state", "value")],
    )
    def update_output(input, n_clicks, state):
        call_count.value += 1
        return 'input="{}", state="{}"'.format(input, state)

    dash_duo.start_server(app)

    def btn():
        return dash_duo.find_element("#button")

    def output():
        return dash_duo.find_element("#output")

    assert (
        output().text == 'input="Initial Input", state="Initial State"'
    ), "callback gets called with initial input"

    btn().click()
    wait.until(lambda: call_count.value == 2, timeout=1)
    assert (
        output().text == 'input="Initial Input", state="Initial State"'
    ), "button click doesn't count on output"

    dash_duo.find_element("#input").send_keys("x")
    wait.until(lambda: call_count.value == 3, timeout=1)

    assert (
        output().text == 'input="Initial Inputx", state="Initial State"'
    ), "output get updated with key `x`"

    dash_duo.find_element("#state").send_keys("z")
    time.sleep(0.5)
    assert call_count.value == 3, "state not trigger callback with 0.5 wait"
    assert (
        output().text == 'input="Initial Inputx", state="Initial State"'
    ), "output remains the same as last step"

    btn().click()
    wait.until(lambda: call_count.value == 4, timeout=1)
    assert output().text == 'input="Initial Inputx", state="Initial Statez"'
