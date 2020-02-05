from multiprocessing import Value

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


def test_cbsc001_simple_callback(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(html.Div([1.5, None, "string", html.Div(id="output-1")])),
        ]
    )
    call_count = Value("i", 0)

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        call_count.value = call_count.value + 1
        return value

    dash_duo.start_server(app)

    assert dash_duo.find_element("#output-1").text == "initial value"
    dash_duo.percy_snapshot(name="simple-callback-initial")

    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)

    input_.send_keys("hello world")

    assert dash_duo.find_element("#output-1").text == "hello world"
    dash_duo.percy_snapshot(name="simple-callback-hello-world")

    assert call_count.value == 2 + len(
        "hello world"
    ), "initial count + each key stroke"

    assert dash_duo.redux_state_rqs == []

    assert dash_duo.get_logs() == []


def test_cbsc002_callbacks_generating_children(dash_duo):
    """Modify the DOM tree by adding new components in the callbacks."""

    # some components don't exist in the initial render
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [dcc.Input(id="input", value="initial value"), html.Div(id="output")]
    )

    @app.callback(Output("output", "children"), [Input("input", "value")])
    def pad_output(input):
        return html.Div(
            [
                dcc.Input(id="sub-input-1", value="sub input initial value"),
                html.Div(id="sub-output-1"),
            ]
        )

    call_count = Value("i", 0)

    @app.callback(
        Output("sub-output-1", "children"), [Input("sub-input-1", "value")]
    )
    def update_input(value):
        call_count.value = call_count.value + 1
        return value

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#sub-output-1", "sub input initial value")

    assert call_count.value == 1, "called once at initial stage"

    pad_input, pad_div = dash_duo.dash_innerhtml_dom.select_one(
        "#output > div"
    ).contents

    assert (
        pad_input.attrs["value"] == "sub input initial value"
        and pad_input.attrs["id"] == "sub-input-1"
    )
    assert pad_input.name == "input"

    assert (
        pad_div.text == pad_input.attrs["value"]
        and pad_div.get("id") == "sub-output-1"
    ), "the sub-output-1 content reflects to sub-input-1 value"

    dash_duo.percy_snapshot(name="callback-generating-function-1")

    paths = dash_duo.redux_state_paths
    assert paths["objs"] == {}
    assert paths["strs"] == {
        "input": ["props", "children", 0],
        "output": ["props", "children", 1],
        "sub-input-1": [
            "props",
            "children",
            1,
            "props",
            "children",
            "props",
            "children",
            0,
        ],
        "sub-output-1": [
            "props",
            "children",
            1,
            "props",
            "children",
            "props",
            "children",
            1,
        ],
    }, "the paths should include these new output IDs"

    # editing the input should modify the sub output
    dash_duo.find_element("#sub-input-1").send_keys("deadbeef")

    assert (
        dash_duo.find_element("#sub-output-1").text
        == pad_input.attrs["value"] + "deadbeef"
    ), "deadbeef is added"

    # the total updates is initial one + the text input changes
    dash_duo.wait_for_text_to_equal(
        "#sub-output-1", pad_input.attrs["value"] + "deadbeef"
    )

    assert dash_duo.redux_state_rqs == [], "pendingCallbacks is empty"

    dash_duo.percy_snapshot(name="callback-generating-function-2")
    assert dash_duo.get_logs() == [], "console is clean"


def test_cbsc003_callback_with_unloaded_async_component(dash_duo):
    app = dash.Dash()
    app.layout = html.Div(
        children=[
            dcc.Tabs(
                children=[
                    dcc.Tab(
                        children=[
                            html.Button(id="btn", children="Update Input"),
                            html.Div(id="output", children=["Hello"]),
                        ]
                    ),
                    dcc.Tab(children=dash_table.DataTable(id="other-table")),
                ]
            )
        ]
    )

    @app.callback(Output("output", "children"), [Input("btn", "n_clicks")])
    def update_graph(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return "Bye"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()
    assert dash_duo.find_element("#output").text == "Bye"
    assert dash_duo.get_logs() == []


def test_cbsc004_children_types(dash_duo):
    app = dash.Dash()
    app.layout = html.Div([
        html.Button(id="btn"),
        html.Div("init", id="out")
    ])

    outputs = [
        [None, ""],
        ["a string", "a string"],
        [123, "123"],
        [123.45, "123.45"],
        [[6, 7, 8], "678"],
        [["a", "list", "of", "strings"], "alistofstrings"],
        [["strings", 2, "numbers"], "strings2numbers"],
        [["a string", html.Div("and a div")], "a string\nand a div"]
    ]

    @app.callback(Output("out", "children"), [Input("btn", "n_clicks")])
    def set_children(n):
        if n is None or n > len(outputs):
            return dash.no_update
        return outputs[n - 1][0]

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "init")

    for children, text in outputs:
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#out", text)


def test_cbsc005_array_of_objects(dash_duo):
    app = dash.Dash()
    app.layout = html.Div([
        html.Button(id="btn"),
        dcc.Dropdown(id="dd"),
        html.Div(id="out")
    ])

    @app.callback(Output("dd", "options"), [Input("btn", "n_clicks")])
    def set_options(n):
        return [
            {"label": "opt{}".format(i), "value": i}
            for i in range(n or 0)
        ]

    @app.callback(Output("out", "children"), [Input("dd", "options")])
    def set_out(opts):
        print(repr(opts))
        return len(opts)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "0")
    for i in range(5):
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#out", str(i + 1))
        dash_duo.select_dcc_dropdown("#dd", "opt{}".format(i))
