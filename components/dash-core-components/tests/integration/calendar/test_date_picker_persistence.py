from datetime import datetime

from dash import Dash, Input, Output, html, dcc


def test_rdpr001_persisted_dps(dash_dcc):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Button("fire callback", id="btn", n_clicks=1),
            html.Div(children=[html.Div(id="container"), html.P("dps", id="dps-p")]),
        ]
    )

    # changing value of date with each callback to verify
    # persistenceTransforms is stripping the time-part from the date-time
    @app.callback(Output("container", "children"), [Input("btn", "n_clicks")])
    def update_output(value):
        return dcc.DatePickerSingle(
            id="dps",
            min_date_allowed=datetime(2020, 1, 1),
            max_date_allowed=datetime(2020, 1, 7),
            date=datetime(2020, 1, 3, 1, 1, 1, value),
            persistence=True,
            persistence_type="session",
        )

    @app.callback(Output("dps-p", "children"), [Input("dps", "date")])
    def display_dps(value):
        return value

    dash_dcc.start_server(app)

    dash_dcc.select_date_single("dps", day="2")
    dash_dcc.wait_for_text_to_equal("#dps-p", "2020-01-02")
    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_text_to_equal("#dps-p", "2020-01-02")

    assert dash_dcc.get_logs() == []


def test_rdpr002_persisted_dpr(dash_dcc):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Button("fire callback", id="btn", n_clicks=1),
            html.Div(
                children=[
                    html.Div(id="container"),
                    html.P("dpr", id="dpr-p-start"),
                    html.P("dpr", id="dpr-p-end"),
                ]
            ),
        ]
    )

    # changing value of start_date and end_date with each callback to verify
    # persistenceTransforms is stripping the time-part from the date-time
    @app.callback(Output("container", "children"), [Input("btn", "n_clicks")])
    def update_output(value):
        return dcc.DatePickerRange(
            id="dpr",
            min_date_allowed=datetime(2020, 1, 1),
            max_date_allowed=datetime(2020, 1, 7),
            start_date=datetime(2020, 1, 3, 1, 1, 1, value),
            end_date=datetime(2020, 1, 4, 1, 1, 1, value),
            persistence=True,
            persistence_type="session",
        )

    @app.callback(Output("dpr-p-start", "children"), [Input("dpr", "start_date")])
    def display_dpr_start(value):
        return value

    @app.callback(Output("dpr-p-end", "children"), [Input("dpr", "end_date")])
    def display_dpr_end(value):
        return value

    dash_dcc.start_server(app)

    dash_dcc.select_date_range("dpr", (2, 5))
    dash_dcc.wait_for_text_to_equal("#dpr-p-start", "2020-01-02")
    dash_dcc.wait_for_text_to_equal("#dpr-p-end", "2020-01-05")
    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_text_to_equal("#dpr-p-start", "2020-01-02")
    dash_dcc.wait_for_text_to_equal("#dpr-p-end", "2020-01-05")

    assert dash_dcc.get_logs() == []
