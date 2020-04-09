import json
import time
from pytest import approx
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash.testing.wait as wait
import dash_core_components as dcc
import dash_html_components as html


def test_stcp001_clear_data_on_all_types(store_app, dash_dcc):
    dash_dcc.start_server(store_app)

    assert dash_dcc.wait_for_contains_text("#output", store_app.uuid)

    dash_dcc.multiple_click("#btn", 3)
    wait.until(lambda: dash_dcc.get_local_storage() == {"n_clicks": 3}, timeout=1)

    # button click sets clear_data=True on all type of stores
    dash_dcc.find_element("#clear-btn").click()

    dash_dcc.wait_for_text_to_equal("#output", "")

    assert (
        not dash_dcc.find_element("#output").text
        and not dash_dcc.get_local_storage()
        and not dash_dcc.get_session_storage()
    ), "set clear_data=True should clear all data in three storage types"


def test_stcp002_modified_ts(store_app, dash_dcc):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Store(id="initial-storage", storage_type="session"),
            html.Button("set-init-storage", id="set-init-storage"),
            html.Div(id="init-output"),
        ]
    )

    @app.callback(
        Output("initial-storage", "data"),
        [Input("set-init-storage", "n_clicks")],
    )
    def on_init(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return "initialized"

    @app.callback(
        Output("init-output", "children"),
        [Input("initial-storage", "modified_timestamp")],
        [State("initial-storage", "data")],
    )
    def init_output(ts, data):
        return json.dumps({"data": data, "ts": ts})

    dash_dcc.start_server(app)

    dash_dcc.find_element("#set-init-storage").click()
    # the python ts ends at seconds while javascript one ends at ms
    ts = float(time.time() * 1000)

    output_data = json.loads(dash_dcc.find_element("#init-output").text)

    assert (
        output_data.get("data") == "initialized"
    ), "the data should be the text set in on_init"
    assert ts == approx(
        output_data.get("ts"), abs=40
    ), "the modified_timestamp should be updated right after the click action"
