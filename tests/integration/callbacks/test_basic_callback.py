import json
from multiprocessing import Lock, Value

import pytest

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash.testing import wait


def test_cbsc001_simple_callback(dash_duo):
    lock = Lock()

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
        with lock:
            call_count.value = call_count.value + 1
            return value

    dash_duo.start_server(app)

    assert dash_duo.find_element("#output-1").text == "initial value"
    dash_duo.percy_snapshot(name="simple-callback-initial")

    input_ = dash_duo.find_element("#input")
    dash_duo.clear_input(input_)

    for key in "hello world":
        with lock:
            input_.send_keys(key)

    wait.until(lambda: dash_duo.find_element("#output-1").text == "hello world", 2)
    dash_duo.percy_snapshot(name="simple-callback-hello-world")

    assert call_count.value == 2 + len("hello world"), "initial count + each key stroke"

    assert not dash_duo.redux_state_is_loading

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

    @app.callback(Output("sub-output-1", "children"), [Input("sub-input-1", "value")])
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
        pad_div.text == pad_input.attrs["value"] and pad_div.get("id") == "sub-output-1"
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

    assert not dash_duo.redux_state_is_loading, "loadingMap is empty"

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
    def update_out(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return "Bye"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Hello")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Bye")
    assert dash_duo.get_logs() == []


def test_cbsc004_callback_using_unloaded_async_component(dash_duo):
    app = dash.Dash()
    app.layout = html.Div(
        [
            dcc.Tabs(
                [
                    dcc.Tab("boo!"),
                    dcc.Tab(
                        dash_table.DataTable(
                            id="table",
                            columns=[{"id": "a", "name": "A"}],
                            data=[{"a": "b"}],
                        )
                    ),
                ]
            ),
            html.Button("Update Input", id="btn"),
            html.Div("Hello", id="output"),
            html.Div(id="output2"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input("btn", "n_clicks")],
        [State("table", "data")],
    )
    def update_out(n_clicks, data):
        return json.dumps(data) + " - " + str(n_clicks)

    @app.callback(
        Output("output2", "children"),
        [Input("btn", "n_clicks")],
        [State("table", "derived_viewport_data")],
    )
    def update_out2(n_clicks, data):
        return json.dumps(data) + " - " + str(n_clicks)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", '[{"a": "b"}] - None')
    dash_duo.wait_for_text_to_equal("#output2", "null - None")

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", '[{"a": "b"}] - 1')
    dash_duo.wait_for_text_to_equal("#output2", "null - 1")

    dash_duo.find_element(".tab:not(.tab--selected)").click()
    dash_duo.wait_for_text_to_equal("#table th", "A")
    # table props are in state so no change yet
    dash_duo.wait_for_text_to_equal("#output2", "null - 1")

    # repeat a few times, since one of the failure modes I saw during dev was
    # intermittent - but predictably so?
    for i in range(2, 10):
        expected = '[{"a": "b"}] - ' + str(i)
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#output", expected)
        # now derived props are available
        dash_duo.wait_for_text_to_equal("#output2", expected)

    assert dash_duo.get_logs() == []


def test_cbsc005_children_types(dash_duo):
    app = dash.Dash()
    app.layout = html.Div([html.Button(id="btn"), html.Div("init", id="out")])

    outputs = [
        [None, ""],
        ["a string", "a string"],
        [123, "123"],
        [123.45, "123.45"],
        [[6, 7, 8], "678"],
        [["a", "list", "of", "strings"], "alistofstrings"],
        [["strings", 2, "numbers"], "strings2numbers"],
        [["a string", html.Div("and a div")], "a string\nand a div"],
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


def test_cbsc006_array_of_objects(dash_duo):
    app = dash.Dash()
    app.layout = html.Div(
        [html.Button(id="btn"), dcc.Dropdown(id="dd"), html.Div(id="out")]
    )

    @app.callback(Output("dd", "options"), [Input("btn", "n_clicks")])
    def set_options(n):
        return [{"label": "opt{}".format(i), "value": i} for i in range(n or 0)]

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


@pytest.mark.parametrize("refresh", [False, True])
def test_cbsc007_parallel_updates(refresh, dash_duo):
    # This is a funny case, that seems to mostly happen with dcc.Location
    # but in principle could happen in other cases too:
    # A callback chain (in this case the initial hydration) is set to update a
    # value, but after that callback is queued and before it returns, that value
    # is also set explicitly from the front end (in this case Location.pathname,
    # which gets set in its componentDidMount during the render process, and
    # callbacks are delayed until after rendering is finished because of the
    # async table)
    # At one point in the wildcard PR #1103, changing from requestQueue to
    # pendingCallbacks, calling PreventUpdate in the callback would also skip
    # any callbacks that depend on pathname, despite the new front-end-provided
    # value.

    app = dash.Dash()

    app.layout = html.Div(
        [
            dcc.Location(id="loc", refresh=refresh),
            html.Button("Update path", id="btn"),
            dash_table.DataTable(id="t", columns=[{"name": "a", "id": "a"}]),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("t", "data"), [Input("loc", "pathname")])
    def set_data(path):
        return [{"a": (path or repr(path)) + ":a"}]

    @app.callback(
        Output("out", "children"), [Input("loc", "pathname"), Input("t", "data")]
    )
    def set_out(path, data):
        return json.dumps(data) + " - " + (path or repr(path))

    @app.callback(Output("loc", "pathname"), [Input("btn", "n_clicks")])
    def set_path(n):
        if not n:
            raise PreventUpdate

        return "/{0}".format(n)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", '[{"a": "/:a"}] - /')
    dash_duo.find_element("#btn").click()
    # the refresh=True case here is testing that we really do get the right
    # pathname, not the prevented default value from the layout.
    dash_duo.wait_for_text_to_equal("#out", '[{"a": "/1:a"}] - /1')
    if not refresh:
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#out", '[{"a": "/2:a"}] - /2')


def test_cbsc008_wildcard_prop_callbacks(dash_duo):
    lock = Lock()

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(
                html.Div(
                    [
                        1.5,
                        None,
                        "string",
                        html.Div(
                            id="output-1",
                            **{"data-cb": "initial value", "aria-cb": "initial value"}
                        ),
                    ]
                )
            ),
        ]
    )

    input_call_count = Value("i", 0)

    @app.callback(Output("output-1", "data-cb"), [Input("input", "value")])
    def update_data(value):
        with lock:
            input_call_count.value += 1
            return value

    @app.callback(Output("output-1", "children"), [Input("output-1", "data-cb")])
    def update_text(data):
        return data

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output-1", "initial value")
    dash_duo.percy_snapshot(name="wildcard-callback-1")

    input1 = dash_duo.find_element("#input")
    dash_duo.clear_input(input1)

    for key in "hello world":
        with lock:
            input1.send_keys(key)

    dash_duo.wait_for_text_to_equal("#output-1", "hello world")
    dash_duo.percy_snapshot(name="wildcard-callback-2")

    # an initial call, one for clearing the input
    # and one for each hello world character
    assert input_call_count.value == 2 + len("hello world")

    assert not dash_duo.get_logs()
