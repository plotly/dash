import json

from dash import Dash, html, dcc, Input, Output, State, ALL, Patch


def test_pch001_patch_operations(dash_duo):

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Input(id="set-value"),
                    html.Button("Set", id="set-btn"),
                ]
            ),
            html.Div(
                [
                    dcc.Input(id="append-value"),
                    html.Button("Append", id="append-btn"),
                ]
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
                [
                    dcc.Input(id="extend-value"),
                    html.Button("extend", id="extend-btn"),
                ]
            ),
            html.Div(
                [
                    dcc.Input(id="merge-value"),
                    html.Button("Merge", id="merge-btn"),
                ]
            ),
            html.Button("Delete", id="delete-btn"),
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
        "function(value) {return JSON.stringify(value)}",
        Output("store-content", "children"),
        Input("store", "data"),
    )

    @app.callback(
        Output("store", "data"),
        Input("set-btn", "n_clicks"),
        State("set-value", "value"),
        prevent_initial_call=True,
    )
    def on_click(_, value):
        p = Patch()
        p.value = value
        p.n_clicks += 1

        return p

    @app.callback(
        Output("store", "data", allow_duplicate=True),
        Input("append-btn", "n_clicks"),
        State("append-value", "value"),
        prevent_initial_call=True,
    )
    def on_click(_, value):
        p = Patch()
        p.array.append(value)
        p.n_clicks += 1

        return p

    @app.callback(
        Output("store", "data", allow_duplicate=True),
        Input("prepend-btn", "n_clicks"),
        State("prepend-value", "value"),
        prevent_initial_call=True,
    )
    def on_click(_, value):
        p = Patch()
        p.array.prepend(value)
        p.n_clicks += 1

        return p

    @app.callback(
        Output("store", "data", allow_duplicate=True),
        Input("extend-btn", "n_clicks"),
        State("extend-value", "value"),
        prevent_initial_call=True,
    )
    def on_click(_, value):
        p = Patch()
        p.array.extend([value])
        p.n_clicks += 1

        return p

    @app.callback(
        Output("store", "data", allow_duplicate=True),
        Input("merge-btn", "n_clicks"),
        State("merge-value", "value"),
        prevent_initial_call=True,
    )
    def on_click(_, value):
        p = Patch()
        p.merge({"merged": value})
        p.n_clicks += 1

        return p

    @app.callback(
        Output("store", "data", allow_duplicate=True),
        Input("delete-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(_):
        p = Patch()
        del p.delete
        return p

    @app.callback(
        Output("store", "data", allow_duplicate=True),
        Input("insert-btn", "n_clicks"),
        State("insert-value", "value"),
        State("insert-index", "value"),
        prevent_initial_call=True,
    )
    def on_insert(_, value, index):
        p = Patch()
        p.array.insert(index, value)

        return p

    dash_duo.start_server(app)

    assert dash_duo.get_logs() == []

    def get_output():
        e = dash_duo.find_element("#store-content")
        return json.loads(e.text)

    _input = dash_duo.find_element("#set-value")
    _input.send_keys("Set Value")
    dash_duo.find_element("#set-btn").click()

    assert get_output()["value"] == "Set Value"

    _input = dash_duo.find_element("#append-value")
    _input.send_keys("Append")
    dash_duo.find_element("#append-btn").click()

    assert get_output()["array"] == ["initial", "Append"]

    _input = dash_duo.find_element("#prepend-value")
    _input.send_keys("Prepend")
    dash_duo.find_element("#prepend-btn").click()

    assert get_output()["array"] == ["Prepend", "initial", "Append"]

    _input = dash_duo.find_element("#extend-value")
    _input.send_keys("Extend")
    dash_duo.find_element("#extend-btn").click()

    assert get_output()["array"] == ["Prepend", "initial", "Append", "Extend"]

    undef = object()
    assert get_output().get("merge", undef) is undef

    _input = dash_duo.find_element("#merge-value")
    _input.send_keys("Merged")
    dash_duo.find_element("#merge-btn").click()

    assert get_output()["merged"] == "Merged"

    assert get_output()["delete"] == "Delete me"

    dash_duo.find_element("#delete-btn").click()

    assert get_output().get("delete", undef) is undef

    _input = dash_duo.find_element("#insert-value")
    _input.send_keys("Inserted")
    dash_duo.find_element("#insert-btn").click()

    assert get_output().get("array") == [
        "Prepend",
        "Inserted",
        "initial",
        "Append",
        "Extend",
    ]


def test_pch002_patch_app_pmc_callbacks(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("Click", id="click"),
            html.Div(id={"type": "output", "index": 0}, className="first"),
            html.Div(id={"type": "output", "index": 1}, className="second"),
        ]
    )

    @app.callback(
        Output({"type": "output", "index": ALL}, "children"), Input("click", "n_clicks")
    )
    def on_click(n_clicks):
        if n_clicks is None:
            return ["Foo", "Bar"]
        p1 = Patch()
        p2 = Patch()

        p1.append("Bar")
        p2.prepend("Foo")

        return [p1, p2]

    dash_duo.start_server(app)

    dash_duo.find_element("#click").click()
    dash_duo.wait_for_text_to_equal(".first", "FooBar")
    dash_duo.wait_for_text_to_equal(".second", "FooBar")


def test_pch003_patch_children(dash_duo):

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [
                    dcc.Input(value="", id="children-value"),
                    html.Button("Add", id="add-children"),
                ]
            ),
            html.Div([html.Div("init", id="initial")], id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("add-children", "n_clicks"),
        State("children-value", "value"),
        prevent_initial_call=True,
    )
    def on_click(_, value):
        p = Patch()
        p.append(html.Div(value, id=value))

        return p

    dash_duo.start_server(app)

    _input = dash_duo.find_element("#children-value")
    _input.send_keys("new-child")
    dash_duo.find_element("#add-children").click()

    dash_duo.wait_for_text_to_equal("#new-child", "new-child")
    dash_duo.wait_for_text_to_equal("#initial", "init")
