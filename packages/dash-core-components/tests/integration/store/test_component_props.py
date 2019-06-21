import json
import time
from pytest import approx
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html


def test_stcp100_clear_data_on_all_types(store_app, dash_duo):
    dash_duo.start_server(store_app)

    assert dash_duo.wait_for_contains_text("#output", store_app.uuid)

    dash_duo.multiple_click("#btn", 3)
    assert dash_duo.get_local_storage() == {"n_clicks": 3}

    # button click sets clear_data=True on all type of stores
    dash_duo.find_element("#clear-btn").click()

    assert (
        not dash_duo.find_element("#output").text
        and not dash_duo.get_local_storage()
        and not dash_duo.get_session_storage()
    ), "set clear_data=True should clear all data in three storage types"


def test_stcp200_modified_ts(store_app, dash_duo):
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

    dash_duo.start_server(app)

    dash_duo.find_element("#set-init-storage").click()
    # the python ts ends at seconds while javascript one ends at ms
    ts = float(time.time() * 1000)

    output_data = json.loads(dash_duo.find_element("#init-output").text)

    assert (
        output_data.get("data") == "initialized"
    ), "the data should be the text set in on_init"
    assert ts == approx(
        output_data.get("ts"), abs=40
    ), "the modified_timestamp should be updated right after the click action"
