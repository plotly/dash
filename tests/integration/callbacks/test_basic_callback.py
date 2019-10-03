from multiprocessing import Value

from bs4 import BeautifulSoup

import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output


def test_cbsc001_simple_callback(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(html.Div([1.5, None, "string", html.Div(id="output-1")])),
        ]
    )
    call_count = Value("i", 0)

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        call_count.value = call_count.value + 1
        return value

    dash_duo.start_server(app)

    assert dash_duo.find_element("#output-1").text == "initial value"
    dash_duo.percy_snapshot(name="simple-callback-initial")

    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)

    input_.send_keys("hello world")

    assert dash_duo.find_element("#output-1").text == "hello world"
    dash_duo.percy_snapshot(name="simple-callback-hello-world")

    assert call_count.value == 2 + len(
        "hello world"
    ), "initial count + each key stroke"

    rqs = dash_duo.redux_state_rqs
    assert len(rqs) == 1

    assert dash_duo.get_logs() == []


def test_cbsc002_callbacks_generating_children(dash_duo):
    """Modify the DOM tree by adding new components in the callbacks."""

    # some components don't exist in the initial render
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [dcc.Input(id="input", value="initial value"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), [Input("input", "value")])
    def pad_output(input):
        return html.Div(
            [
                dcc.Input(id="sub-input-1", value="sub input initial value"),
                html.Div(id="sub-output-1"),
            ]
        )

    call_count = Value("i", 0)

    @app.callback(
        Output("sub-output-1", "children"), [Input("sub-input-1", "value")]
    )
    def update_input(value):
        call_count.value = call_count.value + 1
        return value

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#sub-output-1", "sub input initial value")

    assert call_count.value == 1, "called once at initial stage"

    pad_input, pad_div = dash_duo.dash_innerhtml_dom.select_one(
        "#output > div"
    ).contents

    assert (
        pad_input.attrs["value"] == "sub input initial value"
        and pad_input.attrs["id"] == "sub-input-1"
    )
    assert pad_input.name == "input"

    assert (
        pad_div.text == pad_input.attrs["value"]
        and pad_div.get("id") == "sub-output-1"
    ), "the sub-output-1 content reflects to sub-input-1 value"

    dash_duo.percy_snapshot(name="callback-generating-function-1")

    assert dash_duo.redux_state_paths == {
        "input": ["props", "children", 0],
        "output": ["props", "children", 1],
        "sub-input-1": [
            "props",
            "children",
            1,
            "props",
            "children",
            "props",
            "children",
            0,
        ],
        "sub-output-1": [
            "props",
            "children",
            1,
            "props",
            "children",
            "props",
            "children",
            1,
        ],
    }, "the paths should include these new output IDs"

    # editing the input should modify the sub output
    dash_duo.find_element("#sub-input-1").send_keys("deadbeef")

    assert (
        dash_duo.find_element("#sub-output-1").text
        == pad_input.attrs["value"] + "deadbeef"
    ), "deadbeef is added"

    # the total updates is initial one + the text input changes
    dash_duo.wait_for_text_to_equal(
        "#sub-output-1", pad_input.attrs["value"] + "deadbeef"
    )

    rqs = dash_duo.redux_state_rqs
    assert rqs, "request queue is not empty"
    assert all((rq["status"] == 200 and not rq["rejected"] for rq in rqs))

    dash_duo.percy_snapshot(name="callback-generating-function-2")
    assert dash_duo.get_logs() == [], "console is clean"
