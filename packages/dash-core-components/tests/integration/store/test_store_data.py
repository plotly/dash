import json
import hashlib
import itertools
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html


def test_stda001_data_types(dash_duo):
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

    dash_duo.start_server(app)

    button = dash_duo.wait_for_element("#click")
    for data_type in data_types:
        button.click()
        dash_duo.wait_for_text_to_equal("#output", json.dumps(data_type[1]))


def test_stda002_nested_data(dash_duo):
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

    obj_btn = dash_duo.wait_for_element("#obj-btn")
    list_btn = dash_duo.find_element("#list-btn")

    obj_btn.click()
    dash_duo.wait_for_text_to_equal("#output", json.dumps(nested))
    # it would of crashed the app before adding the recursive check.

    list_btn.click()
    dash_duo.wait_for_text_to_equal("#output", json.dumps(nested_list))


def test_stda003_data_size_limit(fake_data, dash_duo):
    def fingerprint(data):
        return hashlib.sha1(data.encode("utf-8")).hexdigest()

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Store(id="memory", storage_type="memory"),
            dcc.Store(id="local", storage_type="local"),
            dcc.Store(id="session", storage_type="session"),
            html.Button("big data", id="btn"),
            html.Div(id="mout"),
            html.Div(id="sout"),
            html.Div(id="lout"),
        ]
    )

    @app.callback(
        [
            Output("mout", "children"),
            Output("sout", "children"),
            Output("lout", "children"),
        ],
        [
            Input("memory", "modified_timestamp"),
            Input("session", "modified_timestamp"),
            Input("local", "modified_timestamp"),
        ],
        [
            State("memory", "data"),
            State("session", "data"),
            State("local", "data"),
        ],
    )
    def update_output(mts, sts, lts, mdata, sdata, ldata):
        if None in {mdata, sdata, ldata}:
            return ("nil",) * 3
        return [fingerprint(data) for data in (mdata, sdata, ldata)]

    @app.callback(
        [
            Output("memory", "data"),
            Output("local", "data"),
            Output("session", "data"),
        ],
        [Input("btn", "n_clicks")],
    )
    def on_click(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return (fake_data,) * 3

    dash_duo.start_server(app)
    outputs = ('#mout', '#lout', '#sout')
    for output in outputs:
        assert dash_duo.find_element(output).text == 'nil'

    dash_duo.find_element('#btn').click()
    for output in outputs:
        dash_duo.wait_for_text_to_equal(output, fingerprint(fake_data))

