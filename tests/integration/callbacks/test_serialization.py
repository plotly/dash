import datetime

import pandas as pd
import plotly.graph_objects as go
import pytest

from dash import Dash, Input, Output, State, dcc, html
from tests.integration.utils import json_engine


@pytest.mark.parametrize("engine", ["json", "orjson"])
def test_cbsr001_figure_component_and_timestamp_in_one_response(dash_duo, engine):
    with json_engine(engine):
        app = Dash()
        app.layout = html.Div(
            [
                html.Button("go", id="btn"),
                dcc.Graph(id="graph"),
                html.Div(id="status"),
                dcc.Store(id="store"),
                html.Div(id="check"),
            ]
        )
        start = datetime.datetime(2024, 1, 1)
        x = [start + datetime.timedelta(minutes=i) for i in range(2000)]

        @app.callback(
            Output("graph", "figure"),
            Output("status", "children"),
            Output("store", "data"),
            Input("btn", "n_clicks"),
            prevent_initial_call=True,
        )
        def update(_):
            fig = go.Figure(go.Scatter(x=x, y=[float(i) for i in range(2000)]))
            return fig, html.B("ok"), {"at": pd.Timestamp("2024-01-01 12:00")}

        @app.callback(
            Output("check", "children"),
            Input("store", "data"),
            State("graph", "figure"),
            prevent_initial_call=True,
        )
        def check(data, figure):
            trace = figure["data"][0]
            return f"{data['at']} {len(trace['x'])} {trace['x'][-1]} {trace['y'][-1]}"

        dash_duo.start_server(app)
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#status", "ok")
        dash_duo.wait_for_text_to_equal(
            "#check", "2024-01-01T12:00:00 2000 2024-01-02T09:19:00 1999"
        )
        dash_duo.wait_for_element("#graph .scatterlayer .trace")
        assert dash_duo.get_logs() == []
