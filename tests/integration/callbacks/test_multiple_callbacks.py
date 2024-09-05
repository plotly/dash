import time
from multiprocessing import Value, Lock

import pytest

from dash import Dash, Input, Output, State, callback_context, html, dcc, dash_table
from dash.exceptions import PreventUpdate

import dash.testing.wait as wait


def test_cbmt001_called_multiple_times_and_out_of_order(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("Click", id="input", n_clicks=0), html.Div(id="output")]
    )

    call_count = Value("i", 0)

    @app.callback(Output("output", "children"), [Input("input", "n_clicks")])
    def update_output(n_clicks):
        call_count.value += 1
        if n_clicks == 1:
            time.sleep(1)
        return n_clicks

    dash_duo.start_server(app)
    dash_duo.multiple_click("#input", clicks=3)

    time.sleep(3)

    assert call_count.value == 4, "get called 4 times"
    assert dash_duo.find_element("#output").text == "3", "clicked button 3 times"

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_cbmt002_canceled_intermediate_callback(dash_duo):
    # see https://github.com/plotly/dash/issues/1053
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="a", value="x"),
            html.Div("b", id="b"),
            html.Div("c", id="c"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        [Input("a", "value"), Input("b", "children"), Input("c", "children")],
    )
    def set_out(a, b, c):
        return "{}/{}/{}".format(a, b, c)

    @app.callback(Output("b", "children"), [Input("a", "value")])
    def set_b(a):
        raise PreventUpdate

    @app.callback(Output("c", "children"), [Input("a", "value")])
    def set_c(a):
        return a

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "x/b/x")
    chars = "x"
    for i in list(range(10)) * 2:
        dash_duo.find_element("#a").send_keys(str(i))
        chars += str(i)
        dash_duo.wait_for_text_to_equal("#out", "{0}/b/{0}".format(chars))


def test_cbmt003_chain_with_table(dash_duo):
    # see https://github.com/plotly/dash/issues/1071
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="a1"),
            html.Div(id="a2"),
            html.Div(id="b1"),
            html.H1(id="b2"),
            html.Button("Update", id="button"),
            dash_table.DataTable(id="table"),
        ]
    )

    @app.callback(
        # Changing the order of outputs here fixes the issue
        [Output("a2", "children"), Output("a1", "children")],
        [Input("button", "n_clicks")],
    )
    def a12(n):
        return "a2: {!s}".format(n), "a1: {!s}".format(n)

    @app.callback(Output("b1", "children"), [Input("a1", "children")])
    def b1(a1):
        return "b1: '{!s}'".format(a1)

    @app.callback(
        Output("b2", "children"),
        [Input("a2", "children"), Input("table", "selected_cells")],
    )
    def b2(a2, selected_cells):
        return "b2: '{!s}', {!s}".format(a2, selected_cells)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#a1", "a1: None")
    dash_duo.wait_for_text_to_equal("#a2", "a2: None")
    dash_duo.wait_for_text_to_equal("#b1", "b1: 'a1: None'")
    dash_duo.wait_for_text_to_equal("#b2", "b2: 'a2: None', None")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#a1", "a1: 1")
    dash_duo.wait_for_text_to_equal("#a2", "a2: 1")
    dash_duo.wait_for_text_to_equal("#b1", "b1: 'a1: 1'")
    dash_duo.wait_for_text_to_equal("#b2", "b2: 'a2: 1', None")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#a1", "a1: 2")
    dash_duo.wait_for_text_to_equal("#a2", "a2: 2")
    dash_duo.wait_for_text_to_equal("#b1", "b1: 'a1: 2'")
    dash_duo.wait_for_text_to_equal("#b2", "b2: 'a2: 2', None")


@pytest.mark.parametrize("MULTI", [False, True])
def test_cbmt004_chain_with_sliders(MULTI, dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Button", id="button"),
            html.Div(
                [
                    html.Label(id="label1"),
                    dcc.Slider(id="slider1", min=0, max=10, value=0),
                ]
            ),
            html.Div(
                [
                    html.Label(id="label2"),
                    dcc.Slider(id="slider2", min=0, max=10, value=0),
                ]
            ),
        ]
    )

    if MULTI:

        @app.callback(
            [Output("slider1", "value"), Output("slider2", "value")],
            [Input("button", "n_clicks")],
        )
        def update_slider_vals(n):
            if not n:
                raise PreventUpdate
            return n, n

    else:

        @app.callback(Output("slider1", "value"), [Input("button", "n_clicks")])
        def update_slider1_val(n):
            if not n:
                raise PreventUpdate
            return n

        @app.callback(Output("slider2", "value"), [Input("button", "n_clicks")])
        def update_slider2_val(n):
            if not n:
                raise PreventUpdate
            return n

    @app.callback(Output("label1", "children"), [Input("slider1", "value")])
    def update_slider1_label(val):
        return "Slider1 value {}".format(val)

    @app.callback(Output("label2", "children"), [Input("slider2", "value")])
    def update_slider2_label(val):
        return "Slider2 value {}".format(val)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#label1", "")
    dash_duo.wait_for_text_to_equal("#label2", "")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#label1", "Slider1 value 1")
    dash_duo.wait_for_text_to_equal("#label2", "Slider2 value 1")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#label1", "Slider1 value 2")
    dash_duo.wait_for_text_to_equal("#label2", "Slider2 value 2")


def test_cbmt005_multi_converging_chain(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Button 1", id="b1"),
            html.Button("Button 2", id="b2"),
            dcc.Slider(id="slider1", min=-5, max=5),
            dcc.Slider(id="slider2", min=-5, max=5),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        [Output("slider1", "value"), Output("slider2", "value")],
        [Input("b1", "n_clicks"), Input("b2", "n_clicks")],
    )
    def update_sliders(button1, button2):
        if not callback_context.triggered:
            raise PreventUpdate

        if callback_context.triggered[0]["prop_id"] == "b1.n_clicks":
            return -1, -1
        else:
            return 1, 1

    @app.callback(
        Output("out", "children"),
        [Input("slider1", "value"), Input("slider2", "value")],
    )
    def update_graph(s1, s2):
        return "x={}, y={}".format(s1, s2)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "")

    dash_duo.find_element("#b1").click()
    dash_duo.wait_for_text_to_equal("#out", "x=-1, y=-1")

    dash_duo.find_element("#b2").click()
    dash_duo.wait_for_text_to_equal("#out", "x=1, y=1")


def test_cbmt006_derived_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Div(id="output"), html.Button("click", id="btn"), dcc.Store(id="store")]
    )

    @app.callback(
        Output("output", "children"),
        [Input("store", "modified_timestamp")],
        [State("store", "data")],
    )
    def on_data(ts, data):
        return data

    @app.callback(Output("store", "data"), [Input("btn", "n_clicks")])
    def on_click(n_clicks):
        return n_clicks or 0

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "1")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "2")


def test_cbmt007_early_preventupdate_inputs_above_below(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(id="content")

    @app.callback(Output("content", "children"), [Input("content", "style")])
    def content(_):
        return html.Div(
            [
                html.Div(42, id="above-in"),
                html.Div(id="above-dummy"),
                html.Hr(),
                html.Div(0, id="above-out"),
                html.Div(0, id="below-out"),
                html.Hr(),
                html.Div(id="below-dummy"),
                html.Div(44, id="below-in"),
            ]
        )

    # Create 4 callbacks - 2 above, 2 below.
    for pos in ("above", "below"):

        @app.callback(
            Output("{}-dummy".format(pos), "children"),
            [Input("{}-dummy".format(pos), "style")],
        )
        def dummy(_):
            raise PreventUpdate

        @app.callback(
            Output("{}-out".format(pos), "children"),
            [Input("{}-in".format(pos), "children")],
        )
        def out(v):
            return v

    dash_duo.start_server(app)

    # as of https://github.com/plotly/dash/issues/1223, above-out would be 0
    dash_duo.wait_for_text_to_equal("#above-out", "42")
    dash_duo.wait_for_text_to_equal("#below-out", "44")


def test_cbmt008_direct_chain(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="input-1", value="input 1"),
            dcc.Input(id="input-2"),
            html.Div("test", id="output"),
        ]
    )

    call_counts = {"output": Value("i", 0), "input-2": Value("i", 0)}

    @app.callback(Output("input-2", "value"), Input("input-1", "value"))
    def update_input(input1):
        call_counts["input-2"].value += 1
        return "<<{}>>".format(input1)

    @app.callback(
        Output("output", "children"),
        Input("input-1", "value"),
        Input("input-2", "value"),
    )
    def update_output(input1, input2):
        call_counts["output"].value += 1
        return "{} + {}".format(input1, input2)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#input-1", "input 1")
    dash_duo.wait_for_text_to_equal("#input-2", "<<input 1>>")
    dash_duo.wait_for_text_to_equal("#output", "input 1 + <<input 1>>")
    assert call_counts["output"].value == 1
    assert call_counts["input-2"].value == 1

    dash_duo.find_element("#input-1").send_keys("x")
    dash_duo.wait_for_text_to_equal("#input-1", "input 1x")
    dash_duo.wait_for_text_to_equal("#input-2", "<<input 1x>>")
    dash_duo.wait_for_text_to_equal("#output", "input 1x + <<input 1x>>")
    assert call_counts["output"].value == 2
    assert call_counts["input-2"].value == 2

    dash_duo.find_element("#input-2").send_keys("y")
    dash_duo.wait_for_text_to_equal("#input-2", "<<input 1x>>y")
    dash_duo.wait_for_text_to_equal("#output", "input 1x + <<input 1x>>y")
    dash_duo.wait_for_text_to_equal("#input-1", "input 1x")
    assert call_counts["output"].value == 3
    assert call_counts["input-2"].value == 2


def test_cbmt009_branched_chain(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="grandparent", value="input 1"),
            dcc.Input(id="parent-a"),
            dcc.Input(id="parent-b"),
            html.Div(id="child-a"),
            html.Div(id="child-b"),
        ]
    )
    call_counts = {
        "parent-a": Value("i", 0),
        "parent-b": Value("i", 0),
        "child-a": Value("i", 0),
        "child-b": Value("i", 0),
    }

    @app.callback(Output("parent-a", "value"), Input("grandparent", "value"))
    def update_parenta(value):
        call_counts["parent-a"].value += 1
        return "a: {}".format(value)

    @app.callback(Output("parent-b", "value"), Input("grandparent", "value"))
    def update_parentb(value):
        time.sleep(0.2)
        call_counts["parent-b"].value += 1
        return "b: {}".format(value)

    @app.callback(
        Output("child-a", "children"),
        Input("parent-a", "value"),
        Input("parent-b", "value"),
    )
    def update_childa(parenta_value, parentb_value):
        time.sleep(0.5)
        call_counts["child-a"].value += 1
        return "{} + {}".format(parenta_value, parentb_value)

    @app.callback(
        Output("child-b", "children"),
        Input("parent-a", "value"),
        Input("parent-b", "value"),
        Input("grandparent", "value"),
    )
    def update_childb(parenta_value, parentb_value, grandparent_value):
        call_counts["child-b"].value += 1
        return "{} + {} + {}".format(parenta_value, parentb_value, grandparent_value)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#child-a", "a: input 1 + b: input 1")
    dash_duo.wait_for_text_to_equal("#child-b", "a: input 1 + b: input 1 + input 1")
    dash_duo.wait_for_text_to_equal("#parent-a", "a: input 1")
    dash_duo.wait_for_text_to_equal("#parent-b", "b: input 1")
    assert call_counts["parent-a"].value == 1
    assert call_counts["parent-b"].value == 1
    assert call_counts["child-a"].value == 1
    assert call_counts["child-b"].value == 1


def test_cbmt010_shared_grandparent(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div("id", id="session-id"),
            dcc.Dropdown(id="dropdown-1"),
            dcc.Dropdown(id="dropdown-2"),
            html.Div(id="output"),
        ]
    )

    options = [{"value": "a", "label": "a"}]

    call_counts = {"dropdown_1": Value("i", 0), "dropdown_2": Value("i", 0)}

    @app.callback(
        Output("dropdown-1", "options"),
        [Input("dropdown-1", "value"), Input("session-id", "children")],
    )
    def dropdown_1(value, session_id):
        call_counts["dropdown_1"].value += 1
        return options

    @app.callback(
        Output("dropdown-2", "options"),
        Input("dropdown-2", "value"),
        Input("session-id", "children"),
    )
    def dropdown_2(value, session_id):
        call_counts["dropdown_2"].value += 1
        return options

    @app.callback(
        Output("output", "children"),
        Input("dropdown-1", "value"),
        Input("dropdown-2", "value"),
    )
    def set_output(v1, v2):
        return (v1 or "b") + (v2 or "b")

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "bb")
    assert call_counts["dropdown_1"].value == 1
    assert call_counts["dropdown_2"].value == 1

    assert not dash_duo.get_logs()


def test_cbmt011_callbacks_triggered_on_generated_output(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)

    call_counts = {"tab1": Value("i", 0), "tab2": Value("i", 0)}

    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="outer-controls",
                options=[{"label": i, "value": i} for i in ["a", "b"]],
                value="a",
            ),
            dcc.RadioItems(
                options=[
                    {"label": "Tab 1", "value": 1},
                    {"label": "Tab 2", "value": 2},
                ],
                value=1,
                id="tabs",
            ),
            html.Div(id="tab-output"),
        ]
    )

    @app.callback(Output("tab-output", "children"), Input("tabs", "value"))
    def display_content(value):
        return html.Div([html.Div(id="tab-{}-output".format(value))])

    @app.callback(Output("tab-1-output", "children"), Input("outer-controls", "value"))
    def display_tab1_output(value):
        call_counts["tab1"].value += 1
        return 'Selected "{}" in tab 1'.format(value)

    @app.callback(Output("tab-2-output", "children"), Input("outer-controls", "value"))
    def display_tab2_output(value):
        call_counts["tab2"].value += 1
        return 'Selected "{}" in tab 2'.format(value)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#tab-output", 'Selected "a" in tab 1')
    dash_duo.wait_for_text_to_equal("#tab-1-output", 'Selected "a" in tab 1')
    assert call_counts["tab1"].value == 1
    assert call_counts["tab2"].value == 0

    dash_duo.find_elements('input[type="radio"]')[1].click()

    dash_duo.wait_for_text_to_equal("#tab-output", 'Selected "a" in tab 2')
    dash_duo.wait_for_text_to_equal("#tab-2-output", 'Selected "a" in tab 2')
    assert call_counts["tab1"].value == 1
    assert call_counts["tab2"].value == 1

    assert not dash_duo.get_logs()


@pytest.mark.parametrize("generate", [False, True])
def test_cbmt012_initialization_with_overlapping_outputs(generate, dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=generate)
    block = html.Div(
        [
            html.Div(id="input-1", children="input-1"),
            html.Div(id="input-2", children="input-2"),
            html.Div(id="input-3", children="input-3"),
            html.Div(id="input-4", children="input-4"),
            html.Div(id="input-5", children="input-5"),
            html.Div(id="output-1"),
            html.Div(id="output-2"),
            html.Div(id="output-3"),
            html.Div(id="output-4"),
        ]
    )

    call_counts = {
        "container": Value("i", 0),
        "output-1": Value("i", 0),
        "output-2": Value("i", 0),
        "output-3": Value("i", 0),
        "output-4": Value("i", 0),
    }

    if generate:
        app.layout = html.Div([html.Div(id="input"), html.Div(id="container")])

        @app.callback(Output("container", "children"), Input("input", "children"))
        def set_content(_):
            call_counts["container"].value += 1
            return block

    else:
        app.layout = block

    def generate_callback(outputid):
        def callback(*args):
            call_counts[outputid].value += 1
            return "{}, {}".format(*args)

        return callback

    for i in range(1, 5):
        outputid = "output-{}".format(i)
        app.callback(
            Output(outputid, "children"),
            Input("input-{}".format(i), "children"),
            Input("input-{}".format(i + 1), "children"),
        )(generate_callback(outputid))

    dash_duo.start_server(app)

    for i in range(1, 5):
        outputid = "output-{}".format(i)
        dash_duo.wait_for_text_to_equal(
            "#{}".format(outputid), "input-{}, input-{}".format(i, i + 1)
        )
        assert call_counts[outputid].value == 1

    assert call_counts["container"].value == (1 if generate else 0)


def test_cbmt013_chained_callback_should_be_blocked(dash_duo):
    all_options = {
        "America": ["New York City", "San Francisco", "Cincinnati"],
        "Canada": ["Montreal", "Toronto", "Ottawa"],
    }

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RadioItems(
                id="countries-radio",
                options=[{"label": k, "value": k} for k in all_options.keys()],
                value="America",
            ),
            html.Hr(),
            dcc.RadioItems(id="cities-radio"),
            html.Hr(),
            html.Div(id="display-selected-values"),
        ]
    )

    opts_call_count = Value("i", 0)
    city_call_count = Value("i", 0)
    out_call_count = Value("i", 0)
    out_lock = Lock()

    @app.callback(Output("cities-radio", "options"), Input("countries-radio", "value"))
    def set_cities_options(selected_country):
        opts_call_count.value += 1
        return [{"label": i, "value": i} for i in all_options[selected_country]]

    @app.callback(Output("cities-radio", "value"), Input("cities-radio", "options"))
    def set_cities_value(available_options):
        city_call_count.value += 1
        return available_options[0]["value"]

    @app.callback(
        Output("display-selected-values", "children"),
        Input("countries-radio", "value"),
        Input("cities-radio", "value"),
    )
    def set_display_children(selected_country, selected_city):
        # this may actually be the key to this whole test:
        # these inputs should never be out of sync.
        assert selected_city in all_options[selected_country]

        out_call_count.value += 1
        with out_lock:
            return "{} is a city in {}".format(
                selected_city,
                selected_country,
            )

    dash_duo.start_server(app)

    new_york_text = "New York City is a city in America"
    canada_text = "Montreal is a city in Canada"

    # If we get to the correct initial state with only one call of each callback,
    # then there mustn't have been any intermediate changes to the output text
    dash_duo.wait_for_text_to_equal("#display-selected-values", new_york_text)
    assert opts_call_count.value == 1
    assert city_call_count.value == 1
    assert out_call_count.value == 1

    all_labels = dash_duo.find_elements("label")
    canada_opt = next(
        i for i in all_labels if i.text == "Canada"
    ).find_element_by_tag_name("input")

    with out_lock:
        canada_opt.click()

        # all three callbacks have fired once more, but since we haven't allowed the
        # last one to execute, the output hasn't been changed
        wait.until(lambda: out_call_count.value == 2, timeout=3)
        assert opts_call_count.value == 2
        assert city_call_count.value == 2
        assert dash_duo.find_element("#display-selected-values").text == new_york_text

    dash_duo.wait_for_text_to_equal("#display-selected-values", canada_text)
    assert opts_call_count.value == 2
    assert city_call_count.value == 2
    assert out_call_count.value == 2

    assert dash_duo.get_logs() == []
