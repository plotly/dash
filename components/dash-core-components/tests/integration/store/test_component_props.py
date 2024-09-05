import json
import time
from pytest import approx
from dash import Dash, Input, State, Output, dcc, html
from dash.exceptions import PreventUpdate
import dash.testing.wait as wait


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

    assert dash_dcc.get_logs() == []


def test_stcp002_modified_ts(store_app, dash_dcc):
    app = Dash(__name__)
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

    wait.until(
        lambda: "initialized" in dash_dcc.find_element("#init-output").text, timeout=3
    )

    output_data = json.loads(dash_dcc.find_element("#init-output").text)

    assert (
        output_data.get("data") == "initialized"
    ), "the data should be the text set in on_init"
    assert ts == approx(
        output_data.get("ts"), abs=40
    ), "the modified_timestamp should be updated right after the click action"

    assert dash_dcc.get_logs() == []


def test_stcp003_initial_falsy(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    storage_type,
                    dcc.Store(
                        storage_type=storage_type, id="zero-" + storage_type, data=0
                    ),
                    dcc.Store(
                        storage_type=storage_type,
                        id="false-" + storage_type,
                        data=False,
                    ),
                    dcc.Store(
                        storage_type=storage_type, id="null-" + storage_type, data=None
                    ),
                    dcc.Store(
                        storage_type=storage_type, id="empty-" + storage_type, data=""
                    ),
                ]
            )
            for storage_type in ("memory", "local", "session")
        ],
        id="content",
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#content", "memory\nlocal\nsession")

    for storage_type in ("local", "session"):
        getter = getattr(dash_dcc, f"get_{storage_type}_storage")
        assert getter("zero-" + storage_type) == 0, storage_type
        assert getter("false-" + storage_type) is False, storage_type
        assert getter("null-" + storage_type) is None, storage_type
        assert getter("empty-" + storage_type) == "", storage_type

    assert dash_dcc.get_logs() == []


def test_stcp004_remount_store_component(dash_dcc):
    app = Dash(__name__, suppress_callback_exceptions=True)

    content = html.Div(
        [
            dcc.Store(id="memory", storage_type="memory"),
            dcc.Store(id="local", storage_type="local"),
            dcc.Store(id="session", storage_type="session"),
            html.Button("click me", id="btn"),
            html.Button("clear data", id="clear-btn"),
            html.Div(id="output"),
        ]
    )

    app.layout = html.Div([html.Button("start", id="start"), html.Div(id="content")])

    @app.callback(Output("content", "children"), [Input("start", "n_clicks")])
    def start(n):
        return content if n else "init"

    @app.callback(
        Output("output", "children"),
        [
            Input("memory", "modified_timestamp"),
            Input("local", "modified_timestamp"),
            Input("session", "modified_timestamp"),
        ],
        [State("memory", "data"), State("local", "data"), State("session", "data")],
    )
    def write_memory(tsm, tsl, tss, datam, datal, datas):
        return json.dumps([datam, datal, datas])

    @app.callback(
        [
            Output("local", "clear_data"),
            Output("memory", "clear_data"),
            Output("session", "clear_data"),
        ],
        [Input("clear-btn", "n_clicks")],
    )
    def on_clear(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return True, True, True

    @app.callback(
        [Output("memory", "data"), Output("local", "data"), Output("session", "data")],
        [Input("btn", "n_clicks")],
    )
    def on_click(n_clicks):
        return ({"n_clicks": n_clicks},) * 3

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#content", "init")

    dash_dcc.find_element("#start").click()
    dash_dcc.wait_for_text_to_equal(
        "#output", '[{"n_clicks": null}, {"n_clicks": null}, {"n_clicks": null}]'
    )

    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_text_to_equal(
        "#output", '[{"n_clicks": 1}, {"n_clicks": 1}, {"n_clicks": 1}]'
    )

    dash_dcc.find_element("#clear-btn").click()
    dash_dcc.wait_for_text_to_equal("#output", "[null, null, null]")

    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_text_to_equal(
        "#output", '[{"n_clicks": 2}, {"n_clicks": 2}, {"n_clicks": 2}]'
    )

    # now remount content components
    dash_dcc.find_element("#start").click()
    dash_dcc.wait_for_text_to_equal(
        "#output", '[{"n_clicks": null}, {"n_clicks": null}, {"n_clicks": null}]'
    )

    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_text_to_equal(
        "#output", '[{"n_clicks": 1}, {"n_clicks": 1}, {"n_clicks": 1}]'
    )

    assert dash_dcc.get_logs() == []
