import time
from dash import Dash, dcc, html, Input, Output, State


# Tests for props that are not in dcc.Interval


def test_time001_countdown(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Timer(id="timer", interval=1, duration=2, mode="countdown"),
            dcc.Timer(
                id="timer_msg",
                interval=1,
                duration=2,
                mode="countdown",
                messages={0: "done"},
            ),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#timer", "0ms")
    dash_dcc.wait_for_text_to_equal("#timer_msg", "done")
    assert dash_dcc.get_logs() == []


def test_time002_stopwatch(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Timer(id="timer", interval=1, duration=2, mode="stopwatch"),
            dcc.Timer(
                id="timer_msg",
                interval=1,
                duration=2,
                mode="stopwatch",
                messages={2: "done"},
            ),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#timer", "2ms")
    dash_dcc.wait_for_text_to_equal("#timer_msg", "done")
    assert dash_dcc.get_logs() == []


def test_time003_timer_format(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Timer(
                id="timer1",
                duration=1000 * 10000,
                mode="countdown",
                disabled=True,
                timer_format="default",
            ),
            dcc.Timer(
                id="timer2",
                duration=1000 * 10000,
                mode="countdown",
                disabled=True,
                timer_format="compact",
            ),
            dcc.Timer(
                id="timer3",
                duration=1000 * 10000,
                mode="countdown",
                disabled=True,
                timer_format="verbose",
            ),
            dcc.Timer(
                id="timer4",
                duration=1000 * 10000,
                mode="countdown",
                disabled=True,
                timer_format="colons",
            ),
            dcc.Timer(
                id="timer5",
                duration=1800,
                interval=100,
                mode="countdown",
                disabled=True,
                timer_format="sub_ms",
            ),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#timer1", "2h 46m 40s")
    dash_dcc.wait_for_text_to_equal("#timer2", "2h")
    dash_dcc.wait_for_text_to_equal("#timer3", "2 hours 46 minutes 40 seconds")
    dash_dcc.wait_for_text_to_equal("#timer4", "2:46:40")
    dash_dcc.wait_for_text_to_equal("#timer5", "1s 800ms")
    assert dash_dcc.get_logs() == []


def test_time004_at_fire_time(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="output"),
            dcc.Timer(id="timer", interval=1, max_intervals=3, fire_times=[2]),
        ]
    )

    @app.callback(Output("output", "children"), Input("timer", "at_fire_time"))
    def update_text(n):
        return f"{n}"

    dash_dcc.start_server(app)

    time.sleep(2)

    dash_dcc.wait_for_text_to_equal("#output", "2")
    assert dash_dcc.get_logs() == []


def test_time005_rerun(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="output", children="0"),
            dcc.Timer(
                id="timer",
                interval=1000,
                duration=3000,
                rerun=True,
            ),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("timer", "n_intervals"),
        State("output", "children"),
    )
    def update_text(n, counter):
        print(counter)
        print(int(counter) + 1)
        return f"{int(counter) + 1}"

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#output", "4")
    assert dash_dcc.get_logs() == []


def test_time006_interval_errors(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            "Times not a multiple of interval - no timer started",
            dcc.Timer(id="timer", duration=2),
            dcc.Timer(id="timer2", messages={1: "done"}),
            dcc.Timer(id="timer3", fire_times=[1]),
        ]
    )

    dash_dcc.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    time.sleep(1)
    dash_dcc.wait_for_element("#timer3")
    dash_dcc.percy_snapshot("time006 - multiple of interval errors")

    assert dash_dcc.get_logs() != []
