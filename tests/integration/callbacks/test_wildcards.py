import pytest
import re
import threading
from selenium.webdriver.common.keys import Keys
import json
from multiprocessing import Lock

from dash.testing import wait
import dash
from dash import (
    Dash,
    Input,
    Output,
    State,
    ALL,
    ALLSMALLER,
    MATCH,
    html,
    dcc,
    Patch,
    set_props,
)

from tests.assets.todo_app import todo_app
from tests.assets.grouping_app import grouping_app


def stringify_id(id_):
    if isinstance(id_, dict):
        return json.dumps(id_, sort_keys=True, separators=(",", ":"))
    return id_


def css_escape(s):
    sel = re.sub("[\\{\\}\\\"\\'.:,]", lambda m: "\\" + m.group(0), s)
    print(sel)
    return sel


@pytest.mark.parametrize("content_callback", (False, True))
def test_cbwc001_todo_app(content_callback, dash_duo):
    app = todo_app(content_callback)
    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#totals", "0 of 0 items completed")
    assert app.list_calls.value == 1
    assert app.style_calls.value == 0
    assert app.preceding_calls.value == 0
    assert app.total_calls.value == 1

    new_item = dash_duo.find_element("#new-item")
    add_item = dash_duo.find_element("#add")
    clear_done = dash_duo.find_element("#clear-done")

    def assert_count(items):
        assert len(dash_duo.find_elements("#list-container>div")) == items

    def get_done_item(item):
        selector = css_escape('#{"action":"done","item":%d} input' % item)
        return dash_duo.find_element(selector)

    def assert_item(item, text, done, prefix="", suffix=""):
        dash_duo.wait_for_text_to_equal(css_escape('#{"item":%d}' % item), text)

        expected_note = "" if done else (prefix + " preceding items are done" + suffix)
        dash_duo.wait_for_text_to_equal(
            css_escape('#{"item":%d,"preceding":true}' % item), expected_note
        )

        assert bool(get_done_item(item).get_attribute("checked")) == done

    new_item.send_keys("apples")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 1 items completed - 0%")
    assert_count(1)

    new_item.send_keys("bananas")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 2 items completed - 0%")
    assert_count(2)

    new_item.send_keys("carrots")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 3 items completed - 0%")
    assert_count(3)

    new_item.send_keys("dates")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 4 items completed - 0%")
    assert_count(4)
    assert_item(0, "apples", False, "0 of 0", " DO THIS NEXT!")
    assert_item(1, "bananas", False, "0 of 1")
    assert_item(2, "carrots", False, "0 of 2")
    assert_item(3, "dates", False, "0 of 3")

    get_done_item(2).click()
    dash_duo.wait_for_text_to_equal("#totals", "1 of 4 items completed - 25%")
    assert_item(0, "apples", False, "0 of 0", " DO THIS NEXT!")
    assert_item(1, "bananas", False, "0 of 1")
    assert_item(2, "carrots", True)
    assert_item(3, "dates", False, "1 of 3")

    get_done_item(0).click()
    dash_duo.wait_for_text_to_equal("#totals", "2 of 4 items completed - 50%")
    assert_item(0, "apples", True)
    assert_item(1, "bananas", False, "1 of 1", " DO THIS NEXT!")
    assert_item(2, "carrots", True)
    assert_item(3, "dates", False, "2 of 3")

    clear_done.click()
    dash_duo.wait_for_text_to_equal("#totals", "0 of 2 items completed - 0%")
    assert_count(2)
    assert_item(0, "bananas", False, "0 of 0", " DO THIS NEXT!")
    assert_item(1, "dates", False, "0 of 1")

    get_done_item(0).click()
    dash_duo.wait_for_text_to_equal("#totals", "1 of 2 items completed - 50%")
    assert_item(0, "bananas", True)
    assert_item(1, "dates", False, "1 of 1", " DO THIS NEXT!")

    get_done_item(1).click()
    dash_duo.wait_for_text_to_equal("#totals", "2 of 2 items completed - 100%")
    assert_item(0, "bananas", True)
    assert_item(1, "dates", True)

    clear_done.click()
    # This was a tricky one - trigger based on deleted components
    dash_duo.wait_for_text_to_equal("#totals", "0 of 0 items completed")
    assert_count(0)


fibonacci_count = 0
fibonacci_sum_count = 0


def fibonacci_app(clientside):
    global fibonacci_count
    global fibonacci_sum_count

    fibonacci_count = 0
    fibonacci_sum_count = 0

    # This app tests 2 things in particular:
    # - clientside callbacks work the same as server-side
    # - callbacks using ALLSMALLER as an input to MATCH of the exact same id/prop
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="n", type="number", min=0, max=10, value=4),
            html.Div(id="series"),
            html.Div(id="sum"),
        ]
    )

    @app.callback(Output("series", "children"), Input("n", "value"))
    def items(n):
        return [html.Div(id={"i": i}) for i in range(n)]

    if clientside:
        app.clientside_callback(
            """
            function(vals) {
                var len = vals.length;
                return len < 2 ? len : +(vals[len - 1] || 0) + +(vals[len - 2] || 0);
            }
            """,
            Output({"i": MATCH}, "children"),
            Input({"i": ALLSMALLER}, "children"),
        )

        app.clientside_callback(
            """
            function(vals) {
                var sum = vals.reduce(function(a, b) { return +a + +b; }, 0);
                return vals.length + ' elements, sum: ' + sum;
            }
            """,
            Output("sum", "children"),
            Input({"i": ALL}, "children"),
        )

    else:

        @app.callback(
            Output({"i": MATCH}, "children"), Input({"i": ALLSMALLER}, "children")
        )
        def sequence(prev):
            global fibonacci_count
            fibonacci_count = fibonacci_count + 1
            print(fibonacci_count)

            if len(prev) < 2:
                return len(prev)
            return int(prev[-1] or 0) + int(prev[-2] or 0)

        @app.callback(Output("sum", "children"), Input({"i": ALL}, "children"))
        def show_sum(seq):
            global fibonacci_sum_count
            fibonacci_sum_count = fibonacci_sum_count + 1
            print("fibonacci_sum_count: ", fibonacci_sum_count)

            return "{} elements, sum: {}".format(
                len(seq), sum(int(v or 0) for v in seq)
            )

    return app


@pytest.mark.parametrize("clientside", (False, True))
def test_cbwc002_fibonacci_app(clientside, dash_duo):
    app = fibonacci_app(clientside)
    dash_duo.start_server(app)

    # app starts with 4 elements: 0, 1, 1, 2
    dash_duo.wait_for_text_to_equal("#sum", "4 elements, sum: 4")

    # add 5th item, "3"
    dash_duo.find_element("#n").send_keys(Keys.UP)
    dash_duo.wait_for_text_to_equal("#sum", "5 elements, sum: 7")

    # add 6th item, "5"
    dash_duo.find_element("#n").send_keys(Keys.UP)
    dash_duo.wait_for_text_to_equal("#sum", "6 elements, sum: 12")

    # add 7th item, "8"
    dash_duo.find_element("#n").send_keys(Keys.UP)
    dash_duo.wait_for_text_to_equal("#sum", "7 elements, sum: 20")

    # back down all the way to no elements
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "6 elements, sum: 12")
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "5 elements, sum: 7")
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "4 elements, sum: 4")
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "3 elements, sum: 2")
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "2 elements, sum: 1")
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "1 elements, sum: 0")
    dash_duo.find_element("#n").send_keys(Keys.DOWN)
    dash_duo.wait_for_text_to_equal("#sum", "0 elements, sum: 0")


def test_cbwc003_same_keys(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button("Add Filter", id="add-filter", n_clicks=0),
            html.Div(id="container", children=[]),
        ]
    )

    @app.callback(
        Output("container", "children"),
        [Input("add-filter", "n_clicks")],
        [State("container", "children")],
    )
    def display_dropdowns(n_clicks, children):
        new_element = html.Div(
            [
                dcc.Dropdown(
                    id={"type": "dropdown", "index": n_clicks},
                    options=[
                        {"label": i, "value": i} for i in ["NYC", "MTL", "LA", "TOKYO"]
                    ],
                ),
                html.Div(id={"type": "output", "index": n_clicks}),
            ]
        )
        return children + [new_element]

    @app.callback(
        Output({"type": "output", "index": MATCH}, "children"),
        [Input({"type": "dropdown", "index": MATCH}, "value")],
        [State({"type": "dropdown", "index": MATCH}, "id")],
    )
    def display_output(value, id):
        return html.Div("Dropdown {} = {}".format(id["index"], value))

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#add-filter", "Add Filter")
    dash_duo.select_dcc_dropdown(
        '#\\{\\"index\\"\\:0\\,\\"type\\"\\:\\"dropdown\\"\\}', "LA"
    )
    dash_duo.wait_for_text_to_equal(
        '#\\{\\"index\\"\\:0\\,\\"type\\"\\:\\"output\\"\\}', "Dropdown 0 = LA"
    )
    dash_duo.find_element("#add-filter").click()
    dash_duo.select_dcc_dropdown(
        '#\\{\\"index\\"\\:1\\,\\"type\\"\\:\\"dropdown\\"\\}', "MTL"
    )
    dash_duo.wait_for_text_to_equal(
        '#\\{\\"index\\"\\:1\\,\\"type\\"\\:\\"output\\"\\}', "Dropdown 1 = MTL"
    )
    dash_duo.wait_for_text_to_equal(
        '#\\{\\"index\\"\\:0\\,\\"type\\"\\:\\"output\\"\\}', "Dropdown 0 = LA"
    )
    dash_duo.wait_for_no_elements(dash_duo.devtools_error_count_locator)


def test_cbwc004_layout_chunk_changed_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id={"type": "input", "index": 1}, value="input-1"),
            html.Div(id="container"),
            html.Div(id="output-outer"),
            html.Button("Show content", id="btn"),
        ]
    )

    @app.callback(Output("container", "children"), [Input("btn", "n_clicks")])
    def display_output(n):
        if n:
            return html.Div(
                [
                    dcc.Input(id={"type": "input", "index": 2}, value="input-2"),
                    html.Div(id="output-inner"),
                ]
            )
        else:
            return "No content initially"

    def trigger_info():
        triggered = dash.callback_context.triggered
        return "triggered is {} with prop_ids {}".format(
            "Truthy" if triggered else "Falsy",
            ", ".join(t["prop_id"] for t in triggered),
        )

    @app.callback(
        Output("output-inner", "children"),
        [Input({"type": "input", "index": ALL}, "value")],
    )
    def update_dynamic_output_pattern(wc_inputs):
        return trigger_info()
        # When this is triggered because output-2 was rendered,
        # nothing has changed

    @app.callback(
        Output("output-outer", "children"),
        [Input({"type": "input", "index": ALL}, "value")],
    )
    def update_output_on_page_pattern(value):
        return trigger_info()
        # When this triggered on page load,
        # nothing has changed
        # When dcc.Input(id={'type': 'input', 'index': 2})
        # is rendered (from display_output)
        # then `{'type': 'input', 'index': 2}` has changed

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#container", "No content initially")
    dash_duo.wait_for_text_to_equal(
        "#output-outer", "triggered is Falsy with prop_ids ."
    )

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal(
        "#output-outer",
        'triggered is Truthy with prop_ids {"index":2,"type":"input"}.value',
    )
    dash_duo.wait_for_text_to_equal(
        "#output-inner", "triggered is Falsy with prop_ids ."
    )

    dash_duo.find_elements("input")[0].send_keys("X")
    trigger_text = 'triggered is Truthy with prop_ids {"index":1,"type":"input"}.value'
    dash_duo.wait_for_text_to_equal("#output-outer", trigger_text)
    dash_duo.wait_for_text_to_equal("#output-inner", trigger_text)


def test_cbwc005_callbacks_count(dash_duo):
    global fibonacci_count
    global fibonacci_sum_count

    app = fibonacci_app(False)
    dash_duo.start_server(app)

    wait.until(lambda: fibonacci_count == 4, 3)  # initial
    wait.until(lambda: fibonacci_sum_count == 2, 3)  # initial + triggered

    dash_duo.find_element("#n").send_keys(Keys.UP)  # 5
    wait.until(lambda: fibonacci_count == 9, 3)
    wait.until(lambda: fibonacci_sum_count == 3, 3)

    dash_duo.find_element("#n").send_keys(Keys.UP)  # 6
    wait.until(lambda: fibonacci_count == 15, 3)
    wait.until(lambda: fibonacci_sum_count == 4, 3)

    dash_duo.find_element("#n").send_keys(Keys.DOWN)  # 5
    wait.until(lambda: fibonacci_count == 20, 3)
    wait.until(lambda: fibonacci_sum_count == 5, 3)

    dash_duo.find_element("#n").send_keys(Keys.DOWN)  # 4
    wait.until(lambda: fibonacci_count == 24, 3)
    wait.until(lambda: fibonacci_sum_count == 6, 3)

    dash_duo.find_element("#n").send_keys(Keys.DOWN)  # 3
    wait.until(lambda: fibonacci_count == 27, 3)
    wait.until(lambda: fibonacci_sum_count == 7, 3)

    dash_duo.find_element("#n").send_keys(Keys.DOWN)  # 2
    wait.until(lambda: fibonacci_count == 29, 3)
    wait.until(lambda: fibonacci_sum_count == 8, 3)

    dash_duo.find_element("#n").send_keys(Keys.DOWN)  # 1
    wait.until(lambda: fibonacci_count == 30, 3)
    wait.until(lambda: fibonacci_sum_count == 9, 3)

    dash_duo.find_element("#n").send_keys(Keys.DOWN)  # 0
    wait.until(lambda: fibonacci_count == 30, 3)
    wait.until(lambda: fibonacci_sum_count == 10, 3)


def test_cbwc006_grouping_callbacks(dash_duo):
    app = grouping_app()
    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#title", "Dash To-Do list")

    new_item = dash_duo.find_element("#new-item")
    add_item = dash_duo.find_element("#add")

    def assert_count(items):
        assert len(dash_duo.find_elements("#list-container>div")) == items

    def assert_callback_context(items_text):
        # Check args_grouping
        args_grouping = dict(
            items=dict(
                all=[
                    {
                        "id": {"id": i},
                        "property": "children",
                        "value": text,
                        "str_id": stringify_id({"id": i}),
                        "triggered": False,
                    }
                    for i, text in enumerate(items_text[:-1])
                ],
                new=dict(
                    id="new-item",
                    property="value",
                    value=items_text[-1],
                    str_id="new-item",
                    triggered=False,
                ),
            ),
            triggers=[
                {
                    "id": "add",
                    "property": "n_clicks",
                    "value": len(items_text),
                    "str_id": "add",
                    "triggered": True,
                },
                {
                    "id": "new-item",
                    "property": "n_submit",
                    "value": None,
                    "str_id": "new-item",
                    "triggered": False,
                },
            ],
        )
        dash_duo.wait_for_text_to_equal("#cc-args-grouping", repr(args_grouping))

        # Check outputs_grouping
        outputs_grouping = dict(
            list_container={"id": "list-container", "property": "children"},
            new_item={"id": "new-item", "property": "value"},
            totals={"id": "totals", "property": "children"},
            cc_args_grouping={"id": "cc-args-grouping", "property": "children"},
            cc_outputs_grouping={"id": "cc-outputs-grouping", "property": "children"},
        )
        dash_duo.wait_for_text_to_equal("#cc-outputs-grouping", repr(outputs_grouping))

    new_item.send_keys("apples")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "1 total item(s)")
    assert_count(1)
    assert_callback_context(["apples"])

    new_item.send_keys("bananas")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "2 total item(s)")
    assert_count(2)
    assert_callback_context(["apples", "bananas"])

    new_item.send_keys("carrots")
    add_item.click()
    dash_duo.wait_for_text_to_equal("#totals", "3 total item(s)")
    assert_count(3)
    assert_callback_context(["apples", "bananas", "carrots"])


def test_cbwc007_pmc_update_subtree_ordering(dash_duo):
    # Test for regression bug #2368, updated pmc subtree should keep order.
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("refresh options", id="refresh-options"),
            html.Br(),
            html.Div(
                [
                    *[
                        dcc.Dropdown(
                            id={"type": "demo-options", "index": i},
                            placeholder=f"dropdown-{i}",
                            style={"width": "200px"},
                        )
                        for i in range(2)
                    ],
                    dcc.Dropdown(
                        id={"type": "demo-options", "index": 2},
                        options=[f"option2-{i}" for i in range(3)],
                        placeholder="dropdown-2",
                        style={"width": "200px"},
                    ),
                ],
                id="dropdown-container",
            ),
            html.Br(),
            html.Pre(id="selected-values"),
        ],
        style={"padding": "50px"},
    )

    @app.callback(
        [
            Output({"type": "demo-options", "index": 0}, "options"),
            Output({"type": "demo-options", "index": 1}, "options"),
        ],
        Input("refresh-options", "n_clicks"),
        prevent_initial_call=True,
    )
    def refresh_options(_):
        return [[f"option0-{i}" for i in range(3)], [f"option1-{i}" for i in range(3)]]

    @app.callback(
        Output("selected-values", "children"),
        Input({"type": "demo-options", "index": ALL}, "value"),
    )
    def update_selected_values(values):
        return str(values)

    dash_duo.start_server(app)
    dash_duo.select_dcc_dropdown(".dash-dropdown-wrapper:nth-child(3) button", index=2)

    dash_duo.wait_for_text_to_equal("#selected-values", "[None, None, 'option2-2']")

    dash_duo.wait_for_element("#refresh-options").click()

    dash_duo.select_dcc_dropdown(".dash-dropdown-wrapper:nth-child(2) button", index=2)
    dash_duo.wait_for_text_to_equal(
        "#selected-values", "[None, 'option1-2', 'option2-2']"
    )

    dash_duo.select_dcc_dropdown(".dash-dropdown-wrapper:nth-child(1) button", index=2)
    dash_duo.wait_for_text_to_equal(
        "#selected-values", "['option0-2', 'option1-2', 'option2-2']"
    )


def test_cbwc008_running_match(dash_duo):
    lock = Lock()
    app = dash.Dash()

    app.layout = [
        html.Div(
            [
                html.Button(
                    "Test1",
                    id={"component": "button", "index": "1"},
                ),
                html.Button(
                    "Test2",
                    id={"component": "button", "index": "2"},
                ),
            ],
            id="buttons",
        ),
        html.Div(html.Div(id={"component": "output", "index": "1"}), id="output1"),
        html.Div(html.Div(id={"component": "output", "index": "2"}), id="output2"),
    ]

    @app.callback(
        Output({"component": "output", "index": MATCH}, "children"),
        Input({"component": "button", "index": MATCH}, "n_clicks"),
        running=[
            (
                Output({"component": "button", "index": MATCH}, "children"),
                "running",
                "finished",
            ),
            (Output({"component": "button", "index": ALL}, "disabled"), True, False),
        ],
        prevent_initial_call=True,
    )
    def on_click(_) -> str:
        with lock:
            return "done"

    dash_duo.start_server(app)

    for i in range(1, 3):
        with lock:
            dash_duo.find_element(f"#buttons button:nth-child({i})").click()
            dash_duo.wait_for_text_to_equal(
                f"#buttons button:nth-child({i})", "running"
            )
            # verify all the buttons were disabled.
            assert dash_duo.find_element("#buttons button:nth-child(1)").get_attribute(
                "disabled"
            )
            assert dash_duo.find_element("#buttons button:nth-child(2)").get_attribute(
                "disabled"
            )

        dash_duo.wait_for_text_to_equal(f"#output{i}", "done")
        dash_duo.wait_for_text_to_equal(f"#buttons button:nth-child({i})", "finished")

        assert not dash_duo.find_element("#buttons button:nth-child(1)").get_attribute(
            "disabled"
        )
        assert not dash_duo.find_element("#buttons button:nth-child(2)").get_attribute(
            "disabled"
        )


def test_cbwc009_match_input_fixed_output(dash_duo):
    # Issue #2462: allow MATCH in Input with a fixed-id Output.
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(
                "Alpha",
                id={"type": "btn", "index": "alpha"},
            ),
            html.Button(
                "Beta",
                id={"type": "btn", "index": "beta"},
            ),
            html.Div("initial", id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input({"type": "btn", "index": MATCH}, "n_clicks"),
        State({"type": "btn", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def show_clicked(_, id_):
        return f"clicked {id_['index']}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "initial")

    dash_duo.find_element(
        '[id=\\{\\"index\\"\\:\\"alpha\\"\\,\\"type\\"\\:\\"btn\\"\\}]'
    ).click()
    dash_duo.wait_for_text_to_equal("#out", "clicked alpha")

    dash_duo.find_element(
        '[id=\\{\\"index\\"\\:\\"beta\\"\\,\\"type\\"\\:\\"btn\\"\\}]'
    ).click()
    dash_duo.wait_for_text_to_equal("#out", "clicked beta")

    assert dash_duo.get_logs() == []


def test_cbwc010_match_input_no_output(dash_duo):
    # Issue #2462: allow MATCH in Input with no Output (set_props).
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(
                "One",
                id={"type": "btn", "index": 1},
            ),
            html.Button(
                "Two",
                id={"type": "btn", "index": 2},
            ),
            html.Div("initial", id="out"),
        ]
    )

    @app.callback(
        Input({"type": "btn", "index": MATCH}, "n_clicks"),
        State({"type": "btn", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def announce(_, id_):
        set_props("out", {"children": f"clicked index={id_['index']}"})

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "initial")

    dash_duo.find_element('[id=\\{\\"index\\"\\:1\\,\\"type\\"\\:\\"btn\\"\\}]').click()
    dash_duo.wait_for_text_to_equal("#out", "clicked index=1")

    dash_duo.find_element('[id=\\{\\"index\\"\\:2\\,\\"type\\"\\:\\"btn\\"\\}]').click()
    dash_duo.wait_for_text_to_equal("#out", "clicked index=2")

    assert dash_duo.get_logs() == []


def test_cbwc011_patch_no_spurious_match_callbacks(dash_duo):
    """Test for the initial call suppression in getUnfilteredLayoutCallbacks

    When Patch() appends a new MATCHpattern component, existing MATCH callbacks
    must not refire for preexisting components. Previously, crawlLayout would
    visit all children in the layout chunk and mark every matching output as
    initial Call=true, causing all existing callbacks to spuriously reexecute

    The fix uses what the patch operations recorded while they were applied
    to only give an initial call to the components the patch actually created
    """
    lock = threading.Lock()
    fire_counts = {}  # {index: count}, how many times each MATCH callback fired

    def make_item(index):
        return html.Div(
            [
                dcc.Input(
                    id={"type": "item-input", "index": index},
                    value=index,
                    type="number",
                    className="item-input",
                ),
                html.Div(
                    "init",
                    id={"type": "item-output", "index": index},
                    className="item-output",
                ),
            ]
        )

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Add", id="add-btn", n_clicks=0),
            html.Div([make_item(0), make_item(1)], id="container"),
        ]
    )

    @app.callback(
        Output("container", "children"),
        Input("add-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_item(n):
        p = Patch()
        p.append(make_item(n + 1))
        return p

    @app.callback(
        Output({"type": "item-output", "index": MATCH}, "children"),
        Input({"type": "item-input", "index": MATCH}, "value"),
    )
    def on_value_change(value):
        from dash import ctx

        idx = ctx.outputs_grouping["id"]["index"]
        with lock:
            fire_counts[idx] = fire_counts.get(idx, 0) + 1
            count = fire_counts[idx]
        return f"fired-{idx}-#{count}"

    dash_duo.start_server(app)

    # Wait for the initial callbacks to fire for both preexisting items
    wait.until(lambda: fire_counts.get(0, 0) >= 1, 5)
    wait.until(lambda: fire_counts.get(1, 0) >= 1, 5)

    counts_before = {0: fire_counts[0], 1: fire_counts[1]}

    # Add a new item via Patch, this should fire only for index 2
    dash_duo.find_element("#add-btn").click()
    wait.until(lambda: fire_counts.get(2, 0) >= 1, 5)

    # Preexisting callbacks must not have refired
    assert fire_counts[0] == counts_before[0], (
        f"Item 0 callback fired spuriously after Patch: "
        f"was {counts_before[0]}, now {fire_counts[0]}"
    )
    assert fire_counts[1] == counts_before[1], (
        f"Item 1 callback fired spuriously after Patch: "
        f"was {counts_before[1]}, now {fire_counts[1]}"
    )
    assert (
        fire_counts[2] == 1
    ), f"New item 2 callback should have fired exactly once, fired {fire_counts[2]}"


def test_cbwc012_patch_no_spurious_match_callbacks_undefined_output_prop(dash_duo):
    """Existing MATCH components whose output prop is undefined
    must not have their callbacks refired when Patch() appends a new sibling

    This covers components whose output prop has no value at all
    (dcc.Slider without an explicit `value`): suppression must not depend on
    comparing prop values, which cannot distinguish "unchanged" from "undefined
    on both sides", but on whether the patch created the component
    """
    lock = threading.Lock()
    fire_counts = {}  # {aio_id: count}

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Add Slider", id="add-btn", n_clicks=0),
            html.Div(id="slider-container", children=[]),
        ]
    )

    @app.callback(
        Output("slider-container", "children"),
        Input("add-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_slider(n_clicks):
        p = Patch()
        # dcc.Slider with no explicit `value`, value prop is undefined in layout
        p.append(
            dcc.Slider(
                id={"type": "slider", "aio_id": str(n_clicks)},
                step=0.1,
                persistence=str(n_clicks),
                persistence_type="local",
            )
        )
        return p

    @app.callback(
        Output({"type": "slider", "aio_id": MATCH}, "value"),
        Input({"type": "slider", "aio_id": MATCH}, "value"),
        prevent_initial_call=False,
    )
    def on_slider_value(val):
        from dash import ctx, no_update

        aio_id = ctx.outputs_grouping["id"]["aio_id"]
        with lock:
            fire_counts[aio_id] = fire_counts.get(aio_id, 0) + 1
        return no_update

    dash_duo.start_server(app)

    # Add first slider, should fire exactly once for slider "1"
    dash_duo.find_element("#add-btn").click()
    wait.until(lambda: fire_counts.get("1", 0) >= 1, 5)
    assert (
        fire_counts["1"] == 1
    ), f"Slider 1 fired {fire_counts['1']} times after being added"

    # Add second slider, should fire once for "2", not refire "1"
    dash_duo.find_element("#add-btn").click()
    wait.until(lambda: fire_counts.get("2", 0) >= 1, 5)
    assert fire_counts.get("1", 0) == 1, (
        f"Slider 1 spuriously refired after adding slider 2: "
        f"count={fire_counts.get('1', 0)}"
    )
    assert (
        fire_counts["2"] == 1
    ), f"Slider 2 fired {fire_counts['2']} times after being added"

    # Add third slider, should fire once for "3", not refire "1" or "2"
    dash_duo.find_element("#add-btn").click()
    wait.until(lambda: fire_counts.get("3", 0) >= 1, 5)
    assert fire_counts.get("1", 0) == 1, (
        f"Slider 1 spuriously refired after adding slider 3: "
        f"count={fire_counts.get('1', 0)}"
    )
    assert fire_counts.get("2", 0) == 1, (
        f"Slider 2 spuriously refired after adding slider 3: "
        f"count={fire_counts.get('2', 0)}"
    )
    assert (
        fire_counts["3"] == 1
    ), f"Slider 3 fired {fire_counts['3']} times after being added"


def test_cbwc013_patch_rebuild_match_initial_call_undefined_output_prop(dash_duo):
    """Ensure that initial callbacks are running when they're meant to

    When a Patch operation replaces an entire children list of a container with
    fresh component instances that reuse the same MATCH ids as the prior
    occupants, and the relevant output prop is undefined on both old and new
    sides (a dcc.Slider with no explicit `value`), the per MATCH initial
    callback should only fire once for each newly mounted slot

    Bug behavior:
        Suppression that goes by "was this id already on the page" or by
        comparing old and new prop values considers each rebuilt slider
        unchanged, both sides are undefined, so its initial call is dropped
        from the queue and never fires. The Python fire_counts dict therefore
        stays at the pre rebuild value

    Expected behavior (after fix):
        Every rebuilt slot fires the initial MATCH callback exactly once,
        regardless of whether its output prop is defined: the patch created
        these instances, so they are new whatever ids they reuse

    The MATCH callback used here outputs to `slider.value` (undefined on both
    sides) and is keyed by an Input on `slider.min`. The input value doesn't
    change across the rebuild, so the *only* path by which this callback can
    fire for newly mounted instances is the layout level initial call path
    (handleOneId -> outIdCallbacks)
    """
    lock = threading.Lock()
    fire_counts = {}  # {idx: count}
    N = 5

    def make_slider_row(i):
        return html.Div(
            [
                dcc.Slider(
                    id={"type": "slider", "idx": i},
                    min=0,
                    max=10,
                    step=0.1,
                    # NOTE: no `value` set, undefined in layout on both sides
                ),
            ]
        )

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Rebuild", id="rebuild-btn", n_clicks=0),
            html.Div(
                id="container",
                children=[make_slider_row(i) for i in range(N)],
            ),
        ]
    )

    @app.callback(
        Output("container", "children"),
        Input("rebuild-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def rebuild(_n):
        # Children list replacement via Patch: clear + append rebuilds the
        # entire list with fresh component instances. The MATCH ids match the
        # prior occupants exactly, and so do the props, so nothing in the
        # resulting layout tells the new instances apart from the ones they
        # replaced, only the patch operations themselves know they are new
        p = Patch()
        p.clear()
        for i in range(N):
            p.append(make_slider_row(i))
        return p

    @app.callback(
        Output({"type": "slider", "idx": MATCH}, "value"),
        Input({"type": "slider", "idx": MATCH}, "min"),
        prevent_initial_call=False,
    )
    def on_slider_mount(_min_val):
        from dash import ctx, no_update

        idx = ctx.outputs_grouping["id"]["idx"]
        with lock:
            fire_counts[idx] = fire_counts.get(idx, 0) + 1
        # Don't actually update `value`, keep it undefined on both sides, so
        # that suppressing the initial call by comparing the old and new value
        # would drop it for every rebuilt slider
        return no_update

    dash_duo.start_server(app)

    # Initial mount: every slider should fire its MATCH callback exactly once
    for i in range(N):
        wait.until(lambda i=i: fire_counts.get(i, 0) >= 1, 5)
    initial = dict(fire_counts)
    for i in range(N):
        assert (
            initial[i] == 1
        ), f"Slider {i} fired {initial[i]} times on initial mount (expected 1)"

    # Patch rebuilt the children list. Every slot is freshly mounted, so each
    # MATCH callback should fire exactly once more
    dash_duo.find_element("#rebuild-btn").click()

    # Wait long enough for any queued/dispatched callbacks to complete
    import time

    time.sleep(3)

    failures = []
    for i in range(N):
        expected = initial[i] + 1
        actual = fire_counts.get(i, 0)
        if actual != expected:
            failures.append(f"  slot idx={i}: expected {expected} fires, got {actual}")

    assert not failures, (
        "After Patch driven children list rebuild, the following MATCH "
        "callbacks did not refire as expected (initial call suppression bug):\n"
        + "\n".join(failures)
        + "\n\nThe renderer must only suppress the initial call for components "
        "the Patch carried over, which it takes from the patch operations "
        "themselves. Components rebuilt with a reused id are new instances and "
        "must get their initial call, even when their output prop is undefined "
        "on both sides"
    )

    assert dash_duo.get_logs() == []


def test_cbwc014_patch_nested_change_does_not_refire_container_callbacks(dash_duo):
    """A Patch that changes something deep inside a container
    must not rerun the initial callbacks of the containers around it

    Patch operations are applied with ramda's assocPath, which rebuilds every
    object between the patched prop and the value that changed. Those
    containers are not new, the patch only carried them over, so their
    initial callbacks must stay suppressed. Reference identity cannot tell
    them apart from a component the patch created, since assocPath gives them
    a brand new props object either way. The renderer instead records what
    each patch operation did while applying it

    The same Patch also appends a genuinely new component, whose initial
    callback must still fire, proving the suppression is not too broad
    """
    lock = threading.Lock()
    fire_counts = {}

    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.Button("Patch", id="patch-btn", n_clicks=0),
            # Never changes, so the counting callbacks below can only fire from
            # the layout level initial call path
            html.Div("static", id="static"),
            html.Div(
                [
                    html.Div(
                        [dcc.Input(id="deep-input", value="initial")],
                        id="patched-group",
                    ),
                    html.Div(id="untouched-group"),
                ],
                id="container",
            ),
            html.Div("0", id="done"),
        ]
    )

    def count_fire(name):
        with lock:
            fire_counts[name] = fire_counts.get(name, 0) + 1
        return f"fired-{name}"

    @app.callback(
        Output("container", "children"),
        Output("done", "children"),
        Input("patch-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def do_patch(n):
        p = Patch()
        # Deep change: only `deep-input.value` is written, but assocPath has to
        # rebuild the children list and `patched-group` on the way there
        p[0]["props"]["children"][0]["props"]["value"] = f"patched-{n}"
        # ... and one genuinely new component
        p.append(html.Div(id="new-group"))
        return p, str(n)

    @app.callback(Output("patched-group", "className"), Input("static", "children"))
    def on_patched_group(_):
        return count_fire("patched-group")

    @app.callback(Output("untouched-group", "className"), Input("static", "children"))
    def on_untouched_group(_):
        return count_fire("untouched-group")

    @app.callback(Output("new-group", "className"), Input("static", "children"))
    def on_new_group(_):
        return count_fire("new-group")

    dash_duo.start_server(app)

    # Both containers get their initial call once, on page load. `new-group`
    # does not exist yet, so its callback cannot run
    wait.until(lambda: fire_counts.get("patched-group", 0) >= 1, 5)
    wait.until(lambda: fire_counts.get("untouched-group", 0) >= 1, 5)
    assert fire_counts.get("new-group", 0) == 0

    dash_duo.find_element("#patch-btn").click()
    dash_duo.wait_for_text_to_equal("#done", "1")

    # The new component's initial call and any spurious refire of the existing
    # ones are queued together, so waiting for it is a sync point for both
    wait.until(lambda: fire_counts.get("new-group", 0) >= 1, 5)
    wait.until(
        lambda: dash_duo.find_element("#deep-input").get_attribute("value")
        == "patched-1",
        5,
    )

    assert fire_counts["patched-group"] == 1, (
        "The container rebuilt by assocPath on the way to the patched value "
        f"refired its initial callback: count={fire_counts['patched-group']}"
    )
    assert fire_counts["untouched-group"] == 1, (
        "An untouched sibling container refired its initial callback: "
        f"count={fire_counts['untouched-group']}"
    )
    assert (
        fire_counts["new-group"] == 1
    ), f"The appended component fired {fire_counts['new-group']} times (expected 1)"

    assert dash_duo.get_logs() == []
