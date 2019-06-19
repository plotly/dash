import json
import time
import itertools
from pytest import approx
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html


def test_stco001_storage_component_smoke(store_app, dash_duo):

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Store(id="memory", storage_type="memory"),
            dcc.Store(id="storage", storage_type="local"),
            dcc.Store(id="session", storage_type="session", data=dummy_data),
            dcc.Store(id="initial-storage", storage_type="session"),
            html.Button("click me", id="btn"),
            html.Button("clear", id="clear-btn"),
            html.Button("set-init-storage", id="set-init-storage"),
            html.Div(id="memory-output"),
            html.Div(id="init-output"),
        ]
    )

    @app.callback(
        Output("storage", "data"),
        [Input("btn", "n_clicks")],
        [State("storage", "data")],
    )
    def on_click(n_clicks, storage):
        if n_clicks is None:
            return
        storage = storage or {}
        return {"clicked": storage.get("clicked", 0) + 1}

    @app.callback(
        Output("storage", "clear_data"), [Input("clear-btn", "n_clicks")]
    )
    def on_clear(n_clicks):
        if n_clicks is None:
            return
        return True

    @app.callback(Output("memory", "data"), [Input("storage", "data")])
    def on_memory(data):
        return data

    @app.callback(
        Output("memory-output", "children"), [Input("memory", "data")]
    )
    def on_memory_json(data):
        if data is None:
            return ""
        return json.dumps(data)

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

    getter = 'return JSON.parse(window.{}.getItem("{}"));'
    clicked_getter = getter.format("localStorage", "storage")

    session = dash_duo.driver.execute_script(
        getter.format("sessionStorage", "session")
    )
    assert dummy_data == session

    for i in range(1, 11):
        dash_duo.find_element("#btn").click()
        click_data = dash_duo.driver.execute_script(clicked_getter)
        assert i == click_data.get("clicked")
        mem = dash_duo.wait_for_element("#memory-output")
        assert i == int(json.loads(mem.text).get("clicked"))


    # Test initial timestamp output
    dash_duo.find_element("#set-init-storage").click()
    # the python ts ends at seconds while javascript one ends at ms
    ts = float(time.time() * 1000)
    dash_duo.driver.refresh()
    init = json.loads(dash_duo.wait_for_element("#init-output").text)

    assert ts == approx(init.get("ts"), abs=10)
    assert init.get("data") == "initialized"


def test_store_nested_data(dash_duo):
    app = dash.Dash(__name__)

    nested = {"nested": {"nest": "much"}}
    nested_list = dict(my_list=[1, 2, 3])

    app.layout = html.Div(
        [
            dcc.Store(id="store", storage_type="local"),
            html.Button("set object as key", id="obj-btn"),
            html.Button("set list as key", id="list-btn"),
            html.Output(id="output"),
        ]
    )

    @app.callback(
        Output("store", "data"),
        [
            Input("obj-btn", "n_clicks_timestamp"),
            Input("list-btn", "n_clicks_timestamp"),
        ],
    )
    def on_obj_click(obj_ts, list_ts):
        if obj_ts is None and list_ts is None:
            raise PreventUpdate

        # python 3 got the default props bug. plotly/dash#396
        if (obj_ts and not list_ts) or obj_ts > list_ts:
            return nested
        else:
            return nested_list

    @app.callback(
        Output("output", "children"),
        [Input("store", "modified_timestamp")],
        [State("store", "data")],
    )
    def on_ts(ts, data):
        if ts is None:
            raise PreventUpdate
        return json.dumps(data)

    dash_duo.start_server(app)

    obj_btn = dash_duo.wait_for_element_by_css_selector("#obj-btn")
    list_btn = dash_duo.wait_for_element_by_css_selector("#list-btn")

    obj_btn.click()
    time.sleep(1)
    dash_duo.wait_for_text_to_equal("#output", json.dumps(nested))
    # it would of crashed the app before adding the recursive check.

    list_btn.click()
    time.sleep(1)
    dash_duo.wait_for_text_to_equal("#output", json.dumps(nested_list))


def test_stco003_data_type_updates(dash_duo):
    app = dash.Dash(__name__)

    types = [
        ("str", "hello"),
        ("number", 1),
        ("dict", {"data": [2, 3, None]}),
        ("list", [5, -6, 700000, 1e-12]),
        ("null", None),
        ("bool", True),
        ("bool", False),
        ("empty-dict", {}),
    ]
    types_changes = list(
        itertools.chain(*itertools.combinations(types, 2))
    ) + [  # No combinations as it add much test time.
        ("list-dict-1", [1, 2, {"data": [55, 66, 77], "dummy": "dum"}]),
        ("list-dict-2", [1, 2, {"data": [111, 99, 88]}]),
        ("dict-3", {"a": 1, "c": 1}),
        ("dict-2", {"a": 1, "b": None}),
    ]

    app.layout = html.Div(
        [
            html.Div(id="output"),
            html.Button("click", id="click"),
            dcc.Store(id="store"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input("store", "modified_timestamp")],
        [State("store", "data")],
    )
    def on_data(ts, data):
        if ts is None:
            raise PreventUpdate
        return json.dumps(data)

    @app.callback(Output("store", "data"), [Input("click", "n_clicks")])
    def on_click(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return types_changes[n_clicks - 1][1]

    dash_duo.start_server(app)

    button = dash_duo.wait_for_element("#click")
    for type_change in types_changes:
        button.click()
        dash_duo.wait_for_text_to_equal("#output", json.dumps(type_change[1]))
