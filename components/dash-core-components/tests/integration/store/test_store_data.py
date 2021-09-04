import sys
import json
import hashlib
import itertools
import pytest
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate


def test_stda001_data_types(dash_dcc):
    app = Dash(__name__)

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
    data_types = list(
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
        return data_types[n_clicks - 1][1]

    dash_dcc.start_server(app)

    button = dash_dcc.wait_for_element("#click")
    for data_type in data_types:
        button.click()
        dash_dcc.wait_for_text_to_equal("#output", json.dumps(data_type[1]))

    assert dash_dcc.get_logs() == []


def test_stda002_nested_data(dash_dcc):
    app = Dash(__name__)

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

    dash_dcc.start_server(app)

    obj_btn = dash_dcc.wait_for_element("#obj-btn")
    list_btn = dash_dcc.find_element("#list-btn")

    obj_btn.click()
    dash_dcc.wait_for_text_to_equal("#output", json.dumps(nested))
    # it would of crashed the app before adding the recursive check.

    list_btn.click()
    dash_dcc.wait_for_text_to_equal("#output", json.dumps(nested_list))

    assert dash_dcc.get_logs() == []


@pytest.mark.skipif(
    sys.version_info < (3, 6),
    reason="tests requires dependency only available in 3.6+",
)
@pytest.mark.parametrize("storage_type", ("memory", "local", "session"))
def test_stda003_large_data_size(storage_type, csv_5mb, dash_dcc):
    def fingerprint(data):
        return hashlib.sha1(data.encode("utf-8")).hexdigest()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Store(id=storage_type, storage_type=storage_type),
            html.Button("big data", id="btn"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        [Input(storage_type, "modified_timestamp")],
        [State(storage_type, "data")],
    )
    def update_output(mts, data):
        if data is None:
            return "nil"
        return fingerprint(data)

    @app.callback(Output(storage_type, "data"), [Input("btn", "n_clicks")])
    def on_click(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return csv_5mb

    dash_dcc.start_server(app)

    assert dash_dcc.find_element("#out").text == "nil"

    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_text_to_equal("#out", fingerprint(csv_5mb))

    assert dash_dcc.get_logs() == []
