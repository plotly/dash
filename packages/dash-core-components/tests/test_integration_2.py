# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import flask
import dash
from multiprocessing import Value
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from dash.exceptions import PreventUpdate
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from IntegrationTests import IntegrationTests

TIMEOUT = 10


class Test2(IntegrationTests):
    def setUp(self):
        pass

    def wait_for_element_by_css_selector(self, selector):
        return WebDriverWait(self.driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def wait_for_text_to_equal(self, selector, assertion_text):
        def text_equal(driver):
            text = driver.find_element_by_css_selector(selector).text
            return text == assertion_text

        WebDriverWait(self.driver, TIMEOUT).until(text_equal)

    def snapshot(self, name):
        if "PERCY_PROJECT" in os.environ and "PERCY_TOKEN" in os.environ:
            python_version = sys.version.split(" ")[0]
            print("Percy Snapshot {}".format(python_version))
            self.percy_runner.snapshot(name=name)

    def test_link_scroll(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Location(id="test-url", refresh=False),
                html.Div(
                    id="push-to-bottom",
                    children=[],
                    style={"display": "block", "height": "200vh"},
                ),
                html.Div(id="page-content"),
                dcc.Link("Test link", href="/test-link", id="test-link"),
            ]
        )

        call_count = Value("i", 0)

        @app.callback(
            Output("page-content", "children"), [Input("test-url", "pathname")]
        )
        def display_page(pathname):
            call_count.value = call_count.value + 1
            return "You are on page {}".format(pathname)

        self.startServer(app=app)

        time.sleep(2)

        # callback is called twice when defined
        self.assertEqual(call_count.value, 2)

        # test if link correctly scrolls back to top of page
        test_link = self.wait_for_element_by_css_selector("#test-link")
        test_link.send_keys(Keys.NULL)
        test_link.click()
        time.sleep(2)

        # test link still fires update on Location
        page_content = self.wait_for_element_by_css_selector("#page-content")
        self.assertNotEqual(page_content.text, "You are on page /")

        self.wait_for_text_to_equal(
            "#page-content", "You are on page /test-link"
        )

        # test if rendered Link's <a> tag has a href attribute
        link_href = test_link.get_attribute("href")
        self.assertEqual(link_href, "http://localhost:8050/test-link")

        # test if callback is only fired once (offset of 2)
        self.assertEqual(call_count.value, 3)

    def test_candlestick(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                html.Button(
                    id="button", children="Update Candlestick", n_clicks=0
                ),
                dcc.Graph(id="graph"),
            ]
        )

        @app.callback(Output("graph", "figure"), [Input("button", "n_clicks")])
        def update_graph(n_clicks):
            return {
                "data": [
                    {
                        "open": [1] * 5,
                        "high": [3] * 5,
                        "low": [0] * 5,
                        "close": [2] * 5,
                        "x": [n_clicks] * 5,
                        "type": "candlestick",
                    }
                ]
            }

        self.startServer(app=app)

        button = self.wait_for_element_by_css_selector("#button")
        self.snapshot("candlestick - initial")
        button.click()
        time.sleep(1)
        self.snapshot("candlestick - 1 click")

        button.click()
        time.sleep(1)
        self.snapshot("candlestick - 2 click")

    def test_graphs_with_different_figures(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Graph(
                    id="example-graph",
                    figure={
                        "data": [
                            {
                                "x": [1, 2, 3],
                                "y": [4, 1, 2],
                                "type": "bar",
                                "name": "SF",
                            },
                            {
                                "x": [1, 2, 3],
                                "y": [2, 4, 5],
                                "type": "bar",
                                "name": u"Montréal",
                            },
                        ],
                        "layout": {"title": "Dash Data Visualization"},
                    },
                ),
                dcc.Graph(
                    id="example-graph-2",
                    figure={
                        "data": [
                            {
                                "x": [20, 24, 33],
                                "y": [5, 2, 3],
                                "type": "bar",
                                "name": "SF",
                            },
                            {
                                "x": [11, 22, 33],
                                "y": [22, 44, 55],
                                "type": "bar",
                                "name": u"Montréal",
                            },
                        ],
                        "layout": {"title": "Dash Data Visualization"},
                    },
                ),
                html.Div(id="restyle-data"),
                html.Div(id="relayout-data"),
            ]
        )

        @app.callback(
            Output("restyle-data", "children"),
            [Input("example-graph", "restyleData")],
        )
        def show_restyle_data(data):
            if data is None:  # ignore initial
                return ""
            return json.dumps(data)

        @app.callback(
            Output("relayout-data", "children"),
            [Input("example-graph", "relayoutData")],
        )
        def show_relayout_data(data):
            if (
                data is None or "autosize" in data
            ):  # ignore initial & auto width
                return ""
            return json.dumps(data)

        self.startServer(app=app)

        # use this opportunity to test restyleData, since there are multiple
        # traces on this graph
        legendToggle = self.driver.find_element_by_css_selector(
            "#example-graph .traces:first-child .legendtoggle"
        )
        legendToggle.click()
        self.wait_for_text_to_equal(
            "#restyle-data", '[{"visible": ["legendonly"]}, [0]]'
        )

        # move snapshot after click, so it's more stable with the wait
        self.snapshot("2 graphs with different figures")

        # and test relayoutData while we're at it
        autoscale = self.driver.find_element_by_css_selector(
            "#example-graph .ewdrag"
        )
        autoscale.click()
        autoscale.click()
        self.wait_for_text_to_equal(
            "#relayout-data", '{"xaxis.autorange": true}'
        )

    def test_interval(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="output"),
                dcc.Interval(id="interval", interval=1, max_intervals=2),
            ]
        )

        @app.callback(
            Output("output", "children"), [Input("interval", "n_intervals")]
        )
        def update_text(n):
            return "{}".format(n)

        self.startServer(app=app)

        # wait for interval to finish
        time.sleep(5)

        self.wait_for_text_to_equal("#output", "2")

    def test_if_interval_can_be_restarted(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Interval(
                    id="interval",
                    interval=100,
                    n_intervals=0,
                    max_intervals=-1,
                ),
                html.Button("Start", id="start", n_clicks_timestamp=-1),
                html.Button("Stop", id="stop", n_clicks_timestamp=-1),
                html.Div(id="output"),
            ]
        )

        @app.callback(
            Output("interval", "max_intervals"),
            [
                Input("start", "n_clicks_timestamp"),
                Input("stop", "n_clicks_timestamp"),
            ],
        )
        def start_stop(start, stop):
            if start < stop:
                return 0
            else:
                return -1

        @app.callback(
            Output("output", "children"), [Input("interval", "n_intervals")]
        )
        def display_data(n_intervals):
            return "Updated {}".format(n_intervals)

        self.startServer(app=app)

        start_button = self.wait_for_element_by_css_selector("#start")
        stop_button = self.wait_for_element_by_css_selector("#stop")

        # interval will start itself, we wait a second before pressing 'stop'
        time.sleep(1)

        # get the output after running it for a bit
        output = self.wait_for_element_by_css_selector("#output")
        stop_button.click()

        time.sleep(1)

        # get the output after it's stopped, it shouldn't be higher than before
        output_stopped = self.wait_for_element_by_css_selector("#output")

        self.wait_for_text_to_equal("#output", output_stopped.text)

        # This test logic is bad
        # same element check for same text will always be true.
        self.assertEqual(output.text, output_stopped.text)

    def _test_confirm(self, app, test_name, add_callback=True):
        count = Value("i", 0)

        if add_callback:

            @app.callback(
                Output("confirmed", "children"),
                [
                    Input("confirm", "submit_n_clicks"),
                    Input("confirm", "cancel_n_clicks"),
                ],
                [
                    State("confirm", "submit_n_clicks_timestamp"),
                    State("confirm", "cancel_n_clicks_timestamp"),
                ],
            )
            def _on_confirmed(
                submit_n_clicks,
                cancel_n_clicks,
                submit_timestamp,
                cancel_timestamp,
            ):
                if not submit_n_clicks and not cancel_n_clicks:
                    return ""
                count.value += 1
                if (submit_timestamp and cancel_timestamp is None) or (
                    submit_timestamp > cancel_timestamp
                ):
                    return "confirmed"
                else:
                    return "canceled"

        self.startServer(app)
        button = self.wait_for_element_by_css_selector("#button")
        self.snapshot(test_name + " -> initial")

        button.click()
        time.sleep(1)
        self.driver.switch_to.alert.accept()

        if add_callback:
            self.wait_for_text_to_equal("#confirmed", "confirmed")
            self.snapshot(test_name + " -> confirmed")

        button.click()
        time.sleep(0.5)
        self.driver.switch_to.alert.dismiss()
        time.sleep(0.5)

        if add_callback:
            self.wait_for_text_to_equal("#confirmed", "canceled")
            self.snapshot(test_name + " -> canceled")

        if add_callback:
            self.assertEqual(
                2,
                count.value,
                "Expected 2 callback but got " + str(count.value),
            )

    def test_confirm(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Button(id="button", children="Send confirm", n_clicks=0),
                dcc.ConfirmDialog(id="confirm", message="Please confirm."),
                html.Div(id="confirmed"),
            ]
        )

        @app.callback(
            Output("confirm", "displayed"), [Input("button", "n_clicks")]
        )
        def on_click_confirm(n_clicks):
            if n_clicks:
                return True

        self._test_confirm(app, "ConfirmDialog")

    def test_confirm_dialog_provider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                dcc.ConfirmDialogProvider(
                    html.Button("click me", id="button"),
                    id="confirm",
                    message="Please confirm.",
                ),
                html.Div(id="confirmed"),
            ]
        )

        self._test_confirm(app, "ConfirmDialogProvider")

    def test_confirm_without_callback(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                dcc.ConfirmDialogProvider(
                    html.Button("click me", id="button"),
                    id="confirm",
                    message="Please confirm.",
                ),
                html.Div(id="confirmed"),
            ]
        )
        self._test_confirm(
            app, "ConfirmDialogProviderWithoutCallback", add_callback=False
        )

    def test_confirm_as_children(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Button(id="button", children="Send confirm"),
                html.Div(id="confirm-container"),
                dcc.Location(id="dummy-location"),
            ]
        )

        @app.callback(
            Output("confirm-container", "children"),
            [Input("button", "n_clicks")],
        )
        def on_click(n_clicks):
            if n_clicks:
                return dcc.ConfirmDialog(
                    displayed=True, id="confirm", message="Please confirm."
                )

        self.startServer(app)

        button = self.wait_for_element_by_css_selector("#button")

        button.click()
        time.sleep(2)

        self.driver.switch_to.alert.accept()

    def test_empty_graph(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Button(id="click", children="Click me"),
                dcc.Graph(
                    id="graph",
                    figure={
                        "data": [
                            dict(x=[1, 2, 3], y=[1, 2, 3], type="scatter")
                        ]
                    },
                ),
            ]
        )

        @app.callback(
            dash.dependencies.Output("graph", "figure"),
            [dash.dependencies.Input("click", "n_clicks")],
            [dash.dependencies.State("graph", "figure")],
        )
        def render_content(click, prev_graph):
            if click:
                return {}
            return prev_graph

        self.startServer(app)
        button = self.wait_for_element_by_css_selector("#click")
        button.click()
        time.sleep(2)  # Wait for graph to re-render
        self.snapshot("render-empty-graph")

    def test_graph_extend_trace(self):
        app = dash.Dash(__name__)

        def generate_with_id(id, data=None):
            if data is None:
                data = [{"x": [0, 1, 2, 3, 4], "y": [0, 0.5, 1, 0.5, 0]}]

            return html.Div(
                [
                    html.P(id),
                    dcc.Graph(id=id, figure=dict(data=data)),
                    html.Div(id="output_{}".format(id)),
                ]
            )

        figs = [
            "trace_will_extend",
            "trace_will_extend_with_no_indices",
            "trace_will_extend_with_max_points",
        ]

        layout = [generate_with_id(id) for id in figs]

        figs.append("trace_will_allow_repeated_extend")
        data = [{"y": [0, 0, 0]}]
        layout.append(generate_with_id(figs[-1], data))

        figs.append("trace_will_extend_selectively")
        data = [
            {"x": [0, 1, 2, 3, 4], "y": [0, 0.5, 1, 0.5, 0]},
            {"x": [0, 1, 2, 3, 4], "y": [1, 1, 1, 1, 1]},
        ]
        layout.append(generate_with_id(figs[-1], data))

        layout.append(
            dcc.Interval(
                id="interval_extendablegraph_update",
                interval=10,
                n_intervals=0,
                max_intervals=1,
            )
        )

        layout.append(
            dcc.Interval(
                id="interval_extendablegraph_extendtwice",
                interval=500,
                n_intervals=0,
                max_intervals=2,
            )
        )

        app.layout = html.Div(layout)

        @app.callback(
            Output("trace_will_allow_repeated_extend", "extendData"),
            [Input("interval_extendablegraph_extendtwice", "n_intervals")],
        )
        def trace_will_allow_repeated_extend(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            return dict(y=[[0.1, 0.2, 0.3, 0.4, 0.5]])

        @app.callback(
            Output("trace_will_extend", "extendData"),
            [Input("interval_extendablegraph_update", "n_intervals")],
        )
        def trace_will_extend(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
            return dict(x=[x_new], y=[y_new]), [0]

        @app.callback(
            Output("trace_will_extend_selectively", "extendData"),
            [Input("interval_extendablegraph_update", "n_intervals")],
        )
        def trace_will_extend_selectively(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
            return dict(x=[x_new], y=[y_new]), [1]

        @app.callback(
            Output("trace_will_extend_with_no_indices", "extendData"),
            [Input("interval_extendablegraph_update", "n_intervals")],
        )
        def trace_will_extend_with_no_indices(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
            return dict(x=[x_new], y=[y_new])

        @app.callback(
            Output("trace_will_extend_with_max_points", "extendData"),
            [Input("interval_extendablegraph_update", "n_intervals")],
        )
        def trace_will_extend_with_max_points(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
            return dict(x=[x_new], y=[y_new]), [0], 7

        for id in figs:

            @app.callback(
                Output("output_{}".format(id), "children"),
                [Input(id, "extendData")],
                [State(id, "figure")],
            )
            def display_data(trigger, fig):
                return json.dumps(fig["data"])

        self.startServer(app)

        comparison = json.dumps(
            [
                dict(
                    x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    y=[0, 0.5, 1, 0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5],
                )
            ]
        )
        self.wait_for_text_to_equal("#output_trace_will_extend", comparison)
        self.wait_for_text_to_equal(
            "#output_trace_will_extend_with_no_indices", comparison
        )
        comparison = json.dumps(
            [
                dict(x=[0, 1, 2, 3, 4], y=[0, 0.5, 1, 0.5, 0]),
                dict(
                    x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                    y=[1, 1, 1, 1, 1, 0.1, 0.2, 0.3, 0.4, 0.5],
                ),
            ]
        )
        self.wait_for_text_to_equal(
            "#output_trace_will_extend_selectively", comparison
        )

        comparison = json.dumps(
            [
                dict(
                    x=[3, 4, 5, 6, 7, 8, 9],
                    y=[0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5],
                )
            ]
        )
        self.wait_for_text_to_equal(
            "#output_trace_will_extend_with_max_points", comparison
        )

        comparison = json.dumps(
            [
                dict(
                    y=[
                        0,
                        0,
                        0,
                        0.1,
                        0.2,
                        0.3,
                        0.4,
                        0.5,
                        0.1,
                        0.2,
                        0.3,
                        0.4,
                        0.5,
                    ]
                )
            ]
        )
        self.wait_for_text_to_equal(
            "#output_trace_will_allow_repeated_extend", comparison
        )

    def test_user_supplied_css(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            className="test-input-css", children=[dcc.Input()]
        )

        self.startServer(app)

        self.wait_for_element_by_css_selector(".test-input-css")
        self.snapshot("styled input - width: 100%, border-color: hotpink")

    def test_logout_btn(self):
        app = dash.Dash(__name__)

        @app.server.route("/_logout", methods=["POST"])
        def on_logout():
            rep = flask.redirect("/logged-out")
            rep.set_cookie("logout-cookie", "", 0)
            return rep

        app.layout = html.Div(
            [
                html.H2("Logout test"),
                dcc.Location(id="location"),
                html.Div(id="content"),
            ]
        )

        @app.callback(
            Output("content", "children"), [Input("location", "pathname")]
        )
        def on_location(location_path):
            if location_path is None:
                raise PreventUpdate

            if "logged-out" in location_path:
                return "Logged out"
            else:

                @flask.after_this_request
                def _insert_cookie(rep):
                    rep.set_cookie("logout-cookie", "logged-in")
                    return rep

                return dcc.LogoutButton(id="logout-btn", logout_url="/_logout")

        self.startServer(app)
        time.sleep(1)
        self.snapshot("Logout button")

        self.assertEqual(
            "logged-in", self.driver.get_cookie("logout-cookie")["value"]
        )
        logout_button = self.wait_for_element_by_css_selector("#logout-btn")
        logout_button.click()
        self.wait_for_text_to_equal("#content", "Logged out")

        self.assertFalse(self.driver.get_cookie("logout-cookie"))

    def test_simple_callback(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="input"),
                html.Div(
                    html.Div([1.5, None, "string", html.Div(id="output-1")])
                ),
            ]
        )

        call_count = Value("i", 0)

        @app.callback(
            Output("output-1", "children"), [Input("input", "value")]
        )
        def update_output(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        input1 = self.wait_for_element_by_css_selector("#input")
        input1.send_keys("hello world")
        output1 = self.wait_for_element_by_css_selector("#output-1")
        self.wait_for_text_to_equal("#output-1", "hello world")
        output1.click()  # Lose focus, no callback sent for value.

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            # plus one for each hello world character
            1 + len("hello world"),
        )

    def test_disabled_tab(self):
        app = dash.Dash(__name__)
        app.layout = html.Div(
            [
                html.H1("Dash Tabs component with disabled tab demo"),
                dcc.Tabs(
                    id="tabs-example",
                    value="tab-2",
                    children=[
                        dcc.Tab(
                            label="Disabled Tab",
                            value="tab-1",
                            id="tab-1",
                            className="test-custom-tab",
                            disabled=True,
                        ),
                        dcc.Tab(
                            label="Active Tab",
                            value="tab-2",
                            id="tab-2",
                            className="test-custom-tab",
                        ),
                    ],
                ),
                html.Div(id="tabs-content-example"),
            ]
        )
        self.startServer(app=app)

        WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "tab-2"))
        )

        WebDriverWait(self.driver, TIMEOUT).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".tab--disabled")
            )
        )

    def test_unmounted_graph_resize(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            children=[
                dcc.Tabs(
                    id="tabs",
                    children=[
                        dcc.Tab(
                            label="Tab one",
                            children=[
                                html.Div(
                                    [
                                        dcc.Graph(
                                            id="eg-graph-1",
                                            figure={
                                                "data": [
                                                    {
                                                        "x": [1, 2, 3],
                                                        "y": [4, 1, 2],
                                                        "type": "scattergl",
                                                        "name": "SF",
                                                    },
                                                    {
                                                        "x": [1, 2, 3],
                                                        "y": [2, 4, 5],
                                                        "type": "scattergl",
                                                        "name": u"Montréal",
                                                    },
                                                ]
                                            },
                                        )
                                    ],
                                    id="graph-tab-1",
                                )
                            ],
                        ),
                        dcc.Tab(
                            label="Tab two",
                            children=[
                                dcc.Graph(
                                    id="eg-graph-2",
                                    figure={
                                        "data": [
                                            {
                                                "x": [1, 2, 3],
                                                "y": [1, 4, 1],
                                                "type": "scattergl",
                                                "name": "SF",
                                            },
                                            {
                                                "x": [1, 2, 3],
                                                "y": [1, 2, 3],
                                                "type": "scattergl",
                                                "name": u"Montréal",
                                            },
                                        ]
                                    },
                                )
                            ],
                            id="graph-tab-2",
                        ),
                    ],
                )
            ]
        )

        self.startServer(app)

        try:
            self.wait_for_element_by_css_selector("#eg-graph-1")
        except Exception as e:
            print(
                self.wait_for_element_by_css_selector(
                    "#_dash-app-content"
                ).get_attribute("innerHTML")
            )
            raise e

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "graph-tab-2"))
        )

        tab_two = self.wait_for_element_by_css_selector("#graph-tab-2")

        tab_two.click()

        # save the current window size
        window_size = self.driver.get_window_size()

        # resize
        self.driver.set_window_size(800, 600)

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

        # set back to original size
        self.driver.set_window_size(
            window_size["width"], window_size["height"]
        )
