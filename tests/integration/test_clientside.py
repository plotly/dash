# -*- coding: UTF-8 -*-
import os
import textwrap

import dash
from dash import Dash
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash.development.base_component import Component
import dash_html_components as html
import dash_core_components as dcc
import dash_renderer_test_components

from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .IntegrationTests import IntegrationTests
from .utils import wait_for
from multiprocessing import Value
import time
import re
import itertools
import json
import string
import plotly
import requests


TIMEOUT = 20


class Tests(IntegrationTests):
    def setUp(self):
        pass

    def wait_for_style_to_equal(self, selector, style, assertion_style, timeout=TIMEOUT):
        start = time.time()
        exception = Exception('Time ran out, {} on {} not found'.format(
            assertion_style, selector))
        while time.time() < start + timeout:
            element = self.wait_for_element_by_css_selector(selector)
            try:
                self.assertEqual(
                    assertion_style, element.value_of_css_property(style))
            except Exception as e:
                exception = e
            else:
                return
            time.sleep(0.1)

        raise exception

    def wait_for_element_by_css_selector(self, selector, timeout=TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector)),
            'Could not find element with selector "{}"'.format(selector)
        )

    def wait_for_text_to_equal(self, selector, assertion_text, timeout=TIMEOUT):
        self.wait_for_element_by_css_selector(selector)
        WebDriverWait(self.driver, timeout).until(
            lambda *args: (
                (str(self.wait_for_element_by_css_selector(selector).text)
                 == assertion_text) or
                (str(self.wait_for_element_by_css_selector(
                    selector).get_attribute('value')) == assertion_text)
            ),
            "Element '{}' text expects to equal '{}' but it didn't".format(
                selector,
                assertion_text
            )
        )

    def clear_input(self, input_element):
        (
            ActionChains(self.driver)
            .click(input_element)
            .send_keys(Keys.HOME)
            .key_down(Keys.SHIFT)
            .send_keys(Keys.END)
            .key_up(Keys.SHIFT)
            .send_keys(Keys.DELETE)
        ).perform()

    def request_queue_assertions(
            self, check_rejected=True, expected_length=None):
        request_queue = self.driver.execute_script(
            'return window.store.getState().requestQueue'
        )
        self.assertTrue(
            all([
                (r['status'] == 200)
                for r in request_queue
            ])
        )

        if check_rejected:
            self.assertTrue(
                all([
                    (r['rejected'] is False)
                    for r in request_queue
                ])
            )

        if expected_length is not None:
            self.assertEqual(len(request_queue), expected_length)

    def test_simple_clientside_serverside_callback(self):
        app = dash.Dash(__name__, assets_folder='clientside_assets')

        app.layout = html.Div([
            dcc.Input(id='input'),
            html.Div(id='output-clientside'),
            html.Div(id='output-serverside')
        ])

        @app.callback(
            Output('output-serverside', 'children'),
            [Input('input', 'value')])
        def update_output(value):
            return 'Server says "{}"'.format(value)

        app.clientside_callback(
            ClientsideFunction(
                namespace='clientside',
                function_name='display'
            ),
            Output('output-clientside', 'children'),
            [Input('input', 'value')]
        )

        self.startServer(app)

        input = self.wait_for_element_by_css_selector('#input')
        self.wait_for_text_to_equal('#output-serverside', 'Server says "None"')
        self.wait_for_text_to_equal(
            '#output-clientside', 'Client says "undefined"'
        )

        input.send_keys('hello world')
        self.wait_for_text_to_equal(
            '#output-serverside', 'Server says "hello world"'
        )
        self.wait_for_text_to_equal(
            '#output-clientside', 'Client says "hello world"'
        )

    def test_chained_serverside_clientside_callbacks(self):
        app = dash.Dash(__name__, assets_folder='clientside_assets')

        app.layout = html.Div([

            html.Label('x'),
            dcc.Input(id='x', value=3),

            html.Label('y'),
            dcc.Input(id='y', value=6),

            # clientside
            html.Label('x + y (clientside)'),
            dcc.Input(id='x-plus-y'),

            # server-side
            html.Label('x+y / 2 (serverside)'),
            dcc.Input(id='x-plus-y-div-2'),

            # server-side
            html.Div([
                html.Label('Display x, y, x+y/2 (serverside)'),
                dcc.Textarea(id='display-all-of-the-values'),
            ]),

            # clientside
            html.Label('Mean(x, y, x+y, x+y/2) (clientside)'),
            dcc.Input(id='mean-of-all-values'),

        ])

        app.clientside_callback(
            ClientsideFunction('clientside', 'add'),
            Output('x-plus-y', 'value'),
            [Input('x', 'value'),
             Input('y', 'value')],
        )

        call_counts = {
            'divide': Value('i', 0),
            'display': Value('i', 0)
        }

        @app.callback(Output('x-plus-y-div-2', 'value'),
                      [Input('x-plus-y', 'value')])
        def divide_by_two(value):
            call_counts['divide'].value += 1
            return float(value) / 2.0

        @app.callback(Output('display-all-of-the-values', 'value'),
                      [Input('x', 'value'),
                       Input('y', 'value'),
                       Input('x-plus-y', 'value'),
                       Input('x-plus-y-div-2', 'value')])
        def display_all(*args):
            call_counts['display'].value += 1
            return '\n'.join([str(a) for a in args])

        app.clientside_callback(
            ClientsideFunction('clientside', 'mean'),
            Output('mean-of-all-values', 'value'),
            [Input('x', 'value'), Input('y', 'value'),
             Input('x-plus-y', 'value'), Input('x-plus-y-div-2', 'value')],
        )

        self.startServer(app)

        test_cases = [
            ['#x', '3'],
            ['#y', '6'],
            ['#x-plus-y', '9'],
            ['#x-plus-y-div-2', '4.5'],
            ['#display-all-of-the-values', '3\n6\n9\n4.5'],
            ['#mean-of-all-values', str((3 + 6 + 9 + 4.5) / 4.0)],
        ]
        for test_case in test_cases:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        self.assertEqual(call_counts['display'].value, 1)
        self.assertEqual(call_counts['divide'].value, 1)

        x_input = self.wait_for_element_by_css_selector('#x')
        x_input.send_keys('1')

        test_cases = [
            ['#x', '31'],
            ['#y', '6'],
            ['#x-plus-y', '37'],
            ['#x-plus-y-div-2', '18.5'],
            ['#display-all-of-the-values', '31\n6\n37\n18.5'],
            ['#mean-of-all-values', str((31 + 6 + 37 + 18.5) / 4.0)],
        ]
        for test_case in test_cases:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        self.assertEqual(call_counts['display'].value, 2)
        self.assertEqual(call_counts['divide'].value, 2)

    def test_clientside_exceptions_halt_subsequent_updates(self):
        app = dash.Dash(__name__, assets_folder='clientside_assets')

        app.layout = html.Div([
            dcc.Input(id='first', value=1),
            dcc.Input(id='second'),
            dcc.Input(id='third'),
        ])

        app.clientside_callback(
            ClientsideFunction('clientside', 'add1_break_at_11'),
            Output('second', 'value'),
            [Input('first', 'value')],
        )

        app.clientside_callback(
            ClientsideFunction('clientside', 'add1_break_at_11'),
            Output('third', 'value'),
            [Input('second', 'value')],
        )

        self.startServer(app)

        test_cases = [
            ['#first', '1'],
            ['#second', '2'],
            ['#third', '3'],
        ]
        for test_case in test_cases:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        first_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'first'))
        )
        first_input.send_keys('1')
        # clientside code will prevent the update from occurring
        test_cases = [
            ['#first', '11'],
            ['#second', '2'],
            ['#third', '3']
        ]
        for test_case in test_cases:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        first_input.send_keys('1')

        # the previous clientside code error should not be fatal:
        # subsequent updates should still be able to occur
        test_cases = [
            ['#first', '111'],
            ['#second', '112'],
            ['#third', '113']
        ]
        for test_case in test_cases:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

    def test_clientside_multiple_outputs(self):
        app = dash.Dash(__name__, assets_folder='clientside_assets')

        app.layout = html.Div([
            dcc.Input(id='input', value=1),
            dcc.Input(id='output-1'),
            dcc.Input(id='output-2'),
            dcc.Input(id='output-3'),
            dcc.Input(id='output-4'),
        ])

        app.clientside_callback(
            ClientsideFunction('clientside', 'add_to_four_outputs'),
            [Output('output-1', 'value'),
             Output('output-2', 'value'),
             Output('output-3', 'value'),
             Output('output-4', 'value')],
            [Input('input', 'value')])

        self.startServer(app)

        for test_case in [
            ['#input', '1'],
            ['#output-1', '2'],
            ['#output-2', '3'],
            ['#output-3', '4'],
            ['#output-4', '5']
        ]:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        input = self.wait_for_element_by_css_selector('#input')
        input.send_keys('1')

        for test_case in [
            ['#input', '11'],
            ['#output-1', '12'],
            ['#output-2', '13'],
            ['#output-3', '14'],
            ['#output-4', '15']
        ]:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

    def test_clientside_fails_when_returning_a_promise(self):
        app = dash.Dash(__name__, assets_folder='clientside_assets')

        app.layout = html.Div([
            html.Div(id='input', children='hello'),
            html.Div(id='side-effect'),
            html.Div(id='output', children='output')
        ])

        app.clientside_callback(
            ClientsideFunction('clientside', 'side_effect_and_return_a_promise'),
            Output('output', 'children'),
            [Input('input', 'children')])

        self.startServer(app)

        self.wait_for_text_to_equal('#input', 'hello')
        self.wait_for_text_to_equal('#side-effect', 'side effect')
        self.wait_for_text_to_equal('#output', 'output')
