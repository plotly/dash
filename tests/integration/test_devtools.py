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
import pytest


TIMEOUT = 20


@pytest.mark.skip(
    reason="flakey with circleci, will readdressing after pytest fixture")
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

    def test_devtools_python_errors(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='python', children='Python exception', n_clicks=0),
            html.Div(id='output')
        ])

        @app.callback(
            Output('output', 'children'),
            [Input('python', 'n_clicks')])
        def update_output(n_clicks):
            if n_clicks == 1:
                1 / 0
            elif n_clicks == 2:
                raise Exception('Special 2 clicks exception')

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
        )

        self.percy_snapshot('devtools - python exception - start')

        self.wait_for_element_by_css_selector('#python').click()
        self.wait_for_text_to_equal('.test-devtools-error-count', '1')
        self.percy_snapshot('devtools - python exception - closed')
        self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()
        self.percy_snapshot('devtools - python exception - open')
        self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()

        self.wait_for_element_by_css_selector('#python').click()
        self.wait_for_text_to_equal('.test-devtools-error-count', '2')
        self.percy_snapshot('devtools - python exception - 2 errors')
        self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()
        self.percy_snapshot('devtools - python exception - 2 errors open')

    def test_devtools_prevent_update(self):
        # raising PreventUpdate shouldn't display the error message
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='python', children='Prevent update', n_clicks=0),
            html.Div(id='output')
        ])

        @app.callback(
            Output('output', 'children'),
            [Input('python', 'n_clicks')])
        def update_output(n_clicks):
            if n_clicks == 1:
                raise PreventUpdate
            if n_clicks == 2:
                raise Exception('An actual python exception')

            return 'button clicks: {}'.format(n_clicks)

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
        )

        self.wait_for_element_by_css_selector('#python').click()
        self.wait_for_element_by_css_selector('#python').click()
        self.wait_for_element_by_css_selector('#python').click()
        self.wait_for_text_to_equal('#output', 'button clicks: 3')

        # two exceptions fired, but only a single exception appeared in the UI:
        # the prevent default was not displayed
        self.wait_for_text_to_equal('.test-devtools-error-count', '1')
        self.percy_snapshot('devtools - prevent update - only a single exception')

    def test_devtools_validation_errors_in_place(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='button', children='update-graph', n_clicks=0),
            dcc.Graph(id='output', figure={'data': [{'y': [3, 1, 2]}]})
        ])

        # animate is a bool property
        @app.callback(
            Output('output', 'animate'),
            [Input('button', 'n_clicks')])
        def update_output(n_clicks):
            if n_clicks == 1:
                return n_clicks

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
        )

        self.wait_for_element_by_css_selector('#button').click()
        self.wait_for_text_to_equal('.test-devtools-error-count', '1')
        self.percy_snapshot('devtools - validation exception - closed')
        self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()
        self.percy_snapshot('devtools - validation exception - open')

    def test_dev_tools_disable_props_check_config(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.P(id='tcid', children='Hello Props Check'),
            dcc.Graph(id='broken', animate=3),  # error ignored by disable
        ])

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
            dev_tools_props_check=False
        )

        self.wait_for_text_to_equal('#tcid', "Hello Props Check")
        self.assertTrue(
            self.driver.find_elements_by_css_selector('#broken svg.main-svg'),
            "graph should be rendered")
        self.assertTrue(
            self.driver.find_elements_by_css_selector('.dash-debug-menu'),
            "the debug menu icon should show up")

        self.percy_snapshot('devtools - disable props check - Graph should render')

    def test_dev_tools_disable_ui_config(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.P(id='tcid', children='Hello Disable UI'),
            dcc.Graph(id='broken', animate=3),  # error ignored by disable
        ])

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
            dev_tools_ui=False
        )

        self.wait_for_text_to_equal('#tcid', "Hello Disable UI")
        logs = self.wait_until_get_log()
        self.assertIn(
            'Invalid argument `animate` passed into Graph', str(logs),
            "the error should present in the console without DEV tools UI")

        self.assertFalse(
            self.driver.find_elements_by_css_selector('.dash-debug-menu'),
            "the debug menu icon should NOT show up")

        self.percy_snapshot('devtools - disable dev tools UI - no debug menu')

    def test_devtools_validation_errors_creation(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='button', children='update-graph', n_clicks=0),
            html.Div(id='output')
        ])

        # animate is a bool property
        @app.callback(
            Output('output', 'children'),
            [Input('button', 'n_clicks')])
        def update_output(n_clicks):
            if n_clicks == 1:
                return dcc.Graph(
                    id='output',
                    animate=0,
                    figure={'data': [{'y': [3, 1, 2]}]}
                )

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
        )

        self.wait_for_element_by_css_selector('#button').click()
        self.wait_for_text_to_equal('.test-devtools-error-count', '1')
        self.percy_snapshot('devtools - validation creation exception - closed')
        self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()
        self.percy_snapshot('devtools - validation creation exception - open')

    def test_devtools_multiple_outputs(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Button(
                id='multi-output',
                children='trigger multi output update',
                n_clicks=0
            ),
            html.Div(id='multi-1'),
            html.Div(id='multi-2'),
        ])

        @app.callback(
            [Output('multi-1', 'children'), Output('multi-2', 'children')],
            [Input('multi-output', 'n_clicks')])
        def update_outputs(n_clicks):
            if n_clicks == 0:
                return [
                    'Output 1 - {} Clicks'.format(n_clicks),
                    'Output 2 - {} Clicks'.format(n_clicks),
                ]
            else:
                n_clicks / 0

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
        )

        self.wait_for_element_by_css_selector('#multi-output').click()
        self.wait_for_text_to_equal('.test-devtools-error-count', '1')
        self.percy_snapshot('devtools - multi output python exception - closed')
        self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()
        self.percy_snapshot('devtools - multi output python exception - open')

    def test_devtools_validation_errors(self):
        app = dash.Dash(__name__)

        test_cases = {
            'not-boolean': {
                'fail': True,
                'name': 'simple "not a boolean" check',
                'component': dcc.Graph,
                'props': {
                    'animate': 0
                }
            },

            'missing-required-nested-prop': {
                'fail': True,
                'name': 'missing required "value" inside options',
                'component': dcc.Checklist,
                'props': {
                    'options': [{
                        'label': 'hello'
                    }],
                    'values': ['test']
                }
            },

            'invalid-nested-prop': {
                'fail': True,
                'name': 'invalid nested prop',
                'component': dcc.Checklist,
                'props': {
                    'options': [{
                        'label': 'hello',
                        'value': True
                    }],
                    'values': ['test']
                }
            },

            'invalid-arrayOf': {
                'fail': True,
                'name': 'invalid arrayOf',
                'component': dcc.Checklist,
                'props': {
                    'options': 'test',
                    'values': []
                }
            },

            'invalid-oneOf': {
                'fail': True,
                'name': 'invalid oneOf',
                'component': dcc.Input,
                'props': {
                    'type': 'test',
                }
            },

            'invalid-oneOfType': {
                'fail': True,
                'name': 'invalid oneOfType',
                'component': dcc.Input,
                'props': {
                    'max': True,
                }
            },

            'invalid-shape-1': {
                'fail': True,
                'name': 'invalid key within nested object',
                'component': dcc.Graph,
                'props': {
                    'config': {
                        'asdf': 'that'
                    }
                }
            },

            'invalid-shape-2': {
                'fail': True,
                'name': 'nested object with bad value',
                'component': dcc.Graph,
                'props': {
                    'config': {
                        'edits': {
                            'legendPosition': 'asdf'
                        }
                    }
                }
            },

            'invalid-shape-3': {
                'fail': True,
                'name': 'invalid oneOf within nested object',
                'component': dcc.Graph,
                'props': {
                    'config': {
                        'toImageButtonOptions': {
                            'format': 'asdf'
                        }
                    }
                }
            },

            'invalid-shape-4': {
                'fail': True,
                'name': 'invalid key within deeply nested object',
                'component': dcc.Graph,
                'props': {
                    'config': {
                        'toImageButtonOptions': {
                            'asdf': 'test'
                        }
                    }
                }
            },

            'invalid-shape-5': {
                'fail': True,
                'name': 'invalid not required key',
                'component': dcc.Dropdown,
                'props': {
                    'options': [
                        {
                            'label': 'new york',
                            'value': 'ny',
                            'typo': 'asdf'
                        }
                    ]
                }
            },

            'string-not-list': {
                'fail': True,
                'name': 'string-not-a-list',
                'component': dcc.Checklist,
                'props': {
                    'options': [{
                        'label': 'hello',
                        'value': 'test'
                    }],
                    'values': 'test'
                }
            },

            'no-properties': {
                'fail': False,
                'name': 'no properties',
                'component': dcc.Graph,
                'props': {}
            },

            'nested-children': {
                'fail': True,
                'name': 'nested children',
                'component': html.Div,
                'props': {'children': [[1]]}
            },

            'deeply-nested-children': {
                'fail': True,
                'name': 'deeply nested children',
                'component': html.Div,
                'props': {'children': html.Div([
                    html.Div([
                        3,
                        html.Div([[10]])
                    ])
                ])}
            },

            'dict': {
                'fail': True,
                'name': 'returning a dictionary',
                'component': html.Div,
                'props': {
                    'children': {'hello': 'world'}
                }
            },

            'nested-prop-failure': {
                'fail': True,
                'name': 'nested string instead of number/null',
                'component': dcc.Graph,
                'props': {
                    'figure': {'data': [{}]},
                    'config': {
                        'toImageButtonOptions': {
                            'width': None,
                            'height': 'test'
                        }
                    }
                }
            },

            'allow-null': {
                'fail': False,
                'name': 'nested null',
                'component': dcc.Graph,
                'props': {
                    'figure': {'data': [{}]},
                    'config': {
                        'toImageButtonOptions': {
                            'width': None,
                            'height': None
                        }
                    }
                }
            },

            'allow-null-2': {
                'fail': False,
                'name': 'allow null as value',
                'component': dcc.Dropdown,
                'props': {
                    'value': None
                }
            },

            'allow-null-3': {
                'fail': False,
                'name': 'allow null in properties',
                'component': dcc.Input,
                'props': {
                    'value': None
                }
            },

            'allow-null-4': {
                'fail': False,
                'name': 'allow null in oneOfType',
                'component': dcc.Store,
                'props': {
                    'id': 'store',
                    'data': None
                }
            },

            'long-property-string': {
                'fail': True,
                'name': 'long property string with id',
                'component': html.Div,
                'props': {
                    'id': 'pink div',
                    'style': 'color: hotpink; ' * 1000
                }
            },

            'multiple-wrong-values': {
                'fail': True,
                'name': 'multiple wrong props',
                'component': dcc.Dropdown,
                'props': {
                    'id': 'dropdown',
                    'value': 10,
                    'options': 'asdf',
                }
            },

            'boolean-html-properties': {
                'fail': True,
                'name': 'dont allow booleans for dom props',
                'component': html.Div,
                'props': {
                    'contentEditable': True
                }
            },

            'allow-exact-with-optional-and-required-1': {
                'fail': False,
                'name': 'allow exact with optional and required keys',
                'component': dcc.Dropdown,
                'props': {
                    'options': [{
                        'label': 'new york',
                        'value': 'ny',
                        'disabled': False
                    }]
                }
            },

            'allow-exact-with-optional-and-required-2': {
                'fail': False,
                'name': 'allow exact with optional and required keys 2',
                'component': dcc.Dropdown,
                'props': {
                    'options': [{
                        'label': 'new york',
                        'value': 'ny'
                    }]
                }
            }

        }

        app.layout = html.Div([
            html.Div(id='content'),
            dcc.Location(id='location'),
        ])

        @app.callback(
            Output('content', 'children'),
            [Input('location', 'pathname')])
        def display_content(pathname):
            if pathname is None or pathname == '/':
                return 'Initial state'
            test_case = test_cases[pathname.strip('/')]
            return html.Div(
                id='new-component',
                children=test_case['component'](**test_case['props'])
            )

        self.startServer(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
        )

        for test_case_id in test_cases:
            self.driver.get('http://localhost:8050/{}'.format(test_case_id))
            if test_cases[test_case_id]['fail']:
                try:
                    self.wait_for_element_by_css_selector('.test-devtools-error-toggle').click()
                except Exception as e:
                    raise Exception('Error popup not shown for {}'.format(test_case_id))
                self.percy_snapshot(
                    'devtools validation exception: {}'.format(
                        test_cases[test_case_id]['name']
                    )
                )
            else:
                try:
                    self.wait_for_element_by_css_selector('#new-component')
                except Exception as e:
                    raise Exception('Component not rendered in {}'.format(test_case_id))
                self.percy_snapshot(
                    'devtools validation no exception: {}'.format(
                        test_cases[test_case_id]['name']
                    )
                )
