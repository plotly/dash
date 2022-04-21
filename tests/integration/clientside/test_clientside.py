# -*- coding: UTF-8 -*-
from multiprocessing import Value, Lock

from dash import Dash, Input, Output, State, ClientsideFunction, ALL, html, dcc
from selenium.webdriver.common.keys import Keys


def test_clsd001_simple_clientside_serverside_callback(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Div(id="output-clientside"),
            html.Div(id="output-serverside"),
        ]
    )

    @app.callback(Output("output-serverside", "children"), [Input("input", "value")])
    def update_output(value):
        return 'Server says "{}"'.format(value)

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="display"),
        Output("output-clientside", "children"),
        [Input("input", "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-serverside", 'Server says "None"')
    dash_duo.wait_for_text_to_equal("#output-clientside", 'Client says "undefined"')

    dash_duo.find_element("#input").send_keys("hello world")
    dash_duo.wait_for_text_to_equal("#output-serverside", 'Server says "hello world"')
    dash_duo.wait_for_text_to_equal("#output-clientside", 'Client says "hello world"')


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

    @app.callback(Output("x-plus-y-div-2", "value"), [Input("x-plus-y", "value")])
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
        [dcc.Input(id="first", value=1), dcc.Input(id="second"), dcc.Input(id="third")]
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


def test_clsd006_PreventUpdate(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="first", value=1),
            dcc.Input(id="second", value=1),
            dcc.Input(id="third", value=1),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="add1_prevent_at_11"),
        Output("second", "value"),
        [Input("first", "value")],
        [State("second", "value")],
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="add1_prevent_at_11"),
        Output("third", "value"),
        [Input("second", "value")],
        [State("third", "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#first", "1")
    dash_duo.wait_for_text_to_equal("#second", "2")
    dash_duo.wait_for_text_to_equal("#third", "2")

    dash_duo.find_element("#first").send_keys("1")

    dash_duo.wait_for_text_to_equal("#first", "11")
    dash_duo.wait_for_text_to_equal("#second", "2")
    dash_duo.wait_for_text_to_equal("#third", "2")

    dash_duo.find_element("#first").send_keys("1")

    dash_duo.wait_for_text_to_equal("#first", "111")
    dash_duo.wait_for_text_to_equal("#second", "3")
    dash_duo.wait_for_text_to_equal("#third", "3")


def test_clsd007_no_update(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="first", value=1),
            dcc.Input(id="second", value=1),
            dcc.Input(id="third", value=1),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace="clientside", function_name="add1_no_update_at_11"
        ),
        [Output("second", "value"), Output("third", "value")],
        [Input("first", "value")],
        [State("second", "value"), State("third", "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#first", "1")
    dash_duo.wait_for_text_to_equal("#second", "2")
    dash_duo.wait_for_text_to_equal("#third", "2")

    dash_duo.find_element("#first").send_keys("1")

    dash_duo.wait_for_text_to_equal("#first", "11")
    dash_duo.wait_for_text_to_equal("#second", "2")
    dash_duo.wait_for_text_to_equal("#third", "3")

    dash_duo.find_element("#first").send_keys("1")

    dash_duo.wait_for_text_to_equal("#first", "111")
    dash_duo.wait_for_text_to_equal("#second", "3")
    dash_duo.wait_for_text_to_equal("#third", "4")


def test_clsd008_clientside_inline_source(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Div(id="output-clientside"),
            html.Div(id="output-serverside"),
        ]
    )

    @app.callback(Output("output-serverside", "children"), [Input("input", "value")])
    def update_output(value):
        return 'Server says "{}"'.format(value)

    app.clientside_callback(
        """
        function (value) {
            return 'Client says "' + value + '"';
        }
        """,
        Output("output-clientside", "children"),
        [Input("input", "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-serverside", 'Server says "None"')
    dash_duo.wait_for_text_to_equal("#output-clientside", 'Client says "undefined"')

    dash_duo.find_element("#input").send_keys("hello world")
    dash_duo.wait_for_text_to_equal("#output-serverside", 'Server says "hello world"')
    dash_duo.wait_for_text_to_equal("#output-clientside", 'Client says "hello world"')


def test_clsd009_clientside_callback_context_triggered(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Button("btn0", id="btn0"),
            html.Button("btn1:0", id={"btn1": 0}),
            html.Button("btn1:1", id={"btn1": 1}),
            html.Button("btn1:2", id={"btn1": 2}),
            html.Div(id="output-clientside", style={"font-family": "monospace"}),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="triggered_to_str"),
        Output("output-clientside", "children"),
        [Input("btn0", "n_clicks"), Input({"btn1": ALL}, "n_clicks")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-clientside", "")

    dash_duo.find_element("#btn0").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        "btn0.n_clicks = 1",
    )

    dash_duo.find_element("button[id*='btn1\":0']").click()
    dash_duo.find_element("button[id*='btn1\":0']").click()

    dash_duo.wait_for_text_to_equal("#output-clientside", '{"btn1":0}.n_clicks = 2')

    dash_duo.find_element("button[id*='btn1\":2']").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        '{"btn1":2}.n_clicks = 1',
    )


def test_clsd010_clientside_callback_context_inputs(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Button("btn0", id="btn0"),
            html.Button("btn1:0", id={"btn1": 0}),
            html.Button("btn1:1", id={"btn1": 1}),
            html.Button("btn1:2", id={"btn1": 2}),
            html.Div(id="output-clientside", style={"font-family": "monospace"}),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="inputs_to_str"),
        Output("output-clientside", "children"),
        [Input("btn0", "n_clicks"), Input({"btn1": ALL}, "n_clicks")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "btn0.n_clicks = null, "
            '{"btn1":0}.n_clicks = null, '
            '{"btn1":1}.n_clicks = null, '
            '{"btn1":2}.n_clicks = null'
        ),
    )

    dash_duo.find_element("#btn0").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "btn0.n_clicks = 1, "
            '{"btn1":0}.n_clicks = null, '
            '{"btn1":1}.n_clicks = null, '
            '{"btn1":2}.n_clicks = null'
        ),
    )

    dash_duo.find_element("button[id*='btn1\":0']").click()
    dash_duo.find_element("button[id*='btn1\":0']").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "btn0.n_clicks = 1, "
            '{"btn1":0}.n_clicks = 2, '
            '{"btn1":1}.n_clicks = null, '
            '{"btn1":2}.n_clicks = null'
        ),
    )

    dash_duo.find_element("button[id*='btn1\":2']").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "btn0.n_clicks = 1, "
            '{"btn1":0}.n_clicks = 2, '
            '{"btn1":1}.n_clicks = null, '
            '{"btn1":2}.n_clicks = 1'
        ),
    )


def test_clsd011_clientside_callback_context_inputs_list(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Button("btn0", id="btn0"),
            html.Button("btn1:0", id={"btn1": 0}),
            html.Button("btn1:1", id={"btn1": 1}),
            html.Button("btn1:2", id={"btn1": 2}),
            html.Div(id="output-clientside", style={"font-family": "monospace"}),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="inputs_list_to_str"),
        Output("output-clientside", "children"),
        [Input("btn0", "n_clicks"), Input({"btn1": ALL}, "n_clicks")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"btn0","property":"n_clicks"},'
            '[{"id":{"btn1":0},"property":"n_clicks"},'
            '{"id":{"btn1":1},"property":"n_clicks"},'
            '{"id":{"btn1":2},"property":"n_clicks"}]]'
        ),
    )

    dash_duo.find_element("#btn0").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"btn0","property":"n_clicks","value":1},'
            '[{"id":{"btn1":0},"property":"n_clicks"},'
            '{"id":{"btn1":1},"property":"n_clicks"},'
            '{"id":{"btn1":2},"property":"n_clicks"}]]'
        ),
    )

    dash_duo.find_element("button[id*='btn1\":0']").click()
    dash_duo.find_element("button[id*='btn1\":0']").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"btn0","property":"n_clicks","value":1},'
            '[{"id":{"btn1":0},"property":"n_clicks","value":2},'
            '{"id":{"btn1":1},"property":"n_clicks"},'
            '{"id":{"btn1":2},"property":"n_clicks"}]]'
        ),
    )

    dash_duo.find_element("button[id*='btn1\":2']").click()

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"btn0","property":"n_clicks","value":1},'
            '[{"id":{"btn1":0},"property":"n_clicks","value":2},'
            '{"id":{"btn1":1},"property":"n_clicks"},'
            '{"id":{"btn1":2},"property":"n_clicks","value":1}]]'
        ),
    )


def test_clsd012_clientside_callback_context_states(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="in0"),
            dcc.Input(id={"in1": 0}),
            dcc.Input(id={"in1": 1}),
            dcc.Input(id={"in1": 2}),
            html.Div(id="output-clientside", style={"font-family": "monospace"}),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="states_to_str"),
        Output("output-clientside", "children"),
        [Input("in0", "n_submit"), Input({"in1": ALL}, "n_submit")],
        [State("in0", "value"), State({"in1": ALL}, "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "in0.value = null, "
            '{"in1":0}.value = null, '
            '{"in1":1}.value = null, '
            '{"in1":2}.value = null'
        ),
    )

    dash_duo.find_element("#in0").send_keys("test 0" + Keys.RETURN)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "in0.value = test 0, "
            '{"in1":0}.value = null, '
            '{"in1":1}.value = null, '
            '{"in1":2}.value = null'
        ),
    )

    dash_duo.find_element("input[id*='in1\":0']").send_keys("test 1" + Keys.RETURN)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "in0.value = test 0, "
            '{"in1":0}.value = test 1, '
            '{"in1":1}.value = null, '
            '{"in1":2}.value = null'
        ),
    )

    dash_duo.find_element("input[id*='in1\":2']").send_keys("test 2" + Keys.RETURN)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            "in0.value = test 0, "
            '{"in1":0}.value = test 1, '
            '{"in1":1}.value = null, '
            '{"in1":2}.value = test 2'
        ),
    )


def test_clsd013_clientside_callback_context_states_list(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            dcc.Input(id="in0"),
            dcc.Input(id={"in1": 0}),
            dcc.Input(id={"in1": 1}),
            dcc.Input(id={"in1": 2}),
            html.Div(id="output-clientside", style={"font-family": "monospace"}),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="states_list_to_str"),
        Output("output-clientside", "children"),
        [Input("in0", "n_submit"), Input({"in1": ALL}, "n_submit")],
        [State("in0", "value"), State({"in1": ALL}, "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"in0","property":"value"},'
            '[{"id":{"in1":0},"property":"value"},'
            '{"id":{"in1":1},"property":"value"},'
            '{"id":{"in1":2},"property":"value"}]]'
        ),
    )

    dash_duo.find_element("#in0").send_keys("test 0" + Keys.RETURN)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"in0","property":"value","value":"test 0"},'
            '[{"id":{"in1":0},"property":"value"},'
            '{"id":{"in1":1},"property":"value"},'
            '{"id":{"in1":2},"property":"value"}]]'
        ),
    )

    dash_duo.find_element("input[id*='in1\":0']").send_keys("test 1" + Keys.RETURN)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"in0","property":"value","value":"test 0"},'
            '[{"id":{"in1":0},"property":"value","value":"test 1"},'
            '{"id":{"in1":1},"property":"value"},'
            '{"id":{"in1":2},"property":"value"}]]'
        ),
    )

    dash_duo.find_element("input[id*='in1\":2']").send_keys("test 2" + Keys.RETURN)

    dash_duo.wait_for_text_to_equal(
        "#output-clientside",
        (
            '[{"id":"in0","property":"value","value":"test 0"},'
            '[{"id":{"in1":0},"property":"value","value":"test 1"},'
            '{"id":{"in1":1},"property":"value"},'
            '{"id":{"in1":2},"property":"value","value":"test 2"}]]'
        ),
    )


def test_clsd014_input_output_callback(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [html.Div(id="input-text"), dcc.Input(id="input", type="number", value=0)]
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace="clientside", function_name="input_output_callback"
        ),
        Output("input", "value"),
        Input("input", "value"),
    )

    app.clientside_callback(
        ClientsideFunction(
            namespace="clientside", function_name="input_output_follower"
        ),
        Output("input-text", "children"),
        Input("input", "value"),
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#input").send_keys("2")
    dash_duo.wait_for_text_to_equal("#input-text", "3")
    call_count = dash_duo.driver.execute_script("return window.callCount;")

    assert call_count == 2, "initial + changed once"

    assert dash_duo.get_logs() == []


def test_clsd015_clientside_chained_callbacks_returning_promise(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Div(id="input", children=["initial"]),
            html.Div(id="div-1"),
            html.Div(id="div-2"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="chained_promise"),
        Output("div-1", "children"),
        Input("input", "children"),
    )

    @app.callback(Output("div-2", "children"), Input("div-1", "children"))
    def callback(value):
        return value + "-twice"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#div-1", "initial-chained")
    dash_duo.wait_for_text_to_equal("#div-2", "initial-chained-twice")


def test_clsd016_serverside_clientside_shared_input_with_promise(dash_duo):
    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Div(id="input", children=["initial"]),
            html.Div(id="clientside-div"),
            html.Div(id="serverside-div"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="delayed_promise"),
        Output("clientside-div", "children"),
        Input("input", "children"),
    )

    @app.callback(Output("serverside-div", "children"), Input("input", "children"))
    def callback(value):
        return "serverside-" + value[0]

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#serverside-div", "serverside-initial")
    dash_duo.driver.execute_script("window.callbackDone('deferred')")
    dash_duo.wait_for_text_to_equal("#clientside-div", "clientside-initial-deferred")


def test_clsd017_clientside_serverside_shared_input_with_promise(dash_duo):
    lock = Lock()
    lock.acquire()

    app = Dash(__name__, assets_folder="assets")

    app.layout = html.Div(
        [
            html.Div(id="input", children=["initial"]),
            html.Div(id="clientside-div"),
            html.Div(id="serverside-div"),
        ]
    )

    app.clientside_callback(
        ClientsideFunction(namespace="clientside", function_name="non_delayed_promise"),
        Output("clientside-div", "children"),
        Input("input", "children"),
    )

    @app.callback(Output("serverside-div", "children"), Input("input", "children"))
    def callback(value):
        with lock:
            return "serverside-" + value[0] + "-deferred"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#clientside-div", "clientside-initial")
    lock.release()
    dash_duo.wait_for_text_to_equal("#serverside-div", "serverside-initial-deferred")


def test_clsd018_clientside_inline_async_function(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(id="input", children=["initial"]),
            html.Div(id="output-div"),
        ]
    )

    app.clientside_callback(
        """
        async function(input) {
            return input + "-inline";
        }
        """,
        Output("output-div", "children"),
        Input("input", "children"),
    )

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output-div", "initial-inline")


def test_clsd019_clientside_inline_promise(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(id="input", children=["initial"]),
            html.Div(id="output-div"),
        ]
    )

    app.clientside_callback(
        """
        function(inputValue) {
            return new Promise(function (resolve) {
                resolve(inputValue + "-inline");
            });
        }
        """,
        Output("output-div", "children"),
        Input("input", "children"),
    )

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output-div", "initial-inline")
