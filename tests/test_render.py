import os
import textwrap

import dash
from dash import Dash
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash.development.base_component import Component
import dash_html_components as html
import dash_core_components as dcc

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
                 (str(self.wait_for_element_by_css_selector(selector).get_attribute('value'))
                  == assertion_text)
            ),
            "Element '{}' text was supposed to equal '{}' but it didn't".format(
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


    def test_initial_state(self):
        app = Dash(__name__)
        my_class_attrs = {
            'id': 'p.c.4',
            'className': 'my-class',
            'title': 'tooltip',
            'style': {'color': 'red', 'fontSize': 30},
        }
        app.layout = html.Div([
            'Basic string',
            3.14,
            True,
            None,
            html.Div('Child div with basic string', **my_class_attrs),
            html.Div(id='p.c.5'),
            html.Div([
                html.Div('Grandchild div', id='p.c.6.p.c.0'),
                html.Div([
                    html.Div('Great grandchild', id='p.c.6.p.c.1.p.c.0'),
                    3.14159,
                    'another basic string'
                ], id='p.c.6.p.c.1'),
                html.Div([
                    html.Div(
                        html.Div([
                            html.Div([
                                html.Div(
                                    id='p.c.6.p.c.2.p.c.0.p.c.p.c.0.p.c.0'
                                ),
                                '',
                                html.Div(
                                    id='p.c.6.p.c.2.p.c.0.p.c.p.c.0.p.c.2'
                                )
                            ], id='p.c.6.p.c.2.p.c.0.p.c.p.c.0')
                        ], id='p.c.6.p.c.2.p.c.0.p.c'),
                        id='p.c.6.p.c.2.p.c.0'
                    )
                ], id='p.c.6.p.c.2')
            ], id='p.c.6')
        ])

        self.startServer(app)
        el = self.wait_for_element_by_css_selector('#react-entry-point')

        _dash_app_content_html = os.path.join(
            os.path.dirname(__file__),
            'test_assets', 'initial_state_dash_app_content.html')
        with open(_dash_app_content_html) as fp:
            rendered_dom = BeautifulSoup(fp.read(), 'lxml')
        fetched_dom = BeautifulSoup(el.get_attribute('outerHTML'), 'lxml')

        self.assertEqual(
            fetched_dom.decode(), rendered_dom.decode(),
            "the fetching rendered dom is expected ")

        # Check that no errors or warnings were displayed
        self.assertTrue(self.is_console_clean())

        self.assertEqual(
            self.driver.execute_script(
                'return JSON.parse(JSON.stringify('
                'window.store.getState().layout'
                '))'
            ),
            json.loads(json.dumps(app.layout, cls=plotly.utils.PlotlyJSONEncoder)),
            "the state layout is identical to app.layout"
        )

        r = requests.get('http://localhost:8050/_dash-dependencies')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.json(), [],
            "no dependencies present in app as no callbacks are defined"

        )

        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().paths'
            ),
            {
                abbr: [
                    int(token) if token in string.digits
                    else token.replace('p', 'props').replace('c', 'children')
                    for token in abbr.split('.')
                ]
                for abbr in (
                    child.get('id')
                    for child in fetched_dom.find(
                    id='react-entry-point').findChildren(id=True)
                )
            },
            "paths should refect to the component hierarchy"
        )

        self.request_queue_assertions(0)

        self.percy_snapshot(name='layout')

        self.assertTrue(self.is_console_clean())

    def test_array_of_falsy_child(self):
        app = Dash(__name__)
        app.layout = html.Div(id='nully-wrapper', children=[0])

        self.startServer(app)

        self.wait_for_text_to_equal('#nully-wrapper', '0')

        self.assertTrue(self.is_console_clean())

    def test_of_falsy_child(self):
        app = Dash(__name__)
        app.layout = html.Div(id='nully-wrapper', children=0)

        self.startServer(app)

        self.wait_for_text_to_equal('#nully-wrapper', '0')

        self.assertTrue(self.is_console_clean())

    def test_simple_callback(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    1.5,
                    None,
                    'string',
                    html.Div(id='output-1')
                ])
            )
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        self.wait_for_text_to_equal('#output-1', 'initial value')
        self.percy_snapshot(name='simple-callback-1')

        input1 = self.wait_for_element_by_css_selector('#input')
        self.clear_input(input1)

        input1.send_keys('hello world')

        self.wait_for_text_to_equal('#output-1', 'hello world')
        self.percy_snapshot(name='simple-callback-2')

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value + clear is now one
            2 +
            # one for each hello world character
            len('hello world')
        )

        self.request_queue_assertions(
            expected_length=1,
            check_rejected=False)

        self.assertTrue(self.is_console_clean())

    def test_callbacks_generating_children(self):
        ''' Modify the DOM tree by adding new
        components in the callbacks
        '''

        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'children'), [Input('input', 'value')])
        def pad_output(input):
            return html.Div([
                dcc.Input(
                    id='sub-input-1',
                    value='sub input initial value'
                ),
                html.Div(id='sub-output-1')
            ])

        call_count = Value('i', 0)

        # these components don't exist in the initial render
        app.config.supress_callback_exceptions = True

        @app.callback(
            Output('sub-output-1', 'children'),
            [Input('sub-input-1', 'value')]
        )
        def update_input(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        wait_for(lambda: call_count.value == 1)

        pad_input, pad_div = BeautifulSoup(
            self.driver.find_element_by_css_selector(
                '#react-entry-point').get_attribute('innerHTML'),
            'lxml').select_one('#output > div').contents

        self.assertTrue(
            pad_input.attrs == {'id': 'sub-input-1', 'value': 'sub input initial value'}
                and pad_input.name == 'input',
            "pad input is correctly rendered")

        self.assertTrue(
            pad_div.text == pad_input.attrs['value']
                and pad_div.get('id') == 'sub-output-1',
            "the sub-output-1 content reflects to sub-input-1 value"
        )

        self.percy_snapshot(name='callback-generating-function-1')

        # the paths should include these new output IDs
        self.assertEqual(
            self.driver.execute_script('return window.store.getState().paths'),
            {
                'input': [
                    'props', 'children', 0
                ],
                'output': ['props', 'children', 1],
                'sub-input-1': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 0
                ],
                'sub-output-1': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 1
                ]
            }
        )

        # editing the input should modify the sub output
        sub_input = self.driver.find_element_by_id('sub-input-1')

        sub_input.send_keys('deadbeef')
        self.wait_for_text_to_equal(
            '#sub-output-1',
            pad_input.attrs['value'] + 'deadbeef')

        self.assertEqual(
            call_count.value, len('deadbeef') + 1,
            "the total updates is initial one + the text input changes")

        self.request_queue_assertions(call_count.value + 1)
        self.percy_snapshot(name='callback-generating-function-2')

        self.assertTrue(self.is_console_clean())

    def test_radio_buttons_callbacks_generating_children(self):
        self.maxDiff = 100 * 1000
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.RadioItems(
                options=[
                    {'label': 'Chapter 1', 'value': 'chapter1'},
                    {'label': 'Chapter 2', 'value': 'chapter2'},
                    {'label': 'Chapter 3', 'value': 'chapter3'},
                    {'label': 'Chapter 4', 'value': 'chapter4'},
                    {'label': 'Chapter 5', 'value': 'chapter5'}
                ],
                value='chapter1',
                id='toc'
            ),
            html.Div(id='body')
        ])
        for script in dcc._js_dist:
            app.scripts.append_script(script)

        chapters = {
            'chapter1': html.Div([
                html.H1('Chapter 1', id='chapter1-header'),
                dcc.Dropdown(
                    options=[{'label': i, 'value': i} for i in ['NYC', 'MTL', 'SF']],
                    value='NYC',
                    id='chapter1-controls'
                ),
                html.Label(id='chapter1-label'),
                dcc.Graph(id='chapter1-graph')
            ]),
            # Chapter 2 has the some of the same components in the same order
            # as Chapter 1. This means that they won't get remounted
            # unless they set their own keys are differently.
            # Switching back and forth between 1 and 2 implicitly
            # tests how components update when they aren't remounted.
            'chapter2': html.Div([
                html.H1('Chapter 2', id='chapter2-header'),
                dcc.RadioItems(
                    options=[{'label': i, 'value': i}
                             for i in ['USA', 'Canada']],
                    value='USA',
                    id='chapter2-controls'
                ),
                html.Label(id='chapter2-label'),
                dcc.Graph(id='chapter2-graph')
            ]),
            # Chapter 3 has a different layout and so the components
            # should get rewritten
            'chapter3': [html.Div(
                html.Div([
                    html.H3('Chapter 3', id='chapter3-header'),
                    html.Label(id='chapter3-label'),
                    dcc.Graph(id='chapter3-graph'),
                    dcc.RadioItems(
                        options=[{'label': i, 'value': i}
                                 for i in ['Summer', 'Winter']],
                        value='Winter',
                        id='chapter3-controls'
                    )
                ])
            )],

            # Chapter 4 doesn't have an object to recursively
            # traverse
            'chapter4': 'Just a string',

        }

        call_counts = {
            'body': Value('i', 0),
            'chapter1-graph': Value('i', 0),
            'chapter1-label': Value('i', 0),
            'chapter2-graph': Value('i', 0),
            'chapter2-label': Value('i', 0),
            'chapter3-graph': Value('i', 0),
            'chapter3-label': Value('i', 0),
        }

        @app.callback(Output('body', 'children'), [Input('toc', 'value')])
        def display_chapter(toc_value):
            call_counts['body'].value += 1
            return chapters[toc_value]

        app.config.supress_callback_exceptions = True

        def generate_graph_callback(counterId):
            def callback(value):
                call_counts[counterId].value += 1
                return {
                        'data': [{
                            'x': ['Call Counter'],
                            'y': [call_counts[counterId].value],
                            'type': 'bar'
                        }],
                        'layout': {'title': value}
                    }
            return callback

        def generate_label_callback(id):
            def update_label(value):
                call_counts[id].value += 1
                return value
            return update_label

        for chapter in ['chapter1', 'chapter2', 'chapter3']:
            app.callback(
                Output('{}-graph'.format(chapter), 'figure'),
                [Input('{}-controls'.format(chapter), 'value')]
            )(generate_graph_callback('{}-graph'.format(chapter)))

            app.callback(
                Output('{}-label'.format(chapter), 'children'),
                [Input('{}-controls'.format(chapter), 'value')]
            )(generate_label_callback('{}-label'.format(chapter)))

        self.startServer(app)

        time.sleep(0.5)
        wait_for(lambda: call_counts['body'].value == 1)
        wait_for(lambda: call_counts['chapter1-graph'].value == 1)
        wait_for(lambda: call_counts['chapter1-label'].value == 1)
        self.assertEqual(call_counts['chapter2-graph'].value, 0)
        self.assertEqual(call_counts['chapter2-label'].value, 0)
        self.assertEqual(call_counts['chapter3-graph'].value, 0)
        self.assertEqual(call_counts['chapter3-label'].value, 0)

        def generic_chapter_assertions(chapter):
            # each element should exist in the dom
            paths = self.driver.execute_script(
                'return window.store.getState().paths'
            )
            for key in paths:
                self.driver.find_element_by_id(key)

            if chapter == 'chapter3':
                value = chapters[chapter][0][
                    '{}-controls'.format(chapter)
                ].value
            else:
                value = chapters[chapter]['{}-controls'.format(chapter)].value
            # check the actual values
            self.wait_for_text_to_equal('#{}-label'.format(chapter), value)
            wait_for(
                lambda: (
                    self.driver.execute_script(
                        'return document.'
                        'getElementById("{}-graph").'.format(chapter) +
                        'layout.title.text'
                    ) == value
                )
            )
            self.request_queue_assertions()

        def chapter1_assertions():
            paths = self.driver.execute_script(
                'return window.store.getState().paths'
            )
            self.assertEqual(paths, {
                'toc': ['props', 'children', 0],
                'body': ['props', 'children', 1],
                'chapter1-header': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 0
                ],
                'chapter1-controls': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 1
                ],
                'chapter1-label': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 2
                ],
                'chapter1-graph': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 3
                ]
            })
            generic_chapter_assertions('chapter1')

        chapter1_assertions()
        self.percy_snapshot(name='chapter-1')

        # switch chapters
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[1]).click()

        # sleep just to make sure that no calls happen after our check
        time.sleep(2)
        self.percy_snapshot(name='chapter-2')
        wait_for(lambda: call_counts['body'].value == 2)
        wait_for(lambda: call_counts['chapter2-graph'].value == 1)
        wait_for(lambda: call_counts['chapter2-label'].value == 1)
        self.assertEqual(call_counts['chapter1-graph'].value, 1)
        self.assertEqual(call_counts['chapter1-label'].value, 1)

        def chapter2_assertions():
            paths = self.driver.execute_script(
                'return window.store.getState().paths'
            )
            self.assertEqual(paths, {
                'toc': ['props', 'children', 0],
                'body': ['props', 'children', 1],
                'chapter2-header': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 0
                ],
                'chapter2-controls': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 1
                ],
                'chapter2-label': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 2
                ],
                'chapter2-graph': [
                    'props', 'children', 1,
                    'props', 'children',
                    'props', 'children', 3
                ]
            })
            generic_chapter_assertions('chapter2')

        chapter2_assertions()

        # switch to 3
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[2]).click()
        # sleep just to make sure that no calls happen after our check
        time.sleep(2)
        self.percy_snapshot(name='chapter-3')
        wait_for(lambda: call_counts['body'].value == 3)
        wait_for(lambda: call_counts['chapter3-graph'].value == 1)
        wait_for(lambda: call_counts['chapter3-label'].value == 1)
        self.assertEqual(call_counts['chapter2-graph'].value, 1)
        self.assertEqual(call_counts['chapter2-label'].value, 1)
        self.assertEqual(call_counts['chapter1-graph'].value, 1)
        self.assertEqual(call_counts['chapter1-label'].value, 1)

        def chapter3_assertions():
            paths = self.driver.execute_script(
                'return window.store.getState().paths'
            )
            self.assertEqual(paths, {
                'toc': ['props', 'children', 0],
                'body': ['props', 'children', 1],
                'chapter3-header': [
                    'props', 'children', 1,
                    'props', 'children', 0,
                    'props', 'children',
                    'props', 'children', 0
                ],
                'chapter3-label': [
                    'props', 'children', 1,
                    'props', 'children', 0,
                    'props', 'children',
                    'props', 'children', 1
                ],
                'chapter3-graph': [
                    'props', 'children', 1,
                    'props', 'children', 0,
                    'props', 'children',
                    'props', 'children', 2
                ],
                'chapter3-controls': [
                    'props', 'children', 1,
                    'props', 'children', 0,
                    'props', 'children',
                    'props', 'children', 3
                ]
            })
            generic_chapter_assertions('chapter3')

        chapter3_assertions()

        # switch to 4
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[3]).click()
        self.wait_for_text_to_equal('#body', 'Just a string')
        self.percy_snapshot(name='chapter-4')

        # each element should exist in the dom
        paths = self.driver.execute_script(
            'return window.store.getState().paths'
        )
        for key in paths:
            self.driver.find_element_by_id(key)
        self.assertEqual(paths, {
            'toc': ['props', 'children', 0],
            'body': ['props', 'children', 1]
        })

        # switch back to 1
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[0]).click()
        time.sleep(0.5)
        chapter1_assertions()
        self.percy_snapshot(name='chapter-1-again')

    def test_dependencies_on_components_that_dont_exist(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='input', value='initial value'),
            html.Div(id='output-1')
        ])

        # standard callback
        output_1_call_count = Value('i', 0)

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            output_1_call_count.value += 1
            return value

        # callback for component that doesn't yet exist in the dom
        # in practice, it might get added by some other callback
        app.config.supress_callback_exceptions = True
        output_2_call_count = Value('i', 0)

        @app.callback(
            Output('output-2', 'children'),
            [Input('input', 'value')]
        )
        def update_output_2(value):
            output_2_call_count.value += 1
            return value

        self.startServer(app)

        self.wait_for_text_to_equal('#output-1', 'initial value')
        self.percy_snapshot(name='dependencies')
        time.sleep(1.0)
        self.assertEqual(output_1_call_count.value, 1)
        self.assertEqual(output_2_call_count.value, 0)

        input = self.driver.find_element_by_id('input')

        input.send_keys('a')
        self.wait_for_text_to_equal('#output-1', 'initial valuea')
        time.sleep(1.0)
        self.assertEqual(output_1_call_count.value, 2)
        self.assertEqual(output_2_call_count.value, 0)

        self.request_queue_assertions(2)

        self.assertTrue(self.is_console_clean())

    def test_event_properties(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button('Click Me', id='button'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'children'),
                      [Input('button', 'n_clicks')])
        def update_output(n_clicks):
            if(not n_clicks):
                raise PreventUpdate
            call_count.value += 1
            return 'Click'

        self.startServer(app)
        btn = self.driver.find_element_by_id('button')
        output = lambda: self.driver.find_element_by_id('output')
        self.assertEqual(call_count.value, 0)
        self.assertEqual(output().text, '')

        btn.click()
        wait_for(lambda: output().text == 'Click')
        self.assertEqual(call_count.value, 1)

    def test_event_properties_and_state(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button('Click Me', id='button'),
            dcc.Input(value='Initial State', id='state'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'children'),
                      [Input('button', 'n_clicks')],
                      [State('state', 'value')])
        def update_output(n_clicks, value):
            if(not n_clicks):
                raise PreventUpdate
            call_count.value += 1
            return value

        self.startServer(app)
        btn = self.driver.find_element_by_id('button')
        output = lambda: self.driver.find_element_by_id('output')

        self.assertEqual(call_count.value, 0)
        self.assertEqual(output().text, '')

        btn.click()
        wait_for(lambda: output().text == 'Initial State')
        self.assertEqual(call_count.value, 1)

        # Changing state shouldn't fire the callback
        state = self.driver.find_element_by_id('state')
        state.send_keys('x')
        time.sleep(0.75)
        self.assertEqual(output().text, 'Initial State')
        self.assertEqual(call_count.value, 1)

        btn.click()
        wait_for(lambda: output().text == 'Initial Statex')
        self.assertEqual(call_count.value, 2)

    def test_event_properties_state_and_inputs(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button('Click Me', id='button'),
            dcc.Input(value='Initial Input', id='input'),
            dcc.Input(value='Initial State', id='state'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'children'),
                      [Input('input', 'value'), Input('button', 'n_clicks')],
                      [State('state', 'value')])
        def update_output(input, n_clicks, state):
            call_count.value += 1
            return 'input="{}", state="{}"'.format(input, state)

        self.startServer(app)
        btn = lambda: self.driver.find_element_by_id('button')
        output = lambda: self.driver.find_element_by_id('output')
        input = lambda: self.driver.find_element_by_id('input')
        state = lambda: self.driver.find_element_by_id('state')

        # callback gets called with initial input
        self.assertEqual(
            output().text,
            'input="Initial Input", state="Initial State"'
        )

        btn().click()
        wait_for(lambda: call_count.value == 2)
        self.assertEqual(
            output().text,
            'input="Initial Input", state="Initial State"')

        input().send_keys('x')
        wait_for(lambda: call_count.value == 3)
        self.assertEqual(
            output().text,
            'input="Initial Inputx", state="Initial State"')

        state().send_keys('x')
        time.sleep(0.75)
        self.assertEqual(call_count.value, 3)
        self.assertEqual(
            output().text,
            'input="Initial Inputx", state="Initial State"')

        btn().click()
        wait_for(lambda: call_count.value == 4)
        self.assertEqual(
            output().text,
            'input="Initial Inputx", state="Initial Statex"')

    def test_state_and_inputs(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(value='Initial Input', id='input'),
            dcc.Input(value='Initial State', id='state'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(
            Output('output', 'children'), [Input('input', 'value')],
            [State('state', 'value')])
        def update_output(input, state):
            call_count.value += 1
            return 'input="{}", state="{}"'.format(input, state)

        self.startServer(app)
        output = lambda: self.driver.find_element_by_id('output')
        input = lambda: self.driver.find_element_by_id('input')
        state = lambda: self.driver.find_element_by_id('state')

        # callback gets called with initial input
        self.assertEqual(
            output().text,
            'input="Initial Input", state="Initial State"'
        )

        input().send_keys('x')
        wait_for(lambda: call_count.value == 2)
        self.assertEqual(
            output().text,
            'input="Initial Inputx", state="Initial State"')

        state().send_keys('x')
        time.sleep(0.75)
        self.assertEqual(call_count.value, 2)
        self.assertEqual(
            output().text,
            'input="Initial Inputx", state="Initial State"')

        input().send_keys('y')
        wait_for(lambda: call_count.value == 3)
        self.assertEqual(
            output().text,
            'input="Initial Inputxy", state="Initial Statex"')

    def test_event_properties_creating_inputs(self):
        app = Dash(__name__)

        ids = {
            k: k for k in ['button', 'button-output', 'input', 'input-output']
        }
        app.layout = html.Div([
            html.Button(id=ids['button']),
            html.Div(id=ids['button-output'])
        ])
        for script in dcc._js_dist:
            script['namespace'] = 'dash_core_components'
            app.scripts.append_script(script)

        app.config.supress_callback_exceptions = True
        call_counts = {
            ids['input-output']: Value('i', 0),
            ids['button-output']: Value('i', 0)
        }

        @app.callback(
            Output(ids['button-output'], 'children'),
            [Input(ids['button'], 'n_clicks')])
        def display(n_clicks):
            if(not n_clicks):
                raise PreventUpdate
            call_counts['button-output'].value += 1
            return html.Div([
                dcc.Input(id=ids['input'], value='initial state'),
                html.Div(id=ids['input-output'])
            ])

        @app.callback(
            Output(ids['input-output'], 'children'),
            [Input(ids['input'], 'value')])
        def update_input(value):
            call_counts['input-output'].value += 1
            return 'Input is equal to "{}"'.format(value)

        self.startServer(app)
        time.sleep(1)
        self.assertEqual(call_counts[ids['button-output']].value, 0)
        self.assertEqual(call_counts[ids['input-output']].value, 0)

        btn = lambda: self.driver.find_element_by_id(ids['button'])
        output = lambda: self.driver.find_element_by_id(ids['input-output'])
        with self.assertRaises(Exception):
            output()

        btn().click()
        wait_for(lambda: call_counts[ids['input-output']].value == 1)
        self.assertEqual(call_counts[ids['button-output']].value, 1)
        self.assertEqual(output().text, 'Input is equal to "initial state"')

    def test_chained_dependencies_direct_lineage(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='input-1', value='input 1'),
            dcc.Input(id='input-2'),
            html.Div('test', id='output')
        ])
        input1 = lambda: self.driver.find_element_by_id('input-1')
        input2 = lambda: self.driver.find_element_by_id('input-2')
        output = lambda: self.driver.find_element_by_id('output')

        call_counts = {
            'output': Value('i', 0),
            'input-2': Value('i', 0)
        }

        @app.callback(Output('input-2', 'value'), [Input('input-1', 'value')])
        def update_input(input1):
            call_counts['input-2'].value += 1
            return '<<{}>>'.format(input1)

        @app.callback(Output('output', 'children'), [
            Input('input-1', 'value'),
            Input('input-2', 'value')
        ])
        def update_output(input1, input2):
            call_counts['output'].value += 1
            return '{} + {}'.format(input1, input2)

        self.startServer(app)

        wait_for(lambda: call_counts['output'].value == 1)
        wait_for(lambda: call_counts['input-2'].value == 1)
        self.assertEqual(input1().get_attribute('value'), 'input 1')
        self.assertEqual(input2().get_attribute('value'), '<<input 1>>')
        self.assertEqual(output().text, 'input 1 + <<input 1>>')

        input1().send_keys('x')
        wait_for(lambda: call_counts['output'].value == 2)
        wait_for(lambda: call_counts['input-2'].value == 2)
        self.assertEqual(input1().get_attribute('value'), 'input 1x')
        self.assertEqual(input2().get_attribute('value'), '<<input 1x>>')
        self.assertEqual(output().text, 'input 1x + <<input 1x>>')

        input2().send_keys('y')
        wait_for(lambda: call_counts['output'].value == 3)
        wait_for(lambda: call_counts['input-2'].value == 2)
        self.assertEqual(input1().get_attribute('value'), 'input 1x')
        self.assertEqual(input2().get_attribute('value'), '<<input 1x>>y')
        self.assertEqual(output().text, 'input 1x + <<input 1x>>y')


    def test_chained_dependencies_branched_lineage(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='grandparent', value='input 1'),
            dcc.Input(id='parent-a'),
            dcc.Input(id='parent-b'),
            html.Div(id='child-a'),
            html.Div(id='child-b')
        ])
        grandparent = lambda: self.driver.find_element_by_id('grandparent')
        parenta = lambda: self.driver.find_element_by_id('parent-a')
        parentb = lambda: self.driver.find_element_by_id('parent-b')
        childa = lambda: self.driver.find_element_by_id('child-a')
        childb = lambda: self.driver.find_element_by_id('child-b')

        call_counts = {
            'parent-a': Value('i', 0),
            'parent-b': Value('i', 0),
            'child-a': Value('i', 0),
            'child-b': Value('i', 0)
        }

        @app.callback(Output('parent-a', 'value'),
                      [Input('grandparent', 'value')])
        def update_parenta(value):
            call_counts['parent-a'].value += 1
            return 'a: {}'.format(value)

        @app.callback(Output('parent-b', 'value'),
                      [Input('grandparent', 'value')])
        def update_parentb(value):
            time.sleep(0.5)
            call_counts['parent-b'].value += 1
            return 'b: {}'.format(value)

        @app.callback(Output('child-a', 'children'),
                      [Input('parent-a', 'value'),
                       Input('parent-b', 'value')])
        def update_childa(parenta_value, parentb_value):
            time.sleep(1)
            call_counts['child-a'].value += 1
            return '{} + {}'.format(parenta_value, parentb_value)

        @app.callback(Output('child-b', 'children'),
                      [Input('parent-a', 'value'),
                       Input('parent-b', 'value'),
                       Input('grandparent', 'value')])
        def update_childb(parenta_value, parentb_value, grandparent_value):
            call_counts['child-b'].value += 1
            return '{} + {} + {}'.format(
                parenta_value,
                parentb_value,
                grandparent_value
            )

        self.startServer(app)

        wait_for(lambda: childa().text == 'a: input 1 + b: input 1')
        wait_for(lambda: childb().text == 'a: input 1 + b: input 1 + input 1')
        time.sleep(1)  # wait for potential requests of app to settle down
        self.assertEqual(parenta().get_attribute('value'), 'a: input 1')
        self.assertEqual(parentb().get_attribute('value'), 'b: input 1')
        self.assertEqual(call_counts['parent-a'].value, 1)
        self.assertEqual(call_counts['parent-b'].value, 1)
        self.assertEqual(call_counts['child-a'].value, 1)
        self.assertEqual(call_counts['child-b'].value, 1)

    def test_removing_component_while_its_getting_updated(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.RadioItems(
                id='toc',
                options=[
                    {'label': i, 'value': i} for i in ['1', '2']
                ],
                value='1'
            ),
            html.Div(id='body')
        ])
        app.config.supress_callback_exceptions = True

        call_counts = {
            'body': Value('i', 0),
            'button-output': Value('i', 0)
        }

        @app.callback(Output('body', 'children'), [Input('toc', 'value')])
        def update_body(chapter):
            call_counts['body'].value += 1
            if chapter == '1':
                return [
                    html.Div('Chapter 1'),
                    html.Button(
                        'clicking this button takes forever',
                        id='button'
                    ),
                    html.Div(id='button-output')
                ]
            elif chapter == '2':
                return 'Chapter 2'
            else:
                raise Exception('chapter is {}'.format(chapter))

        @app.callback(
            Output('button-output', 'children'),
            [Input('button', 'n_clicks')])
        def this_callback_takes_forever(n_clicks):
            if not n_clicks:
                # initial value is quick, only new value is slow
                # also don't let the initial value increment call_counts
                return 'Initial Value'
            time.sleep(5)
            call_counts['button-output'].value += 1
            return 'New value!'

        body = lambda: self.driver.find_element_by_id('body')
        self.startServer(app)

        wait_for(lambda: call_counts['body'].value == 1)
        time.sleep(0.5)
        self.driver.find_element_by_id('button').click()

        # while that callback is resolving, switch the chapter,
        # hiding the `button-output` tag
        def chapter2_assertions():
            wait_for(lambda: body().text == 'Chapter 2')

            layout = self.driver.execute_script(
                'return JSON.parse(JSON.stringify('
                'window.store.getState().layout'
                '))'
            )

            dcc_radio = layout['props']['children'][0]
            html_body = layout['props']['children'][1]

            self.assertEqual(dcc_radio['props']['id'], 'toc')
            self.assertEqual(dcc_radio['props']['value'], '2')

            self.assertEqual(html_body['props']['id'], 'body')
            self.assertEqual(html_body['props']['children'], 'Chapter 2')

        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[1]).click()
        chapter2_assertions()
        self.assertEqual(call_counts['button-output'].value, 0)
        time.sleep(5)
        wait_for(lambda: call_counts['button-output'].value, expected_value=1)
        time.sleep(2)  # liberally wait for the front-end to process request
        chapter2_assertions()
        self.assertTrue(self.is_console_clean())

    def test_rendering_layout_calls_callback_once_per_output(self):
        app = Dash(__name__)
        call_count = Value('i', 0)

        app.config['suppress_callback_exceptions'] = True
        app.layout = html.Div([
            html.Div([
                dcc.Input(
                    value='Input {}'.format(i),
                    id='input-{}'.format(i)
                )
                for i in range(10)
            ]),
            html.Div(id='container'),
            dcc.RadioItems()
        ])

        @app.callback(
            Output('container', 'children'),
            [Input('input-{}'.format(i), 'value') for i in range(10)])
        def dynamic_output(*args):
            call_count.value += 1
            return json.dumps(args, indent=2)

        self.startServer(app)

        time.sleep(5)

        self.percy_snapshot(
            name='test_rendering_layout_calls_callback_once_per_output'
        )

        self.assertEqual(call_count.value, 1)

    def test_rendering_new_content_calls_callback_once_per_output(self):
        app = Dash(__name__)
        call_count = Value('i', 0)

        app.config['suppress_callback_exceptions'] = True
        app.layout = html.Div([
            html.Button(
                id='display-content',
                children='Display Content',
                n_clicks=0
            ),
            html.Div(id='container'),
            dcc.RadioItems()
        ])

        @app.callback(
            Output('container', 'children'),
            [Input('display-content', 'n_clicks')])
        def display_output(n_clicks):
            if n_clicks == 0:
                return ''
            return html.Div([
                html.Div([
                    dcc.Input(
                        value='Input {}'.format(i),
                        id='input-{}'.format(i)
                    )
                    for i in range(10)
                ]),
                html.Div(id='dynamic-output')
            ])

        @app.callback(
            Output('dynamic-output', 'children'),
            [Input('input-{}'.format(i), 'value') for i in range(10)])
        def dynamic_output(*args):
            call_count.value += 1
            return json.dumps(args, indent=2)

        self.startServer(app)

        self.wait_for_element_by_css_selector('#display-content').click()

        time.sleep(5)

        self.percy_snapshot(
            name='test_rendering_new_content_calls_callback_once_per_output'
        )

        self.assertEqual(call_count.value, 1)

    def test_callbacks_called_multiple_times_and_out_of_order(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button(id='input', n_clicks=0),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(
            Output('output', 'children'),
            [Input('input', 'n_clicks')])
        def update_output(n_clicks):
            call_count.value = call_count.value + 1
            if n_clicks == 1:
                time.sleep(4)
            return n_clicks

        self.startServer(app)
        button = self.wait_for_element_by_css_selector('#input')
        button.click()
        button.click()
        time.sleep(8)
        self.percy_snapshot(
            name='test_callbacks_called_multiple_times_and_out_of_order'
        )
        self.assertEqual(call_count.value, 3)
        self.assertEqual(
            self.driver.find_element_by_id('output').text,
            '2'
        )
        request_queue = self.driver.execute_script(
            'return window.store.getState().requestQueue'
        )
        self.assertFalse(request_queue[0]['rejected'])
        self.assertEqual(len(request_queue), 1)

    def test_callbacks_called_multiple_times_and_out_of_order_multi_output(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button(id='input', n_clicks=0),
            html.Div(id='output1'),
            html.Div(id='output2')
        ])

        call_count = Value('i', 0)

        @app.callback(
            [Output('output1', 'children'),
             Output('output2', 'children')],
            [Input('input', 'n_clicks')]
        )
        def update_output(n_clicks):
            call_count.value = call_count.value + 1
            if n_clicks == 1:
                time.sleep(4)
            return n_clicks, n_clicks + 1

        self.startServer(app)
        button = self.wait_for_element_by_css_selector('#input')
        button.click()
        button.click()
        time.sleep(8)
        self.percy_snapshot(
            name='test_callbacks_called_multiple_times'
                 '_and_out_of_order_multi_output'
        )
        self.assertEqual(call_count.value, 3)
        self.wait_for_text_to_equal('#output1', '2')
        self.wait_for_text_to_equal('#output2', '3')
        request_queue = self.driver.execute_script(
            'return window.store.getState().requestQueue'
        )
        self.assertFalse(request_queue[0]['rejected'])
        self.assertEqual(len(request_queue), 1)

    def test_callbacks_with_shared_grandparent(self):
        app = dash.Dash()

        app.layout = html.Div([
            html.Div(id='session-id', children='id'),
            dcc.Dropdown(id='dropdown-1'),
            dcc.Dropdown(id='dropdown-2'),
        ])

        options = [{'value': 'a', 'label': 'a'}]

        call_counts = {
            'dropdown_1': Value('i', 0),
            'dropdown_2': Value('i', 0)
        }

        @app.callback(
            Output('dropdown-1', 'options'),
            [Input('dropdown-1', 'value'),
             Input('session-id', 'children')])
        def dropdown_1(value, session_id):
            call_counts['dropdown_1'].value += 1
            return options

        @app.callback(
            Output('dropdown-2', 'options'),
            [Input('dropdown-2', 'value'),
             Input('session-id', 'children')])
        def dropdown_2(value, session_id):
            call_counts['dropdown_2'].value += 1
            return options

        self.startServer(app)

        self.wait_for_element_by_css_selector('#session-id')
        time.sleep(2)
        self.assertEqual(call_counts['dropdown_1'].value, 1)
        self.assertEqual(call_counts['dropdown_2'].value, 1)

        self.assertTrue(self.is_console_clean())

    def test_callbacks_triggered_on_generated_output(self):
        app = dash.Dash()
        app.config['suppress_callback_exceptions'] = True

        call_counts = {
            'tab1': Value('i', 0),
            'tab2': Value('i', 0)
        }

        app.layout = html.Div([
            dcc.Dropdown(
                id='outer-controls',
                options=[{'label': i, 'value': i} for i in ['a', 'b']],
                value='a'
            ),
            dcc.RadioItems(
                options=[
                    {'label': 'Tab 1', 'value': 1},
                    {'label': 'Tab 2', 'value': 2}
                ],
                value=1,
                id='tabs',
            ),
            html.Div(id='tab-output')
        ])

        @app.callback(Output('tab-output', 'children'),
                      [Input('tabs', 'value')])
        def display_content(value):
            return html.Div([
                html.Div(id='tab-{}-output'.format(value))
            ])

        @app.callback(Output('tab-1-output', 'children'),
                      [Input('outer-controls', 'value')])
        def display_tab1_output(value):
            call_counts['tab1'].value += 1
            return 'Selected "{}" in tab 1'.format(value)

        @app.callback(Output('tab-2-output', 'children'),
                      [Input('outer-controls', 'value')])
        def display_tab2_output(value):
            call_counts['tab2'].value += 1
            return 'Selected "{}" in tab 2'.format(value)

        self.startServer(app)
        self.wait_for_element_by_css_selector('#tab-output')
        time.sleep(2)

        self.assertEqual(call_counts['tab1'].value, 1)
        self.assertEqual(call_counts['tab2'].value, 0)
        self.wait_for_text_to_equal('#tab-output', 'Selected "a" in tab 1')
        self.wait_for_text_to_equal('#tab-1-output', 'Selected "a" in tab 1')

        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[1]).click()
        time.sleep(2)

        self.wait_for_text_to_equal('#tab-output', 'Selected "a" in tab 2')
        self.wait_for_text_to_equal('#tab-2-output', 'Selected "a" in tab 2')
        self.assertEqual(call_counts['tab1'].value, 1)
        self.assertEqual(call_counts['tab2'].value, 1)

        self.assertTrue(self.is_console_clean())

    def test_initialization_with_overlapping_outputs(self):
        app = dash.Dash()
        app.layout = html.Div([

            html.Div(id='input-1', children='input-1'),
            html.Div(id='input-2', children='input-2'),
            html.Div(id='input-3', children='input-3'),
            html.Div(id='input-4', children='input-4'),
            html.Div(id='input-5', children='input-5'),

            html.Div(id='output-1'),
            html.Div(id='output-2'),
            html.Div(id='output-3'),
            html.Div(id='output-4'),

        ])
        call_counts = {
            'output-1': Value('i', 0),
            'output-2': Value('i', 0),
            'output-3': Value('i', 0),
            'output-4': Value('i', 0),
        }

        def generate_callback(outputid):
            def callback(*args):
                call_counts[outputid].value += 1
                return '{}, {}'.format(*args)
            return callback

        for i in range(1, 5):
            outputid = 'output-{}'.format(i)
            app.callback(
                Output(outputid, 'children'),
                [Input('input-{}'.format(i), 'children'),
                 Input('input-{}'.format(i+1), 'children')]
            )(generate_callback(outputid))

        self.startServer(app)

        self.wait_for_element_by_css_selector('#output-1')
        time.sleep(5)

        for i in range(1, 5):
            outputid = 'output-{}'.format(i)
            self.assertEqual(call_counts[outputid].value, 1)
            self.wait_for_text_to_equal(
                '#{}'.format(outputid),
                "input-{}, input-{}".format(i, i+1)
            )

    def test_generate_overlapping_outputs(self):
        app = dash.Dash()
        app.config['suppress_callback_exceptions'] = True
        block = html.Div([

            html.Div(id='input-1', children='input-1'),
            html.Div(id='input-2', children='input-2'),
            html.Div(id='input-3', children='input-3'),
            html.Div(id='input-4', children='input-4'),
            html.Div(id='input-5', children='input-5'),

            html.Div(id='output-1'),
            html.Div(id='output-2'),
            html.Div(id='output-3'),
            html.Div(id='output-4'),

        ])
        app.layout = html.Div([
            html.Div(id='input'),
            html.Div(id='container')
        ])

        call_counts = {
            'container': Value('i', 0),
            'output-1': Value('i', 0),
            'output-2': Value('i', 0),
            'output-3': Value('i', 0),
            'output-4': Value('i', 0),
        }

        @app.callback(Output('container', 'children'),
                      [Input('input', 'children')])
        def display_output(*args):
            call_counts['container'].value += 1
            return block

        def generate_callback(outputid):
            def callback(*args):
                call_counts[outputid].value += 1
                return '{}, {}'.format(*args)
            return callback

        for i in range(1, 5):
            outputid = 'output-{}'.format(i)
            app.callback(
                Output(outputid, 'children'),
                [Input('input-{}'.format(i), 'children'),
                 Input('input-{}'.format(i+1), 'children')]
            )(generate_callback(outputid))

        self.startServer(app)

        wait_for(lambda: call_counts['container'].value == 1)
        self.wait_for_element_by_css_selector('#output-1')
        time.sleep(5)

        for i in range(1, 5):
            outputid = 'output-{}'.format(i)
            self.assertEqual(call_counts[outputid].value, 1)
            self.wait_for_text_to_equal(
                '#{}'.format(outputid),
                "input-{}, input-{}".format(i, i+1)
            )
        self.assertEqual(call_counts['container'].value, 1)

    def test_update_react_version(self):
        import dash_renderer

        self.assertEqual(
            dash_renderer._js_dist_dependencies,
            [{
                'external_url': [
                    'https://unpkg.com/react@16.8.6/umd/react.production.min.js',
                    'https://unpkg.com/react-dom@16.8.6/umd/react-dom.production.min.js',
                ],
                'relative_package_path': [
                    'react@16.8.6.min.js',
                    'react-dom@16.8.6.min.js'
                ],
                'namespace': 'dash_renderer',
            }])

        app = dash.Dash()

        # Create a dummy component with no props
        # (dash-html-components may not support tested React version)
        class TestComponent(Component):
            def __init__(self, _namespace):
                self._type = 'TestComponent'
                self._prop_names = []
                self._namespace = _namespace
                self._valid_wildcard_attributes = []
                self.available_properties = []
                self.available_wildcard_properties = []
                super(TestComponent, self).__init__()

        _test_component = TestComponent(_namespace='test-namespace')
        app.layout = _test_component

        self.startServer(app)


    def test_multiple_properties_update_at_same_time_on_same_component(self):
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
        self.percy_snapshot('button initialization 1')

        self.driver.find_element_by_css_selector('#button-1').click()
        time.sleep(2)
        self.wait_for_text_to_equal('#container', '1, 0')
        self.assertTrue(
            timestamp_1.value >
            ((time.time()  - (24 * 60 * 60)) * 1000))
        self.assertEqual(timestamp_2.value, -1)
        self.assertEqual(call_count.value, 2)
        self.percy_snapshot('button-1 click')
        prev_timestamp_1 = timestamp_1.value

        self.driver.find_element_by_css_selector('#button-2').click()
        time.sleep(2)
        self.wait_for_text_to_equal('#container', '1, 1')
        self.assertEqual(timestamp_1.value, prev_timestamp_1)
        self.assertTrue(
            timestamp_2.value >
            ((time.time()  - 24 * 60 * 60) * 1000))
        self.assertEqual(call_count.value, 3)
        self.percy_snapshot('button-2 click')
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
        self.percy_snapshot('button-2 click again')

    def test_request_hooks(self):
        app = Dash(__name__)

        app.index_string = '''
        <!DOCTYPE html>
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
        </html>
        '''

        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(
                html.Div([
                    html.Div(id='output-1'),
                    html.Div(id='output-pre'),
                    html.Div(id='output-pre-payload'),
                    html.Div(id='output-post'),
                    html.Div(id='output-post-payload'),
                    html.Div(id='output-post-response')
                ])
            )
        ])

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            return value

        self.startServer(app)

        input1 = self.wait_for_element_by_css_selector('#input')
        initialValue = input1.get_attribute('value')

        action = ActionChains(self.driver)
        action.click(input1)
        action = action.send_keys(Keys.BACKSPACE * len(initialValue))

        action.send_keys('fire request hooks').perform()

        self.wait_for_text_to_equal('#output-1', 'fire request hooks')
        self.wait_for_text_to_equal('#output-pre', 'request_pre changed this text!')
        self.wait_for_text_to_equal('#output-pre-payload', '{"output":"output-1.children","changedPropIds":["input.value"],"inputs":[{"id":"input","property":"value","value":"fire request hooks"}]}')
        self.wait_for_text_to_equal('#output-post', 'request_post changed this text!')
        self.wait_for_text_to_equal('#output-post-payload', '{"output":"output-1.children","changedPropIds":["input.value"],"inputs":[{"id":"input","property":"value","value":"fire request hooks"}]}')
        self.wait_for_text_to_equal('#output-post-response', '{"props":{"children":"fire request hooks"}}')
        self.percy_snapshot(name='request-hooks')

    def test_graphs_in_tabs_do_not_share_state(self):
        app = dash.Dash()

        app.config.suppress_callback_exceptions = True

        app.layout = html.Div([
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
        ])
        tab1_layout = [
            html.Div([dcc.Graph(id='graph1',
                                figure={
                                    'data': [{
                                        'x': [1, 2, 3],
                                        'y': [5, 10, 6],
                                        'type': 'bar'
                                        }]
                                })]),

            html.Pre(id='graph1_info'),
        ]


        tab2_layout = [
            html.Div([dcc.Graph(id='graph2',
                                figure={
                                    'data': [{
                                        'x': [4, 3, 2],
                                        'y': [5, 10, 6],
                                        'type': 'bar'
                                        }]
                                })]),

            html.Pre(id='graph2_info'),
        ]

        @app.callback(Output(component_id='graph1_info', component_property='children'),
                    [Input(component_id='graph1', component_property='clickData')])
        def display_hover_data(hover_data):
            return json.dumps(hover_data)


        @app.callback(Output(component_id='graph2_info', component_property='children'),
                    [Input(component_id='graph2', component_property='clickData')])
        def display_hover_data(hover_data):
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

        self.wait_for_element_by_css_selector('#graph1')

        self.driver.find_elements_by_css_selector(
            '#graph1'
        )[0].click()

        graph_1_expected_clickdata = {
            "points": [{"curveNumber": 0, "pointNumber": 1, "pointIndex": 1, "x": 2, "y": 10}]
        }

        graph_2_expected_clickdata = {
            "points": [{"curveNumber": 0, "pointNumber": 1, "pointIndex": 1, "x": 3, "y": 10}]
        }

        self.wait_for_text_to_equal('#graph1_info', json.dumps(graph_1_expected_clickdata))

        self.driver.find_elements_by_css_selector(
            '#tab2'
        )[0].click()

        self.wait_for_element_by_css_selector('#graph2')

        self.driver.find_elements_by_css_selector(
            '#graph2'
        )[0].click()

        self.wait_for_text_to_equal('#graph2_info', json.dumps(graph_2_expected_clickdata))

    def test_hot_reload(self):
        app = dash.Dash(__name__, assets_folder='test_assets')

        app.layout = html.Div([
            html.H3('Hot reload')
        ], id='hot-reload-content')

        self.startServer(
            app,
            dev_tools_hot_reload=True,
            dev_tools_hot_reload_interval=100,
            dev_tools_hot_reload_max_retry=30,
        )

        hot_reload_file = os.path.join(
            os.path.dirname(__file__), 'test_assets', 'hot_reload.css')

        self.wait_for_style_to_equal(
            '#hot-reload-content', 'background-color', 'rgba(0, 0, 255, 1)'
        )

        with open(hot_reload_file, 'r+') as f:
            old_content = f.read()
            f.truncate(0)
            f.seek(0)
            f.write(textwrap.dedent('''
            #hot-reload-content {
                background-color: red;
            }
            '''))

        try:
            self.wait_for_style_to_equal(
                '#hot-reload-content', 'background-color', 'rgba(255, 0, 0, 1)'
            )
        finally:
            with open(hot_reload_file, 'w') as f:
                f.write(old_content)

    def test_single_input_multi_outputs_on_multiple_components(self):
        call_count = Value('i')

        app = dash.Dash(__name__)

        N_OUTPUTS = 50

        app.layout = html.Div([
            html.Button('click me', id='btn'),
        ] + [html.Div(id='output-{}'.format(i)) for i in range(N_OUTPUTS)])

        @app.callback([Output('output-{}'.format(i), 'children') for i in range(N_OUTPUTS)],
                      [Input('btn', 'n_clicks')])
        def update_output(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            call_count.value += 1
            return ['{}={}'.format(i, i+n_clicks) for i in range(N_OUTPUTS)]

        self.startServer(app)

        btn = self.wait_for_element_by_css_selector('#btn')

        for click in range(1, 20):
            btn.click()

            for i in range(N_OUTPUTS):
                self.wait_for_text_to_equal(
                    '#output-{}'.format(i), '{}={}'.format(i, i+click))

            self.assertEqual(call_count.value, click)

    def test_multi_outputs_on_single_component(self):
        call_count = Value('i')
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Input(id='input', value='dash'),
            html.Div(html.Div(id='output'), id='output-container'),
        ])

        @app.callback(
            [Output('output', 'children'),
             Output('output', 'style'),
             Output('output', 'className')],

            [Input('input', 'value')])
        def update_output(value):
            call_count.value += 1
            return [
                value,
                {'fontFamily': value},
                value
            ]

        self.startServer(app)

        def html_equal(selector, inner_html):
            return self.driver.find_element_by_css_selector(selector)\
                       .get_property('innerHTML') == inner_html

        wait_for(
            lambda: html_equal(
                '#output-container',
                '<div id="output" class="dash" style="font-family: dash;">dash</div>'
            ),
            get_message=lambda: self.driver.find_element_by_css_selector('#output-container').get_property('innerHTML')
        )

        self.assertEqual(call_count.value, 1)

        el = self.wait_for_element_by_css_selector('#input')
        el.send_keys(' hello')

        wait_for(
            lambda: html_equal(
                '#output-container',
                '<div id="output" class="dash hello" style="font-family: &quot;dash hello&quot;;">dash hello</div>'
            ),
            get_message=lambda: self.driver.find_element_by_css_selector('#output-container').get_property('innerHTML')
        )

        self.assertEqual(call_count.value, 7)

    def test_single_output_as_multi(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Input(id='input', value=''),
            html.Div(html.Div(id='output'), id='output-container'),
        ])

        @app.callback(
            [Output('output', 'children')],
            [Input('input', 'value')])
        def update_output(value):
            return ['out' + value]

        self.startServer(app)

        input = self.wait_for_element_by_css_selector('#input')
        input.send_keys('house')
        self.wait_for_text_to_equal('#output', 'outhouse')

    def test_multi_output_circular_dependencies(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='a'),
            dcc.Input(id='b'),
            html.P(id='c')
        ])

        @app.callback(Output('a', 'value'), [Input('b', 'value')])
        def set_a(b):
            return ((b or '') + 'X')[:100]

        @app.callback(
            [Output('b', 'value'), Output('c', 'children')],
            [Input('a', 'value')])
        def set_bc(a):
            return [a, a]

        self.startServer(
            app, debug=True, use_debugger=True,
            use_reloader=False, dev_tools_hot_reload=False)

        self.assertEqual(
            'Circular Dependencies',
            self.driver.find_element_by_css_selector('span.dash-fe-error__title').text,
            "circular dependencies should be captured by debug menu"
        )

        self.assertEqual(
            {'X'},
            set(self.driver.find_element_by_css_selector('#c').text),
            "the UI still renders the output triggered by callback"
        )

    def test_simple_clientside_serverside_callback(self):
        app = dash.Dash(__name__, assets_folder='test_clientside')

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
        app = dash.Dash(__name__, assets_folder='test_clientside')

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

    def test_simple_clientside_serverside_callback(self):
        app = dash.Dash(__name__, assets_folder='test_clientside')

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
        app = dash.Dash(__name__, assets_folder='test_clientside')

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
            ['#mean-of-all-values', str((3+6+9+4.5) / 4.0)],
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
            ['#mean-of-all-values', str((31+6+37+18.5) / 4.0)],
        ]
        for test_case in test_cases:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        self.assertEqual(call_counts['display'].value, 2)
        self.assertEqual(call_counts['divide'].value, 2)


    def test_clientside_exceptions_halt_subsequent_updates(self):
        app = dash.Dash(__name__, assets_folder='test_clientside')

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
        app = dash.Dash(__name__, assets_folder='test_clientside')

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

        for test_case in [['#input', '1'],
                ['#output-1', '2'],
                ['#output-2', '3'],
                ['#output-3', '4'],
                ['#output-4', '5']]:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

        input = self.wait_for_element_by_css_selector('#input')
        input.send_keys('1')

        for test_case in [['#input', '11'],
                ['#output-1', '12'],
                ['#output-2', '13'],
                ['#output-3', '14'],
                ['#output-4', '15']]:
            self.wait_for_text_to_equal(test_case[0], test_case[1])

    def test_clientside_fails_when_returning_a_promise(self):
        app = dash.Dash(__name__, assets_folder='test_clientside')

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
                1/0
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
