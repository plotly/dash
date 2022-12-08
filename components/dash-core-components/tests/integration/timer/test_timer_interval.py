import time
from dash import Dash, dcc, html, Input, Output
from dash.testing import wait

# These are the same tests as /interval/test_interval.ppy


def test_tiin001_interval(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="output"),
            dcc.Timer(id="timer", interval=1, max_intervals=2),
        ]
    )

    @app.callback(Output("output", "children"), [Input("timer", "n_intervals")])
    def update_text(n):
        return f"{n}"

    dash_dcc.start_server(app)

    time.sleep(2)

    dash_dcc.wait_for_text_to_equal("#output", "2")
    assert dash_dcc.get_logs() == []


def test_tiin002_restart(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Timer(
                id="timer",
                interval=100,
                n_intervals=0,
                max_intervals=-1,
            ),
            html.Button("Start", id="start", n_clicks_timestamp=-1),
            html.Button("Stop", id="stop", n_clicks_timestamp=-1),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("timer", "max_intervals"),
        Input("start", "n_clicks_timestamp"),
        Input("stop", "n_clicks_timestamp"),
    )
    def start_stop(start, stop):
        if start < stop:
            return 0
        return -1

    @app.callback(Output("output", "children"), [Input("timer", "n_intervals")])
    def display_data(n_intervals):
        return f"Updated {n_intervals}"

    dash_dcc.start_server(app)

    wait.until(lambda: dash_dcc.find_element("#output").text != "Updated 0", 3)
    dash_dcc.find_element("#stop").click()
    time.sleep(2)

    text_now = dash_dcc.find_element("#output").text
    time.sleep(2)
    text_later = dash_dcc.find_element("#output").text

    assert text_now == text_later

    dash_dcc.find_element("#start").click()

    wait.until(lambda: dash_dcc.find_element("#output").text != text_later, 3)

    assert dash_dcc.get_logs() == []
