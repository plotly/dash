from multiprocessing import Value
import time

from dash import Dash, Input, Output, html


def test_click_simple(dash_duo):
    call_count = Value("i", 0)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="container"),
            html.Button("Click", id="button", n_clicks=0),
            html.Iframe(id="video", allow="fullscreen", referrerPolicy="origin"),
        ]
    )

    @app.callback(
        Output("container", "children"),
        Input("button", "n_clicks"),
        # The new percy runner loads the page, so to get consistent behavior for
        # call_count we need to skip the initial call
        prevent_initial_call=True,
    )
    def update_output(n_clicks):
        call_count.value += 1
        return "clicked {} times".format(n_clicks)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#container", "")

    assert call_count.value == 0

    dash_duo.find_element("#button").click()

    dash_duo.wait_for_text_to_equal("#container", "clicked 1 times")
    assert call_count.value == 1
    dash_duo.percy_snapshot("html button click")

    assert not dash_duo.get_logs()

    assert dash_duo.find_element("#video").get_attribute("allow") == "fullscreen"
    assert dash_duo.find_element("#video").get_attribute("referrerpolicy") == "origin"


def test_click_prev(dash_duo):
    call_count = Value("i", 0)
    timestamp_1 = Value("d", -5)
    timestamp_2 = Value("d", -5)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div("Initial", id="container"),
            html.Button("Click", id="button-1", n_clicks=0, n_clicks_timestamp=-1),
            html.Button("Click", id="button-2", n_clicks=0, n_clicks_timestamp=-1),
        ]
    )

    @app.callback(
        Output("container", "children"),
        [
            Input("button-1", "n_clicks"),
            Input("button-1", "n_clicks_timestamp"),
            Input("button-2", "n_clicks"),
            Input("button-2", "n_clicks_timestamp"),
        ],
        prevent_initial_call=True,
    )
    def update_output(*args):
        print(args)
        call_count.value += 1
        timestamp_1.value = args[1]
        timestamp_2.value = args[3]
        return "{}, {}".format(args[0], args[2])

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#container", "Initial")
    assert timestamp_1.value == -5
    assert timestamp_2.value == -5
    assert call_count.value == 0

    dash_duo.find_element("#button-1").click()
    dash_duo.wait_for_text_to_equal("#container", "1, 0")
    assert timestamp_1.value > ((time.time() - (24 * 60 * 60)) * 1000)
    assert timestamp_2.value == -1
    assert call_count.value == 1
    prev_timestamp_1 = timestamp_1.value

    dash_duo.find_element("#button-2").click()
    dash_duo.wait_for_text_to_equal("#container", "1, 1")
    assert timestamp_1.value == prev_timestamp_1
    assert timestamp_2.value > ((time.time() - 24 * 60 * 60) * 1000)
    assert call_count.value == 2
    prev_timestamp_2 = timestamp_2.value

    dash_duo.find_element("#button-2").click()
    dash_duo.wait_for_text_to_equal("#container", "1, 2")
    assert timestamp_1.value == prev_timestamp_1
    assert timestamp_2.value > prev_timestamp_2
    assert timestamp_2.value > timestamp_1.value
    assert call_count.value == 3

    assert not dash_duo.get_logs()

    def test_click_static(dash_duo):
        app = Dash(__name__)

        app.layout = html.Div(
            [
                html.Div("no event listener", className="div-1"),
                html.Div("event listener", id="div-2", n_clicks=0),
                html.Div(
                    "no event listener", id="div-3", n_clicks=0, disable_n_clicks=True
                ),
                html.Div(
                    "event listener", id="div-4", n_clicks=0, disable_n_clicks=False
                ),
                html.Div(id="div-output"),
            ]
        )

        @app.callback(
            Output("div-output", "children"),
            Input("div-2", "n_clicks"),
            Input("div-3", "n_clicks"),
            Input("div-4", "n_clicks"),
            prevent_initial_call=True,
        )
        def update(n2, n3, n4):
            return f"{n2}, {n3}, {n4}"

        dash_duo.start_server(app)
        dash_duo.find_element("#div-2").click()
        dash_duo.find_element("#div-3").click()
        dash_duo.find_element("#div-4").click()

        dash_duo.wait_for_text_to_equal("#div-output", "1, 0, 1")

        assert not dash_duo.get_logs()
