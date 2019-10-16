# -*- coding: UTF-8 -*-
from multiprocessing import Value

import dash_html_components as html
import dash_core_components as dcc
from dash import Dash
from dash.dependencies import Input, Output, ClientsideFunction


def test_clsd001_simple_clientside_serverside_callback(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Div(id="output-clientside"),
            html.Div(id="output-serverside"),
        ]
    )

    @app.callback(
        Output("output-serverside", "children"), [Input("input", "value")]
    )
    def update_output(value):
        return 'Server says "{}"'.format(value)

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="display"),
        Output("output-clientside", "children"),
        [Input("input", "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-serverside", 'Server says "None"')
    dash_duo.wait_for_text_to_equal(
        "#output-clientside", 'Client says "undefined"'
    )

    dash_duo.find_element("#input").send_keys("hello world")
    dash_duo.wait_for_text_to_equal(
        "#output-serverside", 'Server says "hello world"'
    )
    dash_duo.wait_for_text_to_equal(
        "#output-clientside", 'Client says "hello world"'
    )


def test_clsd002_chained_serverside_clientside_callbacks(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Label("x"),
            dcc.Input(id="x", value=3),
            html.Label("y"),
            dcc.Input(id="y", value=6),
            # clientside
            html.Label("x + y (clientside)"),
            dcc.Input(id="x-plus-y"),
            # server-side
            html.Label("x+y / 2 (serverside)"),
            dcc.Input(id="x-plus-y-div-2"),
            # server-side
            html.Div(
                [
                    html.Label("Display x, y, x+y/2 (serverside)"),
                    dcc.Textarea(id="display-all-of-the-values"),
                ]
            ),
            # clientside
            html.Label("Mean(x, y, x+y, x+y/2) (clientside)"),
            dcc.Input(id="mean-of-all-values"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction("clientside", "add"),
        Output("x-plus-y", "value"),
        [Input("x", "value"), Input("y", "value")],
    )

    call_counts = {"divide": Value("i", 0), "display": Value("i", 0)}

    @app.callback(
        Output("x-plus-y-div-2", "value"), [Input("x-plus-y", "value")]
    )
    def divide_by_two(value):
        call_counts["divide"].value += 1
        return float(value) / 2.0

    @app.callback(
        Output("display-all-of-the-values", "value"),
        [
            Input("x", "value"),
            Input("y", "value"),
            Input("x-plus-y", "value"),
            Input("x-plus-y-div-2", "value"),
        ],
    )
    def display_all(*args):
        call_counts["display"].value += 1
        return "\n".join([str(a) for a in args])

    app.clientside_callback(
        ClientsideFunction("clientside", "mean"),
        Output("mean-of-all-values", "value"),
        [
            Input("x", "value"),
            Input("y", "value"),
            Input("x-plus-y", "value"),
            Input("x-plus-y-div-2", "value"),
        ],
    )

    dash_duo.start_server(app)

    test_cases = [
        ["#x", "3"],
        ["#y", "6"],
        ["#x-plus-y", "9"],
        ["#x-plus-y-div-2", "4.5"],
        ["#display-all-of-the-values", "3\n6\n9\n4.5"],
        ["#mean-of-all-values", str((3 + 6 + 9 + 4.5) / 4.0)],
    ]
    for selector, expected in test_cases:
        dash_duo.wait_for_text_to_equal(selector, expected)

    assert call_counts["display"].value == 1
    assert call_counts["divide"].value == 1

    x_input = dash_duo.wait_for_element_by_css_selector("#x")
    x_input.send_keys("1")

    test_cases = [
        ["#x", "31"],
        ["#y", "6"],
        ["#x-plus-y", "37"],
        ["#x-plus-y-div-2", "18.5"],
        ["#display-all-of-the-values", "31\n6\n37\n18.5"],
        ["#mean-of-all-values", str((31 + 6 + 37 + 18.5) / 4.0)],
    ]
    for selector, expected in test_cases:
        dash_duo.wait_for_text_to_equal(selector, expected)

    assert call_counts["display"].value == 2
    assert call_counts["divide"].value == 2


def test_clsd003_clientside_exceptions_halt_subsequent_updates(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="first", value=1),
            dcc.Input(id="second"),
            dcc.Input(id="third"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction("clientside", "add1_break_at_11"),
        Output("second", "value"),
        [Input("first", "value")],
    )

    app.clientside_callback(
        ClientsideFunction("clientside", "add1_break_at_11"),
        Output("third", "value"),
        [Input("second", "value")],
    )

    dash_duo.start_server(app)

    test_cases = [["#first", "1"], ["#second", "2"], ["#third", "3"]]
    for selector, expected in test_cases:
        dash_duo.wait_for_text_to_equal(selector, expected)

    first_input = dash_duo.wait_for_element("#first")
    first_input.send_keys("1")
    # clientside code will prevent the update from occurring
    test_cases = [["#first", "11"], ["#second", "2"], ["#third", "3"]]
    for selector, expected in test_cases:
        dash_duo.wait_for_text_to_equal(selector, expected)

    first_input.send_keys("1")

    # the previous clientside code error should not be fatal:
    # subsequent updates should still be able to occur
    test_cases = [["#first", "111"], ["#second", "112"], ["#third", "113"]]
    for selector, expected in test_cases:
        dash_duo.wait_for_text_to_equal(selector, expected)


def test_clsd004_clientside_multiple_outputs(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="input", value=1),
            dcc.Input(id="output-1"),
            dcc.Input(id="output-2"),
            dcc.Input(id="output-3"),
            dcc.Input(id="output-4"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction("clientside", "add_to_four_outputs"),
        [
            Output("output-1", "value"),
            Output("output-2", "value"),
            Output("output-3", "value"),
            Output("output-4", "value"),
        ],
        [Input("input", "value")],
    )

    dash_duo.start_server(app)

    for selector, expected in [
        ["#input", "1"],
        ["#output-1", "2"],
        ["#output-2", "3"],
        ["#output-3", "4"],
        ["#output-4", "5"],
    ]:
        dash_duo.wait_for_text_to_equal(selector, expected)

    dash_duo.wait_for_element("#input").send_keys("1")

    for selector, expected in [
        ["#input", "11"],
        ["#output-1", "12"],
        ["#output-2", "13"],
        ["#output-3", "14"],
        ["#output-4", "15"],
    ]:
        dash_duo.wait_for_text_to_equal(selector, expected)


def test_clsd005_clientside_fails_when_returning_a_promise(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Div(id="input", children="hello"),
            html.Div(id="side-effect"),
            html.Div(id="output", children="output"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction("clientside", "side_effect_and_return_a_promise"),
        Output("output", "children"),
        [Input("input", "children")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#input", "hello")
    dash_duo.wait_for_text_to_equal("#side-effect", "side effect")
    dash_duo.wait_for_text_to_equal("#output", "output")

def test_clsd008_clientside_inline_source(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Div(id="output-clientside"),
            html.Div(id="output-serverside"),
        ]
    )

    @app.callback(
        Output("output-serverside", "children"), [Input("input", "value")]
    )
    def update_output(value):
        return 'Server says "{}"'.format(value)

    app.clientside_callback(
        ClientsideFunction(namespace="inline", function_name="display_inline"),
        Output("output-clientside", "children"),
        [Input("input", "value")],
        source="""
        function (value) {
            return 'Client says "' + value + '"';
        }
        """
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-serverside", 'Server says "None"')
    dash_duo.wait_for_text_to_equal(
        "#output-clientside", 'Client says "undefined"'
    )

    dash_duo.find_element("#input").send_keys("hello world")
    dash_duo.wait_for_text_to_equal(
        "#output-serverside", 'Server says "hello world"'
    )
    dash_duo.wait_for_text_to_equal(
        "#output-clientside", 'Client says "hello world"'
    )

def test_clsd009_clientside_inline_decorator(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="input", value=1),
            dcc.Input(id="output"),
        ]
    )

    @app.callback(
        Output("output", "value"),
        [Input("input", "value")],
        clientside=True
    )
    def add_to_four_outputs(value):
        # Interior code is JS not python so disable linting.
        # pylint: disable=all
        return parseInt(value) + 1;

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal('#input', '1')
    dash_duo.wait_for_text_to_equal('#output', '2')

    dash_duo.wait_for_element("#input").send_keys("1")

    dash_duo.wait_for_text_to_equal('#input', '11')
    dash_duo.wait_for_text_to_equal('#output', '12')
