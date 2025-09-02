import json

import flaky

from selenium.webdriver.common.keys import Keys

from dash import Dash, html, dcc, Input, Output, State, ALL, Patch
from dash.testing.wait import until


@flaky.flaky(max_runs=3)
def test_pch_cs001_patch_operations_clientside(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div([dcc.Input(id="set-value"), html.Button("Set", id="set-btn")]),
            html.Div(
                [dcc.Input(id="append-value"), html.Button("Append", id="append-btn")]
            ),
            html.Div(
                [
                    dcc.Input(id="prepend-value"),
                    html.Button("prepend", id="prepend-btn"),
                ]
            ),
            html.Div(
                [
                    dcc.Input(id="insert-value"),
                    dcc.Input(id="insert-index", type="number", value=1),
                    html.Button("insert", id="insert-btn"),
                ]
            ),
            html.Div(
                [dcc.Input(id="extend-value"), html.Button("extend", id="extend-btn")]
            ),
            html.Div(
                [dcc.Input(id="merge-value"), html.Button("Merge", id="merge-btn")]
            ),
            html.Button("Delete", id="delete-btn"),
            html.Button("Delete index", id="delete-index"),
            html.Button("Clear", id="clear-btn"),
            html.Button("Reverse", id="reverse-btn"),
            html.Button("Remove", id="remove-btn"),
            dcc.Store(
                data={
                    "value": "unset",
                    "n_clicks": 0,
                    "array": ["initial"],
                    "delete": "Delete me",
                },
                id="store",
            ),
            html.Div(id="store-content"),
        ]
    )

    app.clientside_callback(
        "function a(value) {return JSON.stringify(value)}",
        Output("store-content", "children"),
        Input("store", "data"),
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            return patch
                .assign(["value"], value)
                .add(["n_clicks"], 1)
                .build();
        }
        """,
        Output("store", "data"),
        Input("set-btn", "n_clicks"),
        State("set-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            return patch
                .append(["array"], value)
                .add(["n_clicks"], 1)
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("append-btn", "n_clicks"),
        State("append-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            return patch
                .prepend(["array"], value)
                .add(["n_clicks"], 1)
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("prepend-btn", "n_clicks"),
        State("prepend-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            return patch
                .extend(["array"], [value])
                .add(["n_clicks"], 1)
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("extend-btn", "n_clicks"),
        State("extend-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            return patch
                .merge([], {merged: value})
                .add(["n_clicks"], 1)
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("merge-btn", "n_clicks"),
        State("merge-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            return patch
                .delete(["delete"])
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("delete-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value, index) {
            const patch = new dash_clientside.Patch
            return patch
                .insert(["array"], index, value)
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("insert-btn", "n_clicks"),
        State("insert-value", "value"),
        State("insert-index", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            return patch
                .delete(["array", 1])
                .delete(["array", -2])
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("delete-index", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            return patch
                .clear(["array"])
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("clear-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            return patch
                .reverse(["array"])
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("reverse-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            return patch
                .remove(["array"], "initial")
                .build();
        }
        """,
        Output("store", "data", allow_duplicate=True),
        Input("remove-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    assert dash_duo.get_logs() == []

    def get_output():
        e = dash_duo.find_element("#store-content")
        return json.loads(e.text)

    _input = dash_duo.find_element("#set-value")
    _input.send_keys("Set Value")
    dash_duo.find_element("#set-btn").click()

    until(lambda: get_output().get("value") == "Set Value", 2)

    _input = dash_duo.find_element("#append-value")
    _input.send_keys("Append")
    dash_duo.find_element("#append-btn").click()

    until(lambda: get_output().get("array") == ["initial", "Append"], 2)

    _input = dash_duo.find_element("#prepend-value")
    _input.send_keys("Prepend")
    dash_duo.find_element("#prepend-btn").click()

    until(lambda: get_output().get("array") == ["Prepend", "initial", "Append"], 2)

    _input = dash_duo.find_element("#extend-value")
    _input.send_keys("Extend")
    dash_duo.find_element("#extend-btn").click()

    until(
        lambda: get_output().get("array") == ["Prepend", "initial", "Append", "Extend"],
        2,
    )

    undef = object()
    until(lambda: get_output().get("merged", undef) is undef, 2)

    _input = dash_duo.find_element("#merge-value")
    _input.send_keys("Merged")
    dash_duo.find_element("#merge-btn").click()

    until(lambda: get_output().get("merged") == "Merged", 2)

    until(lambda: get_output().get("delete") == "Delete me", 2)

    dash_duo.find_element("#delete-btn").click()

    until(lambda: get_output().get("delete", undef) is undef, 2)

    _input = dash_duo.find_element("#insert-value")
    _input.send_keys("Inserted")
    dash_duo.find_element("#insert-btn").click()

    until(
        lambda: get_output().get("array")
        == [
            "Prepend",
            "Inserted",
            "initial",
            "Append",
            "Extend",
        ],
        2,
    )

    _input.send_keys(" with negative index")
    _input = dash_duo.find_element("#insert-index")
    _input.send_keys(Keys.BACKSPACE)
    _input.send_keys("-1")
    dash_duo.find_element("#insert-btn").click()

    until(
        lambda: get_output().get("array")
        == [
            "Prepend",
            "Inserted",
            "initial",
            "Append",
            "Inserted with negative index",
            "Extend",
        ],
        2,
    )

    dash_duo.find_element("#delete-index").click()
    until(
        lambda: get_output().get("array")
        == [
            "Prepend",
            "initial",
            "Append",
            "Extend",
        ],
        2,
    )

    dash_duo.find_element("#reverse-btn").click()
    until(
        lambda: get_output().get("array")
        == [
            "Extend",
            "Append",
            "initial",
            "Prepend",
        ],
        2,
    )

    dash_duo.find_element("#remove-btn").click()
    until(
        lambda: get_output().get("array")
        == [
            "Extend",
            "Append",
            "Prepend",
        ],
        2,
    )

    dash_duo.find_element("#clear-btn").click()
    until(lambda: get_output()["array"] == [], 2)


@flaky.flaky(max_runs=3)
def test_pch_cs002_patch_operations_set_props(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div([dcc.Input(id="set-value"), html.Button("Set", id="set-btn")]),
            html.Div(
                [dcc.Input(id="append-value"), html.Button("Append", id="append-btn")]
            ),
            html.Div(
                [
                    dcc.Input(id="prepend-value"),
                    html.Button("prepend", id="prepend-btn"),
                ]
            ),
            html.Div(
                [
                    dcc.Input(id="insert-value"),
                    dcc.Input(id="insert-index", type="number", value=1),
                    html.Button("insert", id="insert-btn"),
                ]
            ),
            html.Div(
                [dcc.Input(id="extend-value"), html.Button("extend", id="extend-btn")]
            ),
            html.Div(
                [dcc.Input(id="merge-value"), html.Button("Merge", id="merge-btn")]
            ),
            html.Button("Delete", id="delete-btn"),
            html.Button("Delete index", id="delete-index"),
            html.Button("Clear", id="clear-btn"),
            html.Button("Reverse", id="reverse-btn"),
            html.Button("Remove", id="remove-btn"),
            dcc.Store(
                data={
                    "value": "unset",
                    "n_clicks": 0,
                    "array": ["initial"],
                    "delete": "Delete me",
                },
                id="store",
            ),
            html.Div(id="store-content"),
        ]
    )

    app.clientside_callback(
        "function a(value) {return JSON.stringify(value)}",
        Output("store-content", "children"),
        Input("store", "data"),
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .assign(["value"], value)
                .add(["n_clicks"], 1)
                .build()});
        }
        """,
        Input("set-btn", "n_clicks"),
        State("set-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .append(["array"], value)
                .add(["n_clicks"], 1)
                .build()});
        }
        """,
        Input("append-btn", "n_clicks"),
        State("append-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .prepend(["array"], value)
                .add(["n_clicks"], 1)
                .build()});
        }
        """,
        Input("prepend-btn", "n_clicks"),
        State("prepend-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .extend(["array"], [value])
                .add(["n_clicks"], 1)
                .build()});
        }
        """,
        Input("extend-btn", "n_clicks"),
        State("extend-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .merge([], {merged: value})
                .add(["n_clicks"], 1)
                .build()});
        }
        """,
        Input("merge-btn", "n_clicks"),
        State("merge-value", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .delete(["delete"])
                .build()});
        }
        """,
        Input("delete-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks, value, index) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .insert(["array"], index, value)
                .build()});
        }
        """,
        Input("insert-btn", "n_clicks"),
        State("insert-value", "value"),
        State("insert-index", "value"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .delete(["array", 1])
                .delete(["array", -2])
                .build()});
        }
        """,
        Input("delete-index", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .clear(["array"])
                .build()});
        }
        """,
        Input("clear-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .reverse(["array"])
                .build()});
        }
        """,
        Input("reverse-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    app.clientside_callback(
        """
        function a(n_clicks) {
            const patch = new dash_clientside.Patch
            dash_clientside.set_props('store', {data: patch
                .remove(["array"], "initial")
                .build()});
        }
        """,
        Input("remove-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    assert dash_duo.get_logs() == []

    def get_output():
        e = dash_duo.find_element("#store-content")
        return json.loads(e.text)

    _input = dash_duo.find_element("#set-value")
    _input.send_keys("Set Value")
    dash_duo.find_element("#set-btn").click()

    until(lambda: get_output().get("value") == "Set Value", 2)

    _input = dash_duo.find_element("#append-value")
    _input.send_keys("Append")
    dash_duo.find_element("#append-btn").click()

    until(lambda: get_output().get("array") == ["initial", "Append"], 2)

    _input = dash_duo.find_element("#prepend-value")
    _input.send_keys("Prepend")
    dash_duo.find_element("#prepend-btn").click()

    until(lambda: get_output().get("array") == ["Prepend", "initial", "Append"], 2)

    _input = dash_duo.find_element("#extend-value")
    _input.send_keys("Extend")
    dash_duo.find_element("#extend-btn").click()

    until(
        lambda: get_output().get("array") == ["Prepend", "initial", "Append", "Extend"],
        2,
    )

    undef = object()
    until(lambda: get_output().get("merged", undef) is undef, 2)

    _input = dash_duo.find_element("#merge-value")
    _input.send_keys("Merged")
    dash_duo.find_element("#merge-btn").click()

    until(lambda: get_output().get("merged") == "Merged", 2)

    until(lambda: get_output().get("delete") == "Delete me", 2)

    dash_duo.find_element("#delete-btn").click()

    until(lambda: get_output().get("delete", undef) is undef, 2)

    _input = dash_duo.find_element("#insert-value")
    _input.send_keys("Inserted")
    dash_duo.find_element("#insert-btn").click()

    until(
        lambda: get_output().get("array")
        == [
            "Prepend",
            "Inserted",
            "initial",
            "Append",
            "Extend",
        ],
        2,
    )

    _input.send_keys(" with negative index")
    _input = dash_duo.find_element("#insert-index")
    _input.send_keys(Keys.BACKSPACE)
    _input.send_keys("-1")
    dash_duo.find_element("#insert-btn").click()

    until(
        lambda: get_output().get("array")
        == [
            "Prepend",
            "Inserted",
            "initial",
            "Append",
            "Inserted with negative index",
            "Extend",
        ],
        2,
    )

    dash_duo.find_element("#delete-index").click()
    until(
        lambda: get_output().get("array")
        == [
            "Prepend",
            "initial",
            "Append",
            "Extend",
        ],
        2,
    )

    dash_duo.find_element("#reverse-btn").click()
    until(
        lambda: get_output().get("array")
        == [
            "Extend",
            "Append",
            "initial",
            "Prepend",
        ],
        2,
    )

    dash_duo.find_element("#remove-btn").click()
    until(
        lambda: get_output().get("array")
        == [
            "Extend",
            "Append",
            "Prepend",
        ],
        2,
    )

    dash_duo.find_element("#clear-btn").click()
    until(lambda: get_output()["array"] == [], 2)
