import base64
from datetime import datetime
import io
import itertools
from multiprocessing import Value
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
from textwrap import dedent
import time
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc

from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console


class Tests(IntegrationTests):
    def setUp(self):
        pass

    def wait_for_element_by_css_selector(self, selector):
        start_time = time.time()
        error = None
        while time.time() < start_time + 20:
            try:
                return self.driver.find_element_by_css_selector(selector)
            except Exception as e:
                error = e
            self.driver.implicitly_wait(1)
        raise error

    def wait_for_text_to_equal(self, selector, assertion_text):
        start_time = time.time()
        error = None
        while time.time() < start_time + 20:
            el = self.wait_for_element_by_css_selector(selector)
            try:
                return self.assertEqual(el.text, assertion_text)
            except Exception as e:
                error = e
            time.sleep(0.25)
        raise error

    def snapshot(self, name):
        if 'PERCY_PROJECT' in os.environ and 'PERCY_TOKEN' in os.environ:
            python_version = sys.version.split(' ')[0]
            print('Percy Snapshot {}'.format(python_version))
            self.percy_runner.snapshot(name=name)

    def test_click(self):
        call_count = Value('i', 0)

        app = dash.Dash()
        app.layout = html.Div([
            html.Div(id='container'),
            html.Button('Click', id='button', n_clicks=0)
        ])

        @app.callback(Output('container', 'children'), [Input('button', 'n_clicks')])
        def update_output(n_clicks):
            call_count.value += 1
            return 'You have clicked the button {} times'.format(n_clicks)

        self.startServer(app)

        self.wait_for_element_by_css_selector('#container')

        self.wait_for_text_to_equal(
            '#container', 'You have clicked the button 0 times')
        self.assertEqual(call_count.value, 1)
        self.snapshot('button initialization')

        self.driver.find_element_by_css_selector('#button').click()

        self.wait_for_text_to_equal(
            '#container', 'You have clicked the button 1 times')
        self.assertEqual(call_count.value, 2)
        self.snapshot('button click')


    def test_click_prev(self):
        call_count = Value('i', 0)
        timestamp_1 = Value('d', -5)
        timestamp_2 = Value('d', -5)

        app = dash.Dash()
        app.layout = html.Div([
            html.Div(id='container'),
            html.Button('Click', id='button-1', n_clicks=0, n_clicks_timestamp=-1),
            html.Button('Click', id='button-2', n_clicks=0, n_clicks_timestamp=-1)
        ])

        @app.callback(
            Output('container', 'children'),
            [Input('button-1', 'n_clicks'),
             Input('button-1', 'n_clicks_timestamp'),
             Input('button-2', 'n_clicks'),
             Input('button-2', 'n_clicks_timestamp')])
        def update_output(*args):
            print(args)
            call_count.value += 1
            timestamp_1.value = args[1]
            timestamp_2.value = args[3]
            return '{}, {}'.format(args[0], args[2])

        self.startServer(app)

        self.wait_for_element_by_css_selector('#container')
        time.sleep(2)
        self.wait_for_text_to_equal('#container', '0, 0')
        self.assertEqual(timestamp_1.value, -1)
        self.assertEqual(timestamp_2.value, -1)
        self.assertEqual(call_count.value, 1)
        self.snapshot('button initialization 1')

        self.driver.find_element_by_css_selector('#button-1').click()
        time.sleep(2)
        self.wait_for_text_to_equal('#container', '1, 0')
        print(timestamp_1.value)
        print((time.time() - (24 * 60 * 60)) * 1000)
        self.assertTrue(
            timestamp_1.value >
            ((time.time() - (24 * 60 * 60)) * 1000))
        self.assertEqual(timestamp_2.value, -1)
        self.assertEqual(call_count.value, 2)
        self.snapshot('button-1 click')
        prev_timestamp_1 = timestamp_1.value

        self.driver.find_element_by_css_selector('#button-2').click()
        time.sleep(2)
        self.wait_for_text_to_equal('#container', '1, 1')
        self.assertEqual(timestamp_1.value, prev_timestamp_1)
        self.assertTrue(
            timestamp_2.value >
            ((time.time() - 24 * 60 * 60) * 1000))
        self.assertEqual(call_count.value, 3)
        self.snapshot('button-2 click')
        prev_timestamp_2 = timestamp_2.value

        self.driver.find_element_by_css_selector('#button-2').click()
        time.sleep(2)
        self.wait_for_text_to_equal('#container', '1, 2')
        self.assertEqual(timestamp_1.value, prev_timestamp_1)
        self.assertTrue(
            timestamp_2.value >
            prev_timestamp_2)
        self.assertTrue(timestamp_2.value > timestamp_1.value)
        self.assertEqual(call_count.value, 4)
        self.snapshot('button-2 click again')
