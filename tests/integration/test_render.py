# -*- coding: UTF-8 -*-
import time
import json
from multiprocessing import Value
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dash import Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc

from .IntegrationTests import IntegrationTests
from .utils import wait_for


TIMEOUT = 20


class Tests(IntegrationTests):
    def setUp(self):
        pass

    def wait_for_element_by_css_selector(self, selector, timeout=TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
            'Could not find element with selector "{}"'.format(selector),
        )

    def wait_for_text_to_equal(self, selector, assertion_text, timeout=TIMEOUT):
        self.wait_for_element_by_css_selector(selector)
        WebDriverWait(self.driver, timeout).until(
            lambda *args: (
                (
                    str(self.wait_for_element_by_css_selector(selector).text)
                    == assertion_text
                )
                or (
                    str(
                        self.wait_for_element_by_css_selector(selector).get_attribute(
                            "value"
                        )
                    )
                    == assertion_text
                )
            ),
            "Element '{}' text expects to equal '{}' but it didn't".format(
                selector, assertion_text
            ),
        )

    def request_queue_assertions(self, check_rejected=True, expected_length=None):
        request_queue = self.driver.execute_script(
            "return window.store.getState().requestQueue"
        )
        self.assertTrue(all([(r["status"] == 200) for r in request_queue]))

        if check_rejected:
            self.assertTrue(all([(r["rejected"] is False) for r in request_queue]))

        if expected_length is not None:
            self.assertEqual(len(request_queue), expected_length)

    def click_undo(self):
        undo_selector = "._dash-undo-redo span:first-child div:last-child"
        undo = self.wait_for_element_by_css_selector(undo_selector)
        self.wait_for_text_to_equal(undo_selector, "undo")
        undo.click()

    def click_redo(self):
        redo_selector = "._dash-undo-redo span:last-child div:last-child"
        self.wait_for_text_to_equal(redo_selector, "redo")
        redo = self.wait_for_element_by_css_selector(redo_selector)
        redo.click()

    def check_undo_redo_exist(self, has_undo, has_redo):
        selector = "._dash-undo-redo span div:last-child"
        els = self.driver.find_elements_by_css_selector(selector)
        texts = (["undo"] if has_undo else []) + (["redo"] if has_redo else [])

        self.assertEqual(len(els), len(texts))
        for el, text in zip(els, texts):
            self.assertEqual(el.text, text)

    def test_undo_redo(self):
        app = Dash(__name__, show_undo_redo=True)
        app.layout = html.Div([dcc.Input(id="a"), html.Div(id="b")])

        @app.callback(Output("b", "children"), [Input("a", "value")])
        def set_b(a):
            return a

        self.startServer(app)

        a = self.wait_for_element_by_css_selector("#a")
        a.send_keys("xyz")

        self.wait_for_text_to_equal("#b", "xyz")
        self.check_undo_redo_exist(True, False)

        self.click_undo()
        self.wait_for_text_to_equal("#b", "xy")
        self.check_undo_redo_exist(True, True)

        self.click_undo()
        self.wait_for_text_to_equal("#b", "x")
        self.check_undo_redo_exist(True, True)

        self.click_redo()
        self.wait_for_text_to_equal("#b", "xy")
        self.check_undo_redo_exist(True, True)

        self.percy_snapshot(name="undo-redo")

        self.click_undo()
        self.click_undo()
        self.wait_for_text_to_equal("#b", "")
        self.check_undo_redo_exist(False, True)

    def test_no_undo_redo(self):
        app = Dash(__name__)
        app.layout = html.Div([dcc.Input(id="a"), html.Div(id="b")])

        @app.callback(Output("b", "children"), [Input("a", "value")])
        def set_b(a):
            return a

        self.startServer(app)

        a = self.wait_for_element_by_css_selector("#a")
        a.send_keys("xyz")

        self.wait_for_text_to_equal("#b", "xyz")
        toolbar = self.driver.find_elements_by_css_selector("._dash-undo-redo")
        self.assertEqual(len(toolbar), 0)

    def test_array_of_falsy_child(self):
        app = Dash(__name__)
        app.layout = html.Div(id="nully-wrapper", children=[0])

        self.startServer(app)

        self.wait_for_text_to_equal("#nully-wrapper", "0")

        self.assertTrue(self.is_console_clean())

    def test_of_falsy_child(self):
        app = Dash(__name__)
        app.layout = html.Div(id="nully-wrapper", children=0)

        self.startServer(app)

        self.wait_for_text_to_equal("#nully-wrapper", "0")

        self.assertTrue(self.is_console_clean())

    def test_event_properties(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [html.Button("Click Me", id="button"), html.Div(id="output")]
        )

        call_count = Value("i", 0)

        @app.callback(Output("output", "children"), [Input("button", "n_clicks")])
        def update_output(n_clicks):
            if not n_clicks:
                raise PreventUpdate
            call_count.value += 1
            return "Click"

        self.startServer(app)
        btn = self.driver.find_element_by_id("button")
        output = lambda: self.driver.find_element_by_id("output")
        self.assertEqual(call_count.value, 0)
        self.assertEqual(output().text, "")

        btn.click()
        wait_for(lambda: output().text == "Click")
        self.assertEqual(call_count.value, 1)

    def test_chained_dependencies_direct_lineage(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="input-1", value="input 1"),
                dcc.Input(id="input-2"),
                html.Div("test", id="output"),
            ]
        )
        input1 = lambda: self.driver.find_element_by_id("input-1")
        input2 = lambda: self.driver.find_element_by_id("input-2")
        output = lambda: self.driver.find_element_by_id("output")

        call_counts = {"output": Value("i", 0), "input-2": Value("i", 0)}

        @app.callback(Output("input-2", "value"), [Input("input-1", "value")])
        def update_input(input1):
            call_counts["input-2"].value += 1
            return "<<{}>>".format(input1)

        @app.callback(
            Output("output", "children"),
            [Input("input-1", "value"), Input("input-2", "value")],
        )
        def update_output(input1, input2):
            call_counts["output"].value += 1
            return "{} + {}".format(input1, input2)

        self.startServer(app)

        wait_for(lambda: call_counts["output"].value == 1)
        wait_for(lambda: call_counts["input-2"].value == 1)
        self.assertEqual(input1().get_attribute("value"), "input 1")
        self.assertEqual(input2().get_attribute("value"), "<<input 1>>")
        self.assertEqual(output().text, "input 1 + <<input 1>>")

        input1().send_keys("x")
        wait_for(lambda: call_counts["output"].value == 2)
        wait_for(lambda: call_counts["input-2"].value == 2)
        self.assertEqual(input1().get_attribute("value"), "input 1x")
        self.assertEqual(input2().get_attribute("value"), "<<input 1x>>")
        self.assertEqual(output().text, "input 1x + <<input 1x>>")

        input2().send_keys("y")
        wait_for(lambda: call_counts["output"].value == 3)
        wait_for(lambda: call_counts["input-2"].value == 2)
        self.assertEqual(input1().get_attribute("value"), "input 1x")
        self.assertEqual(input2().get_attribute("value"), "<<input 1x>>y")
        self.assertEqual(output().text, "input 1x + <<input 1x>>y")

    def test_chained_dependencies_branched_lineage(self):
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
        parenta = lambda: self.driver.find_element_by_id("parent-a")
        parentb = lambda: self.driver.find_element_by_id("parent-b")
        childa = lambda: self.driver.find_element_by_id("child-a")
        childb = lambda: self.driver.find_element_by_id("child-b")

        call_counts = {
            "parent-a": Value("i", 0),
            "parent-b": Value("i", 0),
            "child-a": Value("i", 0),
            "child-b": Value("i", 0),
        }

        @app.callback(Output("parent-a", "value"), [Input("grandparent", "value")])
        def update_parenta(value):
            call_counts["parent-a"].value += 1
            return "a: {}".format(value)

        @app.callback(Output("parent-b", "value"), [Input("grandparent", "value")])
        def update_parentb(value):
            time.sleep(0.5)
            call_counts["parent-b"].value += 1
            return "b: {}".format(value)

        @app.callback(
            Output("child-a", "children"),
            [Input("parent-a", "value"), Input("parent-b", "value")],
        )
        def update_childa(parenta_value, parentb_value):
            time.sleep(1)
            call_counts["child-a"].value += 1
            return "{} + {}".format(parenta_value, parentb_value)

        @app.callback(
            Output("child-b", "children"),
            [
                Input("parent-a", "value"),
                Input("parent-b", "value"),
                Input("grandparent", "value"),
            ],
        )
        def update_childb(parenta_value, parentb_value, grandparent_value):
            call_counts["child-b"].value += 1
            return "{} + {} + {}".format(
                parenta_value, parentb_value, grandparent_value
            )

        self.startServer(app)

        wait_for(lambda: childa().text == "a: input 1 + b: input 1")
        wait_for(lambda: childb().text == "a: input 1 + b: input 1 + input 1")
        time.sleep(1)  # wait for potential requests of app to settle down
        self.assertEqual(parenta().get_attribute("value"), "a: input 1")
        self.assertEqual(parentb().get_attribute("value"), "b: input 1")
        self.assertEqual(call_counts["parent-a"].value, 1)
        self.assertEqual(call_counts["parent-b"].value, 1)
        self.assertEqual(call_counts["child-a"].value, 1)
        self.assertEqual(call_counts["child-b"].value, 1)

    def test_removing_component_while_its_getting_updated(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.RadioItems(
                    id="toc",
                    options=[{"label": i, "value": i} for i in ["1", "2"]],
                    value="1",
                ),
                html.Div(id="body"),
            ]
        )
        app.config.suppress_callback_exceptions = True

        call_counts = {"body": Value("i", 0), "button-output": Value("i", 0)}

        @app.callback(Output("body", "children"), [Input("toc", "value")])
        def update_body(chapter):
            call_counts["body"].value += 1
            if chapter == "1":
                return [
                    html.Div("Chapter 1"),
                    html.Button("clicking this button takes forever", id="button"),
                    html.Div(id="button-output"),
                ]
            elif chapter == "2":
                return "Chapter 2"
            else:
                raise Exception("chapter is {}".format(chapter))

        @app.callback(
            Output("button-output", "children"), [Input("button", "n_clicks")]
        )
        def this_callback_takes_forever(n_clicks):
            if not n_clicks:
                # initial value is quick, only new value is slow
                # also don't let the initial value increment call_counts
                return "Initial Value"
            time.sleep(5)
            call_counts["button-output"].value += 1
            return "New value!"

        body = lambda: self.driver.find_element_by_id("body")
        self.startServer(app)

        wait_for(lambda: call_counts["body"].value == 1)
        time.sleep(0.5)
        self.driver.find_element_by_id("button").click()

        # while that callback is resolving, switch the chapter,
        # hiding the `button-output` tag
        def chapter2_assertions():
            wait_for(lambda: body().text == "Chapter 2")

            layout = self.driver.execute_script(
                "return JSON.parse(JSON.stringify("
                "window.store.getState().layout"
                "))"
            )

            dcc_radio = layout["props"]["children"][0]
            html_body = layout["props"]["children"][1]

            self.assertEqual(dcc_radio["props"]["id"], "toc")
            self.assertEqual(dcc_radio["props"]["value"], "2")

            self.assertEqual(html_body["props"]["id"], "body")
            self.assertEqual(html_body["props"]["children"], "Chapter 2")

        (self.driver.find_elements_by_css_selector('input[type="radio"]')[1]).click()
        chapter2_assertions()
        self.assertEqual(call_counts["button-output"].value, 0)
        time.sleep(5)
        wait_for(lambda: call_counts["button-output"].value == 1)
        time.sleep(2)  # liberally wait for the front-end to process request
        chapter2_assertions()
        self.assertTrue(self.is_console_clean())

    def test_rendering_layout_calls_callback_once_per_output(self):
        app = Dash(__name__)
        call_count = Value("i", 0)

        app.config["suppress_callback_exceptions"] = True
        app.layout = html.Div(
            [
                html.Div(
                    [
                        dcc.Input(value="Input {}".format(i), id="input-{}".format(i))
                        for i in range(10)
                    ]
                ),
                html.Div(id="container"),
                dcc.RadioItems(),
            ]
        )

        @app.callback(
            Output("container", "children"),
            [Input("input-{}".format(i), "value") for i in range(10)],
        )
        def dynamic_output(*args):
            call_count.value += 1
            return json.dumps(args, indent=2)

        self.startServer(app)

        time.sleep(5)

        self.percy_snapshot(name="test_rendering_layout_calls_callback_once_per_output")

        self.assertEqual(call_count.value, 1)

    def test_rendering_new_content_calls_callback_once_per_output(self):
        app = Dash(__name__)
        call_count = Value("i", 0)

        app.config["suppress_callback_exceptions"] = True
        app.layout = html.Div(
            [
                html.Button(
                    id="display-content", children="Display Content", n_clicks=0
                ),
                html.Div(id="container"),
                dcc.RadioItems(),
            ]
        )

        @app.callback(
            Output("container", "children"), [Input("display-content", "n_clicks")]
        )
        def display_output(n_clicks):
            if n_clicks == 0:
                return ""
            return html.Div(
                [
                    html.Div(
                        [
                            dcc.Input(
                                value="Input {}".format(i), id="input-{}".format(i)
                            )
                            for i in range(10)
                        ]
                    ),
                    html.Div(id="dynamic-output"),
                ]
            )

        @app.callback(
            Output("dynamic-output", "children"),
            [Input("input-{}".format(i), "value") for i in range(10)],
        )
        def dynamic_output(*args):
            call_count.value += 1
            return json.dumps(args, indent=2)

        self.startServer(app)

        self.wait_for_element_by_css_selector("#display-content").click()

        time.sleep(5)

        self.percy_snapshot(
            name="test_rendering_new_content_calls_callback_once_per_output"
        )

        self.assertEqual(call_count.value, 1)

    def test_callbacks_called_multiple_times_and_out_of_order_multi_output(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Button(id="input", n_clicks=0),
                html.Div(id="output1"),
                html.Div(id="output2"),
            ]
        )

        call_count = Value("i", 0)

        @app.callback(
            [Output("output1", "children"), Output("output2", "children")],
            [Input("input", "n_clicks")],
        )
        def update_output(n_clicks):
            call_count.value = call_count.value + 1
            if n_clicks == 1:
                time.sleep(4)
            return n_clicks, n_clicks + 1

        self.startServer(app)
        button = self.wait_for_element_by_css_selector("#input")
        button.click()
        button.click()
        time.sleep(8)
        self.percy_snapshot(
            name="test_callbacks_called_multiple_times" "_and_out_of_order_multi_output"
        )
        self.assertEqual(call_count.value, 3)
        self.wait_for_text_to_equal("#output1", "2")
        self.wait_for_text_to_equal("#output2", "3")
        request_queue = self.driver.execute_script(
            "return window.store.getState().requestQueue"
        )
        self.assertFalse(request_queue[0]["rejected"])
        self.assertEqual(len(request_queue), 1)

    def test_callbacks_with_shared_grandparent(self):
        app = Dash()

        app.layout = html.Div(
            [
                html.Div(id="session-id", children="id"),
                dcc.Dropdown(id="dropdown-1"),
                dcc.Dropdown(id="dropdown-2"),
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
            [Input("dropdown-2", "value"), Input("session-id", "children")],
        )
        def dropdown_2(value, session_id):
            call_counts["dropdown_2"].value += 1
            return options

        self.startServer(app)

        self.wait_for_element_by_css_selector("#session-id")
        time.sleep(2)
        self.assertEqual(call_counts["dropdown_1"].value, 1)
        self.assertEqual(call_counts["dropdown_2"].value, 1)

        self.assertTrue(self.is_console_clean())

    def test_callbacks_triggered_on_generated_output(self):
        app = Dash()
        app.config["suppress_callback_exceptions"] = True

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

        @app.callback(Output("tab-output", "children"), [Input("tabs", "value")])
        def display_content(value):
            return html.Div([html.Div(id="tab-{}-output".format(value))])

        @app.callback(
            Output("tab-1-output", "children"), [Input("outer-controls", "value")]
        )
        def display_tab1_output(value):
            call_counts["tab1"].value += 1
            return 'Selected "{}" in tab 1'.format(value)

        @app.callback(
            Output("tab-2-output", "children"), [Input("outer-controls", "value")]
        )
        def display_tab2_output(value):
            call_counts["tab2"].value += 1
            return 'Selected "{}" in tab 2'.format(value)

        self.startServer(app)
        self.wait_for_element_by_css_selector("#tab-output")
        time.sleep(2)

        self.assertEqual(call_counts["tab1"].value, 1)
        self.assertEqual(call_counts["tab2"].value, 0)
        self.wait_for_text_to_equal("#tab-output", 'Selected "a" in tab 1')
        self.wait_for_text_to_equal("#tab-1-output", 'Selected "a" in tab 1')

        (self.driver.find_elements_by_css_selector('input[type="radio"]')[1]).click()
        time.sleep(2)

        self.wait_for_text_to_equal("#tab-output", 'Selected "a" in tab 2')
        self.wait_for_text_to_equal("#tab-2-output", 'Selected "a" in tab 2')
        self.assertEqual(call_counts["tab1"].value, 1)
        self.assertEqual(call_counts["tab2"].value, 1)

        self.assertTrue(self.is_console_clean())

    def test_initialization_with_overlapping_outputs(self):
        app = Dash()
        app.layout = html.Div(
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
            "output-1": Value("i", 0),
            "output-2": Value("i", 0),
            "output-3": Value("i", 0),
            "output-4": Value("i", 0),
        }

        def generate_callback(outputid):
            def callback(*args):
                call_counts[outputid].value += 1
                return "{}, {}".format(*args)

            return callback

        for i in range(1, 5):
            outputid = "output-{}".format(i)
            app.callback(
                Output(outputid, "children"),
                [
                    Input("input-{}".format(i), "children"),
                    Input("input-{}".format(i + 1), "children"),
                ],
            )(generate_callback(outputid))

        self.startServer(app)

        self.wait_for_element_by_css_selector("#output-1")
        time.sleep(5)

        for i in range(1, 5):
            outputid = "output-{}".format(i)
            self.assertEqual(call_counts[outputid].value, 1)
            self.wait_for_text_to_equal(
                "#{}".format(outputid), "input-{}, input-{}".format(i, i + 1)
            )

    def test_generate_overlapping_outputs(self):
        app = Dash()
        app.config["suppress_callback_exceptions"] = True
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
        app.layout = html.Div([html.Div(id="input"), html.Div(id="container")])

        call_counts = {
            "container": Value("i", 0),
            "output-1": Value("i", 0),
            "output-2": Value("i", 0),
            "output-3": Value("i", 0),
            "output-4": Value("i", 0),
        }

        @app.callback(Output("container", "children"), [Input("input", "children")])
        def display_output(*args):
            call_counts["container"].value += 1
            return block

        def generate_callback(outputid):
            def callback(*args):
                call_counts[outputid].value += 1
                return "{}, {}".format(*args)

            return callback

        for i in range(1, 5):
            outputid = "output-{}".format(i)
            app.callback(
                Output(outputid, "children"),
                [
                    Input("input-{}".format(i), "children"),
                    Input("input-{}".format(i + 1), "children"),
                ],
            )(generate_callback(outputid))

        self.startServer(app)

        wait_for(lambda: call_counts["container"].value == 1)
        self.wait_for_element_by_css_selector("#output-1")
        time.sleep(5)

        for i in range(1, 5):
            outputid = "output-{}".format(i)
            self.assertEqual(call_counts[outputid].value, 1)
            self.wait_for_text_to_equal(
                "#{}".format(outputid), "input-{}, input-{}".format(i, i + 1)
            )
        self.assertEqual(call_counts["container"].value, 1)

    def test_multiple_properties_update_at_same_time_on_same_component(self):
        call_count = Value("i", 0)
        timestamp_1 = Value("d", -5)
        timestamp_2 = Value("d", -5)

        app = Dash()
        app.layout = html.Div(
            [
                html.Div(id="container"),
                html.Button("Click", id="button-1", n_clicks=0, n_clicks_timestamp=-1),
                html.Button("Click", id="button-2", n_clicks=0, n_clicks_timestamp=-1),
            ]
        )

        @app.callback(
            Output("container", "children"),
            [
                Input("button-1", "n_clicks"),
                Input("button-1", "n_clicks_timestamp"),
                Input("button-2", "n_clicks"),
                Input("button-2", "n_clicks_timestamp"),
            ],
        )
        def update_output(*args):
            call_count.value += 1
            timestamp_1.value = args[1]
            timestamp_2.value = args[3]
            return "{}, {}".format(args[0], args[2])

        self.startServer(app)

        self.wait_for_element_by_css_selector("#container")
        time.sleep(2)
        self.wait_for_text_to_equal("#container", "0, 0")
        self.assertEqual(timestamp_1.value, -1)
        self.assertEqual(timestamp_2.value, -1)
        self.assertEqual(call_count.value, 1)
        self.percy_snapshot("button initialization 1")

        self.driver.find_element_by_css_selector("#button-1").click()
        time.sleep(2)
        self.wait_for_text_to_equal("#container", "1, 0")
        self.assertTrue(timestamp_1.value > ((time.time() - (24 * 60 * 60)) * 1000))
        self.assertEqual(timestamp_2.value, -1)
        self.assertEqual(call_count.value, 2)
        self.percy_snapshot("button-1 click")
        prev_timestamp_1 = timestamp_1.value

        self.driver.find_element_by_css_selector("#button-2").click()
        time.sleep(2)
        self.wait_for_text_to_equal("#container", "1, 1")
        self.assertEqual(timestamp_1.value, prev_timestamp_1)
        self.assertTrue(timestamp_2.value > ((time.time() - 24 * 60 * 60) * 1000))
        self.assertEqual(call_count.value, 3)
        self.percy_snapshot("button-2 click")
        prev_timestamp_2 = timestamp_2.value

        self.driver.find_element_by_css_selector("#button-2").click()
        time.sleep(2)
        self.wait_for_text_to_equal("#container", "1, 2")
        self.assertEqual(timestamp_1.value, prev_timestamp_1)
        self.assertTrue(timestamp_2.value > prev_timestamp_2)
        self.assertTrue(timestamp_2.value > timestamp_1.value)
        self.assertEqual(call_count.value, 4)
        self.percy_snapshot("button-2 click again")

    def test_request_hooks(self):
        app = Dash(__name__)

        app.index_string = """<!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
            </head>
            <body>
                <div>Testing custom DashRenderer</div>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    <script id="_dash-renderer" type"application/json">
                        const renderer = new DashRenderer({
                            request_pre: (payload) => {
                                var output = document.getElementById('output-pre')
                                var outputPayload = document.getElementById('output-pre-payload')
                                if(output) {
                                    output.innerHTML = 'request_pre changed this text!';
                                }
                                if(outputPayload) {
                                    outputPayload.innerHTML = JSON.stringify(payload);
                                }
                            },
                            request_post: (payload, response) => {
                                var output = document.getElementById('output-post')
                                var outputPayload = document.getElementById('output-post-payload')
                                var outputResponse = document.getElementById('output-post-response')
                                if(output) {
                                    output.innerHTML = 'request_post changed this text!';
                                }
                                if(outputPayload) {
                                    outputPayload.innerHTML = JSON.stringify(payload);
                                }
                                if(outputResponse) {
                                    outputResponse.innerHTML = JSON.stringify(response);
                                }
                            }
                        })
                    </script>
                </footer>
                <div>With request hooks</div>
            </body>
        </html>"""

        app.layout = html.Div(
            [
                dcc.Input(id="input", value="initial value"),
                html.Div(
                    html.Div(
                        [
                            html.Div(id="output-1"),
                            html.Div(id="output-pre"),
                            html.Div(id="output-pre-payload"),
                            html.Div(id="output-post"),
                            html.Div(id="output-post-payload"),
                            html.Div(id="output-post-response"),
                        ]
                    )
                ),
            ]
        )

        @app.callback(Output("output-1", "children"), [Input("input", "value")])
        def update_output(value):
            return value

        self.startServer(app)

        input1 = self.wait_for_element_by_css_selector("#input")
        initialValue = input1.get_attribute("value")

        action = ActionChains(self.driver)
        action.click(input1)
        action = action.send_keys(Keys.BACKSPACE * len(initialValue))

        action.send_keys("fire request hooks").perform()

        self.wait_for_text_to_equal("#output-1", "fire request hooks")
        self.wait_for_text_to_equal("#output-pre", "request_pre changed this text!")
        self.wait_for_text_to_equal(
            "#output-pre-payload",
            '{"output":"output-1.children","changedPropIds":["input.value"],"inputs":[{"id":"input","property":"value","value":"fire request hooks"}]}',
        )
        self.wait_for_text_to_equal("#output-post", "request_post changed this text!")
        self.wait_for_text_to_equal(
            "#output-post-payload",
            '{"output":"output-1.children","changedPropIds":["input.value"],"inputs":[{"id":"input","property":"value","value":"fire request hooks"}]}',
        )
        self.wait_for_text_to_equal(
            "#output-post-response", '{"props":{"children":"fire request hooks"}}'
        )
        self.percy_snapshot(name="request-hooks render")

    def test_graphs_in_tabs_do_not_share_state(self):
        app = Dash()

        app.config.suppress_callback_exceptions = True

        app.layout = html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    children=[
                        dcc.Tab(label="Tab 1", value="tab1", id="tab1"),
                        dcc.Tab(label="Tab 2", value="tab2", id="tab2"),
                    ],
                    value="tab1",
                ),
                # Tab content
                html.Div(id="tab_content"),
            ]
        )
        tab1_layout = [
            html.Div(
                [
                    dcc.Graph(
                        id="graph1",
                        figure={
                            "data": [{"x": [1, 2, 3], "y": [5, 10, 6], "type": "bar"}]
                        },
                    )
                ]
            ),
            html.Pre(id="graph1_info"),
        ]

        tab2_layout = [
            html.Div(
                [
                    dcc.Graph(
                        id="graph2",
                        figure={
                            "data": [{"x": [4, 3, 2], "y": [5, 10, 6], "type": "bar"}]
                        },
                    )
                ]
            ),
            html.Pre(id="graph2_info"),
        ]

        @app.callback(
            Output(component_id="graph1_info", component_property="children"),
            [Input(component_id="graph1", component_property="clickData")],
        )
        def display_hover_data(hover_data):
            return json.dumps(hover_data)

        @app.callback(
            Output(component_id="graph2_info", component_property="children"),
            [Input(component_id="graph2", component_property="clickData")],
        )
        def display_hover_data_2(hover_data):
            return json.dumps(hover_data)

        @app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
        def render_content(tab):
            if tab == "tab1":
                return tab1_layout
            elif tab == "tab2":
                return tab2_layout
            else:
                return tab1_layout

        self.startServer(app)

        self.wait_for_element_by_css_selector("#graph1:not(.dash-graph--pending)")

        self.driver.find_elements_by_css_selector("#graph1:not(.dash-graph--pending)")[
            0
        ].click()

        graph_1_expected_clickdata = {
            "points": [
                {
                    "curveNumber": 0,
                    "pointNumber": 1,
                    "pointIndex": 1,
                    "x": 2,
                    "y": 10,
                    "label": 2,
                    "value": 10,
                }
            ]
        }

        graph_2_expected_clickdata = {
            "points": [
                {
                    "curveNumber": 0,
                    "pointNumber": 1,
                    "pointIndex": 1,
                    "x": 3,
                    "y": 10,
                    "label": 3,
                    "value": 10,
                }
            ]
        }

        self.wait_for_text_to_equal(
            "#graph1_info", json.dumps(graph_1_expected_clickdata)
        )

        self.driver.find_elements_by_css_selector("#tab2")[0].click()

        self.wait_for_element_by_css_selector("#graph2:not(.dash-graph--pending)")

        self.driver.find_elements_by_css_selector("#graph2:not(.dash-graph--pending)")[
            0
        ].click()

        self.wait_for_text_to_equal(
            "#graph2_info", json.dumps(graph_2_expected_clickdata)
        )
