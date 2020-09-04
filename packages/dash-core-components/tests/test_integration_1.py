# -*- coding: utf-8 -*-
import os
import sys
from multiprocessing import Lock
import time
import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from IntegrationTests import IntegrationTests

TIMEOUT = 10


class Test1(IntegrationTests):
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

    def test_loading_slider(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Button(id="test-btn"),
                html.Label(id="test-div", children=["Horizontal Slider"]),
                dcc.Slider(
                    id="horizontal-slider",
                    min=0,
                    max=9,
                    marks={
                        i: "Label {}".format(i) if i == 1 else str(i)
                        for i in range(1, 6)
                    },
                    value=5,
                ),
            ]
        )

        @app.callback(
            Output("horizontal-slider", "value"), [Input("test-btn", "n_clicks")]
        )
        def user_delayed_value(n_clicks):
            with lock:
                return 5

        with lock:
            self.startServer(app)

            self.wait_for_element_by_css_selector(
                '#horizontal-slider[data-dash-is-loading="true"]'
            )

        self.wait_for_element_by_css_selector(
            '#horizontal-slider:not([data-dash-is-loading="true"])'
        )

        with lock:
            self.driver.find_element_by_id("test-btn").click()

            self.wait_for_element_by_css_selector(
                '#horizontal-slider[data-dash-is-loading="true"]'
            )

        self.wait_for_element_by_css_selector(
            '#horizontal-slider:not([data-dash-is-loading="true"])'
        )

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

    def test_horizontal_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Label("Horizontal Slider"),
                dcc.Slider(
                    id="horizontal-slider",
                    min=0,
                    max=9,
                    marks={
                        i: "Label {}".format(i) if i == 1 else str(i)
                        for i in range(1, 6)
                    },
                    value=5,
                ),
            ]
        )
        self.startServer(app)

        self.wait_for_element_by_css_selector("#horizontal-slider")
        self.snapshot("horizontal slider")

        h_slider = self.driver.find_element_by_css_selector(
            '#horizontal-slider div[role="slider"]'
        )
        h_slider.click()

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

    def test_vertical_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Label("Vertical Slider"),
                dcc.Slider(
                    id="vertical-slider",
                    min=0,
                    max=9,
                    marks={
                        i: "Label {}".format(i) if i == 1 else str(i)
                        for i in range(1, 6)
                    },
                    value=5,
                    vertical=True,
                ),
            ],
            style={"height": "500px"},
        )
        self.startServer(app)

        self.wait_for_element_by_css_selector("#vertical-slider")
        self.snapshot("vertical slider")

        v_slider = self.driver.find_element_by_css_selector(
            '#vertical-slider div[role="slider"]'
        )
        v_slider.click()

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

    def test_loading_range_slider(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Button(id="test-btn"),
                html.Label(id="test-div", children=["Horizontal Range Slider"]),
                dcc.RangeSlider(
                    id="horizontal-range-slider",
                    min=0,
                    max=9,
                    marks={
                        i: "Label {}".format(i) if i == 1 else str(i)
                        for i in range(1, 6)
                    },
                    value=[4, 6],
                ),
            ]
        )

        @app.callback(
            Output("horizontal-range-slider", "value"), [Input("test-btn", "n_clicks")]
        )
        def delayed_value(children):
            with lock:
                return [4, 6]

        with lock:
            self.startServer(app)

            self.wait_for_element_by_css_selector(
                '#horizontal-range-slider[data-dash-is-loading="true"]'
            )

        self.wait_for_element_by_css_selector(
            '#horizontal-range-slider:not([data-dash-is-loading="true"])'
        )

        with lock:
            self.driver.find_element_by_id("test-btn").click()

            self.wait_for_element_by_css_selector(
                '#horizontal-range-slider[data-dash-is-loading="true"]'
            )

        self.wait_for_element_by_css_selector(
            '#horizontal-range-slider:not([data-dash-is-loading="true"])'
        )

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

    def test_horizontal_range_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Label("Horizontal Range Slider"),
                dcc.RangeSlider(
                    id="horizontal-range-slider",
                    min=0,
                    max=9,
                    marks={
                        i: "Label {}".format(i) if i == 1 else str(i)
                        for i in range(1, 6)
                    },
                    value=[4, 6],
                ),
            ]
        )
        self.startServer(app)

        self.wait_for_element_by_css_selector("#horizontal-range-slider")
        self.snapshot("horizontal range slider")

        h_slider_1 = self.driver.find_element_by_css_selector(
            '#horizontal-range-slider div.rc-slider-handle-1[role="slider"]'
        )
        h_slider_1.click()

        h_slider_2 = self.driver.find_element_by_css_selector(
            '#horizontal-range-slider div.rc-slider-handle-2[role="slider"]'
        )
        h_slider_2.click()

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

    def test_vertical_range_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.Label("Vertical Range Slider"),
                dcc.RangeSlider(
                    id="vertical-range-slider",
                    min=0,
                    max=9,
                    marks={
                        i: "Label {}".format(i) if i == 1 else str(i)
                        for i in range(1, 6)
                    },
                    value=[4, 6],
                    vertical=True,
                ),
            ],
            style={"height": "500px"},
        )
        self.startServer(app)

        self.wait_for_element_by_css_selector("#vertical-range-slider")
        self.snapshot("vertical range slider")

        v_slider_1 = self.driver.find_element_by_css_selector(
            '#vertical-range-slider div.rc-slider-handle-1[role="slider"]'
        )
        v_slider_1.click()

        v_slider_2 = self.driver.find_element_by_css_selector(
            '#vertical-range-slider div.rc-slider-handle-2[role="slider"]'
        )
        v_slider_2.click()

        for entry in self.get_log():
            raise Exception("browser error logged during test", entry)

    def test_tabs_in_vertical_mode(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    value="tab-3",
                    children=[
                        dcc.Tab(
                            label="Tab one",
                            value="tab-1",
                            id="tab-1",
                            children=[html.Div("Tab One Content")],
                        ),
                        dcc.Tab(
                            label="Tab two",
                            value="tab-2",
                            id="tab-2",
                            children=[html.Div("Tab Two Content")],
                        ),
                        dcc.Tab(
                            label="Tab three",
                            value="tab-3",
                            id="tab-3",
                            children=[html.Div("Tab Three Content")],
                        ),
                    ],
                    vertical=True,
                ),
                html.Div(id="tabs-content"),
            ]
        )

        self.startServer(app=app)
        self.wait_for_text_to_equal("#tab-3", "Tab three")

        self.snapshot("Tabs - vertical mode")

    def test_tabs_without_children(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.H1("Dash Tabs component demo"),
                dcc.Tabs(
                    id="tabs",
                    value="tab-2",
                    children=[
                        dcc.Tab(label="Tab one", value="tab-1", id="tab-1"),
                        dcc.Tab(label="Tab two", value="tab-2", id="tab-2"),
                    ],
                ),
                html.Div(id="tabs-content"),
            ]
        )

        @app.callback(
            dash.dependencies.Output("tabs-content", "children"),
            [dash.dependencies.Input("tabs", "value")],
        )
        def render_content(tab):
            if tab == "tab-1":
                return html.Div([html.H3("Test content 1")], id="test-tab-1")
            elif tab == "tab-2":
                return html.Div([html.H3("Test content 2")], id="test-tab-2")

        self.startServer(app=app)

        self.wait_for_text_to_equal("#tabs-content", "Test content 2")
        self.snapshot("initial tab - tab 2")

        selected_tab = self.wait_for_element_by_css_selector("#tab-1")
        selected_tab.click()
        time.sleep(1)
        self.wait_for_text_to_equal("#tabs-content", "Test content 1")

    def test_tabs_with_children_undefined(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.H1("Dash Tabs component demo"),
                dcc.Tabs(id="tabs", value="tab-1"),
                html.Div(id="tabs-content"),
            ]
        )

        self.startServer(app=app)

        self.wait_for_element_by_css_selector("#tabs-content")

        self.snapshot("Tabs component with children undefined")

    def test_tabs_without_value(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(
            [
                html.H1("Dash Tabs component demo"),
                dcc.Tabs(
                    id="tabs-without-value",
                    children=[
                        dcc.Tab(label="Tab One", value="tab-1"),
                        dcc.Tab(label="Tab Two", value="tab-2"),
                    ],
                ),
                html.Div(id="tabs-content"),
            ]
        )

        @app.callback(
            Output("tabs-content", "children"), [Input("tabs-without-value", "value")]
        )
        def render_content(tab):
            if tab == "tab-1":
                return html.H3("Default selected Tab content 1")
            elif tab == "tab-2":
                return html.H3("Tab content 2")

        self.startServer(app=app)

        self.wait_for_text_to_equal("#tabs-content", "Default selected Tab content 1")

        self.snapshot("Tab 1 should be selected by default")
