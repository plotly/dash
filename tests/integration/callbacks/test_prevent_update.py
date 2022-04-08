from multiprocessing import Value

from copy import copy
from selenium.webdriver.common.keys import Keys

from dash import Dash, no_update, Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate

from dash.testing.wait import until


def test_cbpu001_aborted_callback(dash_duo):
    """Raising PreventUpdate OR returning no_update prevents update and
    triggering dependencies."""

    initial_input = "initial input"
    initial_output = "initial output"

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value=initial_input),
            html.Div(initial_output, id="output1"),
            html.Div(initial_output, id="output2"),
        ]
    )

    callback1_count = Value("i", 0)
    callback2_count = Value("i", 0)

    @app.callback(Output("output1", "children"), [Input("input", "value")])
    def callback1(value):
        callback1_count.value += 1
        if callback1_count.value > 2:
            return no_update
        raise PreventUpdate("testing callback does not update")
        return value

    @app.callback(Output("output2", "children"), [Input("output1", "children")])
    def callback2(value):
        callback2_count.value += 1
        return value

    dash_duo.start_server(app)

    input_ = dash_duo.find_element("#input")
    for i, key in enumerate("xyz"):
        input_.send_keys(key)
        until(
            lambda: callback1_count.value == i + 2,
            timeout=3,
            msg="callback1 runs 4x (initial page load and 3x through send_keys)",
        )

    dash_duo.wait_for_text_to_equal("#input", "initial inputxyz")

    assert (
        callback2_count.value == 0
    ), "callback2 is never triggered, even on initial load"

    # double check that output1 and output2 children were not updated
    assert dash_duo.find_element("#output1").text == initial_output
    assert dash_duo.find_element("#output2").text == initial_output

    assert not dash_duo.get_logs()

    dash_duo.percy_snapshot(name="aborted")


def test_cbpu002_multi_output_no_update(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("B", "btn"),
            html.P("initial1", "n1"),
            html.P("initial2", "n2"),
            html.P("initial3", "n3"),
        ]
    )

    @app.callback(
        [Output("n1", "children"), Output("n2", "children"), Output("n3", "children")],
        [Input("btn", "n_clicks")],
    )
    def show_clicks(n):
        # partial or complete cancellation of updates via no_update
        return [
            no_update if n and n > 4 else n,
            no_update if n and n > 2 else n,
            # make a new instance, to mock up caching and restoring no_update
            copy(no_update),
        ]

    dash_duo.start_server(app)

    dash_duo.multiple_click("#btn", 10, 0.2)

    dash_duo.wait_for_text_to_equal("#n1", "4")
    dash_duo.wait_for_text_to_equal("#n2", "2")
    dash_duo.wait_for_text_to_equal("#n3", "initial3")


def test_cbpu003_no_update_chains(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="a_in", value="a"),
            dcc.Input(id="b_in", value="b"),
            html.P("", id="a_out"),
            html.P("", id="a_out_short"),
            html.P("", id="b_out"),
            html.P("", id="ab_out"),
        ]
    )

    @app.callback(
        [Output("a_out", "children"), Output("a_out_short", "children")],
        [Input("a_in", "value")],
    )
    def a_out(a):
        return a, a if len(a) < 3 else no_update

    @app.callback(Output("b_out", "children"), [Input("b_in", "value")])
    def b_out(b):
        return b

    @app.callback(
        Output("ab_out", "children"),
        [Input("a_out_short", "children")],
        [State("b_out", "children")],
    )
    def ab_out(a, b):
        return a + " " + b

    dash_duo.start_server(app)

    a_in = dash_duo.find_element("#a_in")
    b_in = dash_duo.find_element("#b_in")

    b_in.send_keys("b")
    a_in.send_keys("a")
    dash_duo.wait_for_text_to_equal("#a_out", "aa")
    dash_duo.wait_for_text_to_equal("#b_out", "bb")
    dash_duo.wait_for_text_to_equal("#a_out_short", "aa")
    dash_duo.wait_for_text_to_equal("#ab_out", "aa bb")

    b_in.send_keys("b")
    a_in.send_keys("a")
    dash_duo.wait_for_text_to_equal("#a_out", "aaa")
    dash_duo.wait_for_text_to_equal("#b_out", "bbb")
    dash_duo.wait_for_text_to_equal("#a_out_short", "aa")
    # ab_out has not been triggered because a_out_short received no_update
    dash_duo.wait_for_text_to_equal("#ab_out", "aa bb")

    b_in.send_keys("b")
    a_in.send_keys(Keys.END)
    a_in.send_keys(Keys.BACKSPACE)
    dash_duo.wait_for_text_to_equal("#a_out", "aa")
    dash_duo.wait_for_text_to_equal("#b_out", "bbbb")
    dash_duo.wait_for_text_to_equal("#a_out_short", "aa")
    # now ab_out *is* triggered - a_out_short got a new value
    # even though that value is the same as the last value it got
    dash_duo.wait_for_text_to_equal("#ab_out", "aa bbbb")
