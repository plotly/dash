import time
from multiprocessing import Value
from dash import Dash, Input, Output, State, dcc, html

import dash.testing.wait as wait


def test_state_and_inputs(dash_dcc):
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
        inputs=[Input("input", "value")],
        state=[State("state", "value")],
    )
    def update_output(input, state):
        call_count.value += 1
        return f'input="{input}", state="{state}"'

    dash_dcc.start_server(app)

    input_ = dash_dcc.find_element("#input")

    # callback gets called with initial input
    wait.until(lambda: call_count.value == 1, timeout=1)

    assert dash_dcc.wait_for_text_to_equal(
        "#output", 'input="Initial Input", state="Initial State"'
    )

    input_.send_keys("x")
    wait.until(lambda: call_count.value == 2, timeout=1)
    assert dash_dcc.wait_for_text_to_equal(
        "#output", 'input="Initial Inputx", state="Initial State"'
    )

    dash_dcc.find_element("#state").send_keys("x")
    time.sleep(0.2)

    assert call_count.value == 2
    assert dash_dcc.wait_for_text_to_equal(
        "#output", 'input="Initial Inputx", state="Initial State"'
    ), "state value sshould not trigger callback"

    input_.send_keys("y")

    wait.until(lambda: call_count.value == 3, timeout=1)
    assert dash_dcc.wait_for_text_to_equal(
        "#output", 'input="Initial Inputxy", state="Initial Statex"'
    ), "input value triggers callback, and the last state change is kept"

    assert dash_dcc.get_logs() == []
