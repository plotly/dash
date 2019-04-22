# -*- coding: utf-8 -*-
import base64
import itertools
from datetime import datetime
import io
import os
import sys
from multiprocessing import Lock
import time
import json
import re

import flask
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
from dash_table import DataTable
from dash.exceptions import PreventUpdate
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidElementStateException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from textwrap import dedent
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from .IntegrationTests import IntegrationTests
from .utils import wait_for

from multiprocessing import Value

# Download geckodriver: https://github.com/mozilla/geckodriver/releases
# And add to path:
# export PATH=$PATH:/Users/chriddyp/Repos/dash-stuff/dash-integration-tests
#
# Uses percy.io for automated screenshot tests
# export PERCY_PROJECT=plotly/dash-integration-tests
# export PERCY_TOKEN=...


TIMEOUT = 10


class Tests(IntegrationTests):
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

        WebDriverWait(self.driver, TIMEOUT).until(
            text_equal
        )

    def snapshot(self, name):
        if 'PERCY_PROJECT' in os.environ and 'PERCY_TOKEN' in os.environ:
            python_version = sys.version.split(' ')[0]
            print('Percy Snapshot {}'.format(python_version))
            self.percy_runner.snapshot(name=name)

    def create_upload_component_content_types_test(self, filename):
        app = dash.Dash(__name__)

        filepath = os.path.join(os.getcwd(), 'test', 'upload-assets', filename)

        pre_style = {
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        }

        app.layout = html.Div([
            html.Div(filepath, id='waitfor'),
            html.Div(
                id='upload-div',
                children=dcc.Upload(
                    id='upload',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select a File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center'
                    }
                )
            ),
            html.Div(id='output'),
            html.Div(DataTable(data=[{}]), style={'display': 'none'})
        ])

        @app.callback(Output('output', 'children'),
                      [Input('upload', 'contents')])
        def update_output(contents):
            if contents is not None:
                content_type, content_string = contents.split(',')
                if 'csv' in filepath:
                    df = pd.read_csv(io.StringIO(base64.b64decode(
                        content_string).decode('utf-8')))
                    return html.Div([
                        DataTable(
                            data=df.to_dict('records'),
                            columns=[{'id': i} for i in ['city', 'country']]),
                        html.Hr(),
                        html.Div('Raw Content'),
                        html.Pre(contents, style=pre_style)
                    ])
                elif 'xls' in filepath:
                    df = pd.read_excel(io.BytesIO(base64.b64decode(
                        content_string)))
                    return html.Div([
                        DataTable(
                            data=df.to_dict('records'),
                            columns=[{'id': i} for i in ['city', 'country']]),
                        html.Hr(),
                        html.Div('Raw Content'),
                        html.Pre(contents, style=pre_style)
                    ])
                elif 'image' in content_type:
                    return html.Div([
                        html.Img(src=contents),
                        html.Hr(),
                        html.Div('Raw Content'),
                        html.Pre(contents, style=pre_style)
                    ])
                else:
                    return html.Div([
                        html.Hr(),
                        html.Div('Raw Content'),
                        html.Pre(contents, style=pre_style)
                    ])

        self.startServer(app)

        try:
            self.wait_for_element_by_css_selector('#waitfor')
        except Exception as e:
            print(self.wait_for_element_by_css_selector(
                '#_dash-app-content').get_attribute('innerHTML'))
            raise e

        upload_div = self.wait_for_element_by_css_selector(
            '#upload-div input[type=file]')

        upload_div.send_keys(filepath)
        time.sleep(5)
        self.snapshot(filename)

    def test_upload_csv(self):
        self.create_upload_component_content_types_test('utf8.csv')

    def test_upload_xlsx(self):
        self.create_upload_component_content_types_test('utf8.xlsx')

    def test_upload_png(self):
        self.create_upload_component_content_types_test('dash-logo-stripe.png')

    def test_upload_svg(self):
        self.create_upload_component_content_types_test('dash-logo-stripe.svg')

    def test_upload_gallery(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Div(id='waitfor'),
            html.Label('Empty'),
            dcc.Upload(),

            html.Label('Button'),
            dcc.Upload(html.Button('Upload File')),

            html.Label('Text'),
            dcc.Upload('Upload File'),

            html.Label('Link'),
            dcc.Upload(html.A('Upload File')),

            html.Label('Style'),
            dcc.Upload([
                'Drag and Drop or ',
                html.A('Select a File')
            ], style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center'
            })
        ])
        self.startServer(app)

        try:
            self.wait_for_element_by_css_selector('#waitfor')
        except Exception as e:
            print(self.wait_for_element_by_css_selector(
                '#_dash-app-content').get_attribute('innerHTML'))
            raise e

        self.snapshot('test_upload_gallery')

    def test_loading_component_initialization(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Loading([
                html.Div(id='div-1')
            ], className='loading')
        ], id='root')

        @app.callback(
            Output('div-1', 'children'),
            [Input('root', 'n_clicks')]
        )
        def updateDiv(children):
            with lock:
                return 'content'

        with lock:
            self.startServer(app)
            self.wait_for_element_by_css_selector(
                '.loading .dash-spinner'
            )

        self.wait_for_element_by_css_selector(
            '.loading #div-1'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_loading_component_action(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Loading([
                html.Div(id='div-1')
            ], className='loading')
        ], id='root')

        @app.callback(
            Output('div-1', 'children'),
            [Input('root', 'n_clicks')]
        )
        def updateDiv(n_clicks):
            if n_clicks is not None:
                with lock:
                    return

            return 'content'

        with lock:
            self.startServer(app)
            self.wait_for_element_by_css_selector(
                '.loading #div-1'
            )

            self.driver.find_element_by_id('root').click()

            self.wait_for_element_by_css_selector(
                '.loading .dash-spinner'
            )

        self.wait_for_element_by_css_selector(
            '.loading #div-1'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_multiple_loading_components(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Loading([
                html.Button(id='btn-1')
            ], className='loading-1'),
            dcc.Loading([
                html.Button(id='btn-2')
            ], className='loading-2')
        ], id='root')

        @app.callback(
            Output('btn-1', 'value'),
            [Input('btn-2', 'n_clicks')]
        )
        def updateDiv(n_clicks):
            if n_clicks is not None:
                with lock:
                    return

            return 'content'

        @app.callback(
            Output('btn-2', 'value'),
            [Input('btn-1', 'n_clicks')]
        )
        def updateDiv(n_clicks):
            if n_clicks is not None:
                with lock:
                    return

            return 'content'

        self.startServer(app)

        self.wait_for_element_by_css_selector(
            '.loading-1 #btn-1'
        )
        self.wait_for_element_by_css_selector(
            '.loading-2 #btn-2'
        )

        with lock:
            self.driver.find_element_by_id('btn-1').click()

            self.wait_for_element_by_css_selector(
                '.loading-2 .dash-spinner'
            )
            self.wait_for_element_by_css_selector(
                '.loading-1 #btn-1'
            )

        self.wait_for_element_by_css_selector(
            '.loading-2 #btn-2'
        )

        with lock:
            self.driver.find_element_by_id('btn-2').click()

            self.wait_for_element_by_css_selector(
                '.loading-1 .dash-spinner'
            )

        self.wait_for_element_by_css_selector(
            '.loading-1 #btn-1'
        )
        self.wait_for_element_by_css_selector(
            '.loading-2 #btn-2'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_nested_loading_components(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Loading([
                html.Button(id='btn-1'),
                dcc.Loading([
                    html.Button(id='btn-2')
                ], className='loading-2')
            ], className='loading-1')
        ], id='root')

        @app.callback(
            Output('btn-1', 'value'),
            [Input('btn-2', 'n_clicks')]
        )
        def updateDiv(n_clicks):
            if n_clicks is not None:
                with lock:
                    return

            return 'content'

        @app.callback(
            Output('btn-2', 'value'),
            [Input('btn-1', 'n_clicks')]
        )
        def updateDiv(n_clicks):
            if n_clicks is not None:
                with lock:
                    return

            return 'content'

        self.startServer(app)

        self.wait_for_element_by_css_selector(
            '.loading-1 #btn-1'
        )
        self.wait_for_element_by_css_selector(
            '.loading-2 #btn-2'
        )

        with lock:
            self.driver.find_element_by_id('btn-1').click()

            self.wait_for_element_by_css_selector(
                '.loading-2 .dash-spinner'
            )
            self.wait_for_element_by_css_selector(
                '.loading-1 #btn-1'
            )

        self.wait_for_element_by_css_selector(
            '.loading-2 #btn-2'
        )

        with lock:
            self.driver.find_element_by_id('btn-2').click()

            self.wait_for_element_by_css_selector(
                '.loading-1 .dash-spinner'
            )

        self.wait_for_element_by_css_selector(
            '.loading-1 #btn-1'
        )
        self.wait_for_element_by_css_selector(
            '.loading-2 #btn-2'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_dynamic_loading_component(self):
        lock = Lock()

        app = dash.Dash(__name__)
        app.config['suppress_callback_exceptions'] = True

        app.layout = html.Div([
            html.Button(id='btn-1'),
            html.Div(id='div-1')
        ])

        @app.callback(
            Output('div-1', 'children'),
            [Input('btn-1', 'n_clicks')]
        )
        def updateDiv(n_clicks):
            if n_clicks is None:
                return

            with lock:
                return html.Div([
                    html.Button(id='btn-2'),
                    dcc.Loading([
                        html.Button(id='btn-3')
                    ], className='loading-1')
                ])

        @app.callback(
            Output('btn-3', 'content'),
            [Input('btn-2', 'n_clicks')]
        )
        def updateDynamic(n_clicks):
            if n_clicks is None:
                return

            with lock:
                return 'content'

        self.startServer(app)

        self.wait_for_element_by_css_selector(
            '#btn-1'
        )
        self.wait_for_element_by_css_selector(
            '#div-1'
        )

        self.driver.find_element_by_id('btn-1').click()

        self.wait_for_element_by_css_selector(
            '#div-1 #btn-2'
        )
        self.wait_for_element_by_css_selector(
            '.loading-1 #btn-3'
        )

        with lock:
            self.driver.find_element_by_id('btn-2').click()

            self.wait_for_element_by_css_selector(
                '.loading-1 .dash-spinner'
            )

        self.wait_for_element_by_css_selector(
            '#div-1 #btn-2'
        )
        self.wait_for_element_by_css_selector(
            '.loading-1 #btn-3'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_loading_slider(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='test-btn'),
            html.Label(id='test-div', children=['Horizontal Slider']),
            dcc.Slider(
                id='horizontal-slider',
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=5,
            ),
        ])

        @app.callback(
            Output('horizontal-slider', 'value'),
            [Input('test-btn', 'n_clicks')]
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
            self.driver.find_element_by_id('test-btn').click()

            self.wait_for_element_by_css_selector(
                '#horizontal-slider[data-dash-is-loading="true"]'
            )

        self.wait_for_element_by_css_selector(
            '#horizontal-slider:not([data-dash-is-loading="true"])'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_horizontal_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Label('Horizontal Slider'),
            dcc.Slider(
                id='horizontal-slider',
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=5,
            ),
        ])
        self.startServer(app)

        self.wait_for_element_by_css_selector('#horizontal-slider')
        self.snapshot('horizontal slider')

        h_slider = self.driver.find_element_by_css_selector(
            '#horizontal-slider div[role="slider"]'
        )
        h_slider.click()

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_vertical_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Label('Vertical Slider'),
            dcc.Slider(
                id='vertical-slider',
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=5,
                vertical=True,
            ),
        ], style={'height': '500px'})
        self.startServer(app)

        self.wait_for_element_by_css_selector('#vertical-slider')
        self.snapshot('vertical slider')

        v_slider = self.driver.find_element_by_css_selector(
            '#vertical-slider div[role="slider"]'
        )
        v_slider.click()

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_loading_range_slider(self):
        lock = Lock()

        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='test-btn'),
            html.Label(id='test-div', children=['Horizontal Range Slider']),
            dcc.RangeSlider(
                id='horizontal-range-slider',
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=[4, 6],
            ),
        ])

        @app.callback(
            Output('horizontal-range-slider', 'value'),
            [Input('test-btn', 'n_clicks')]
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
            self.driver.find_element_by_id('test-btn').click()

            self.wait_for_element_by_css_selector(
                '#horizontal-range-slider[data-dash-is-loading="true"]'
            )

        self.wait_for_element_by_css_selector(
            '#horizontal-range-slider:not([data-dash-is-loading="true"])'
        )

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_horizontal_range_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Label('Horizontal Range Slider'),
            dcc.RangeSlider(
                id='horizontal-range-slider',
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=[4, 6],
            ),
        ])
        self.startServer(app)

        self.wait_for_element_by_css_selector('#horizontal-range-slider')
        self.snapshot('horizontal range slider')

        h_slider_1 = self.driver.find_element_by_css_selector(
            '#horizontal-range-slider div.rc-slider-handle-1[role="slider"]'
        )
        h_slider_1.click()

        h_slider_2 = self.driver.find_element_by_css_selector(
            '#horizontal-range-slider div.rc-slider-handle-2[role="slider"]'
        )
        h_slider_2.click()

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_vertical_range_slider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Label('Vertical Range Slider'),
            dcc.RangeSlider(
                id='vertical-range-slider',
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=[4, 6],
                vertical=True,
            ),
        ], style={'height': '500px'})
        self.startServer(app)

        self.wait_for_element_by_css_selector('#vertical-range-slider')
        self.snapshot('vertical range slider')

        v_slider_1 = self.driver.find_element_by_css_selector(
            '#vertical-range-slider div.rc-slider-handle-1[role="slider"]'
        )
        v_slider_1.click()

        v_slider_2 = self.driver.find_element_by_css_selector(
            '#vertical-range-slider div.rc-slider-handle-2[role="slider"]'
        )
        v_slider_2.click()

        for entry in self.get_log():
            raise Exception('browser error logged during test', entry)

    def test_gallery(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Div(id='waitfor'),
            html.Label('Upload'),
            dcc.Upload(),

            html.Label('Horizontal Tabs'),
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Tab one', className='test', style={'border': '1px solid magenta'}, children=[
                    html.Div(['Test'])
                ]),
                dcc.Tab(label='Tab two', children=[
                    html.Div([
                        html.H1("This is the content in tab 2"),
                        html.P("A graph here would be nice!")
                    ])
                ], id='tab-one'),
                dcc.Tab(label='Tab three', children=[
                    html.Div([
                        html.H1("This is the content in tab 3"),
                    ])
                ]),
            ],
                style={
                'fontFamily': 'system-ui'
            },
                content_style={
                'border': '1px solid #d6d6d6',
                'padding': '44px'
            },
                parent_style={
                'maxWidth': '1000px',
                'margin': '0 auto'
            }
            ),

            html.Label('Vertical Tabs'),
            dcc.Tabs(id="tabs1", vertical=True, children=[
                dcc.Tab(label='Tab one', children=[
                    html.Div(['Test'])
                ]),
                dcc.Tab(label='Tab two', children=[
                    html.Div([
                        html.H1("This is the content in tab 2"),
                        html.P("A graph here would be nice!")
                    ])
                ]),
                dcc.Tab(label='Tab three', children=[
                    html.Div([
                        html.H1("This is the content in tab 3"),
                    ])
                ]),
            ]
            ),

            html.Label('Dropdown'),
            dcc.Dropdown(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'},
                    {'label': u'北京', 'value': u'北京'}
                ],
                value='MTL',
                id='dropdown'
            ),

            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'},
                    {'label': u'北京', 'value': u'北京'}
                ],
                value=['MTL', 'SF'],
                multi=True
            ),

            html.Label('Radio Items'),
            dcc.RadioItems(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'},
                    {'label': u'北京', 'value': u'北京'}
                ],
                value='MTL'
            ),

            html.Label('Checkboxes'),
            dcc.Checklist(
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': u'Montréal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'},
                    {'label': u'北京', 'value': u'北京'}
                ],
                values=['MTL', 'SF']
            ),

            html.Label('Text Input'),
            dcc.Input(value='', placeholder='type here', type='text',
                      id='textinput'),
            html.Label('Disabled Text Input'),
            dcc.Input(value='disabled', type='text',
                      id='disabled-textinput', disabled=True),

            html.Label('Slider'),
            dcc.Slider(
                min=0,
                max=9,
                marks={i: 'Label {}'.format(i) if i == 1 else str(i)
                       for i in range(1, 6)},
                value=5,
            ),

            html.Label('Graph'),
            dcc.Graph(
                id='graph',
                figure={
                    'data': [{
                        'x': [1, 2, 3],
                        'y': [4, 1, 4]
                    }],
                    'layout': {
                        'title': u'北京'
                    }
                }
            ),

            html.Div([
                html.Label('DatePickerSingle'),
                dcc.DatePickerSingle(
                    id='date-picker-single',
                    date=datetime(1997, 5, 10)
                ),
                html.Div([
                    html.Label('DatePickerSingle - empty input'),
                    dcc.DatePickerSingle(),
                ], id='dt-single-no-date-value'
                ),
                html.Div([
                    html.Label('DatePickerSingle - initial visible month (May 97)'),
                    dcc.DatePickerSingle(
                        initial_visible_month=datetime(1997, 5, 10)
                    ),
                ], id='dt-single-no-date-value-init-month'
                ),
            ]),

            html.Div([
                html.Label('DatePickerRange'),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=datetime(1997, 5, 3),
                    end_date_placeholder_text='Select a date!'
                ),
                html.Div([
                    html.Label('DatePickerRange - empty input'),
                    dcc.DatePickerRange(
                        start_date_placeholder_text='Start date',
                        end_date_placeholder_text='End date'
                    ),
                ], id='dt-range-no-date-values'
                ),
                html.Div([
                    html.Label('DatePickerRange - initial visible month (May 97)'),
                    dcc.DatePickerRange(
                        start_date_placeholder_text='Start date',
                        end_date_placeholder_text='End date',
                        initial_visible_month=datetime(1997, 5, 10)
                    ),
                ], id='dt-range-no-date-values-init-month'
                ),
            ]),

            html.Label('TextArea'),
            dcc.Textarea(
                placeholder='Enter a value... 北京',
                style={'width': '100%'}
            ),

            html.Label('Markdown'),
            dcc.Markdown('''
                #### Dash and Markdown

                Dash supports [Markdown](https://rexxars.github.io/react-markdown/).

                Markdown is a simple way to write and format text.
                It includes a syntax for things like **bold text** and *italics*,
                [links](https://rexxars.github.io/react-markdown/), inline `code` snippets, lists,
                quotes, and more.

                1. Links are auto-rendered: https://dash.plot.ly.
                2. This uses ~commonmark~ GitHub flavored markdown.

                Tables are also supported:

                | First Header  | Second Header |
                | ------------- | ------------- |
                | Content Cell  | Content Cell  |
                | Content Cell  | Content Cell  |

                北京
            '''.replace('    ', '')),
            dcc.Markdown(['# Line one', '## Line two']),
            dcc.Markdown(),
            dcc.SyntaxHighlighter(dedent('''import python
                print(3)'''), language='python'),
            dcc.SyntaxHighlighter([
                'import python',
                'print(3)'
            ], language='python'),
            dcc.SyntaxHighlighter()
        ])
        self.startServer(app)

        self.wait_for_element_by_css_selector('#waitfor')

        self.snapshot('gallery')

        self.driver.find_element_by_css_selector(
            '#dropdown .Select-input input'
        ).send_keys(u'北')
        self.snapshot('gallery - chinese character')

        text_input = self.driver.find_element_by_id('textinput')
        disabled_text_input = self.driver.find_element_by_id(
            'disabled-textinput')
        text_input.send_keys('HODOR')

        # It seems selenium errors when send(ing)_keys on a disabled element.
        # In case this changes we try anyway and catch the particular
        # exception. In any case Percy will snapshot the disabled input style
        # so we are not totally dependent on the send_keys behaviour for
        # testing disabled state.
        try:
            disabled_text_input.send_keys('RODOH')
        except InvalidElementStateException:
            pass

        self.snapshot('gallery - text input')

        # DatePickerSingle and DatePickerRange test
        # for issue with datepicker when date value is `None`
        dt_input_1 = self.driver.find_element_by_css_selector(
            '#dt-single-no-date-value #date'
        )
        dt_input_1.click()
        self.snapshot('gallery - DatePickerSingle\'s datepicker '
                      'when no date value and no initial month specified')
        dt_length = len(dt_input_1.get_attribute('value'))
        dt_input_1.send_keys(dt_length * Keys.BACKSPACE)
        dt_input_1.send_keys("1997-05-03")

        dt_input_2 = self.driver.find_element_by_css_selector(
            '#dt-single-no-date-value-init-month #date'
        )
        self.driver.find_element_by_css_selector(
            'label'
        ).click()
        dt_input_2.click()
        self.snapshot('gallery - DatePickerSingle\'s datepicker '
                      'when no date value, but initial month is specified')
        dt_length = len(dt_input_2.get_attribute('value'))
        dt_input_2.send_keys(dt_length * Keys.BACKSPACE)
        dt_input_2.send_keys("1997-05-03")

        dt_input_3 = self.driver.find_element_by_css_selector(
            '#dt-range-no-date-values #endDate'
        )
        self.driver.find_element_by_css_selector(
            'label'
        ).click()
        dt_input_3.click()
        self.snapshot('gallery - DatePickerRange\'s datepicker '
                      'when neither start date nor end date '
                      'nor initial month is specified')
        dt_length = len(dt_input_3.get_attribute('value'))
        dt_input_3.send_keys(dt_length * Keys.BACKSPACE)
        dt_input_3.send_keys("1997-05-03")

        dt_input_4 = self.driver.find_element_by_css_selector(
            '#dt-range-no-date-values-init-month #endDate'
        )
        self.driver.find_element_by_css_selector(
            'label'
        ).click()
        dt_input_4.click()
        self.snapshot('gallery - DatePickerRange\'s datepicker '
                      'when neither start date nor end date is specified, '
                      'but initial month is')
        dt_length = len(dt_input_4.get_attribute('value'))
        dt_input_4.send_keys(dt_length * Keys.BACKSPACE)
        dt_input_4.send_keys("1997-05-03")

    def test_tabs_in_vertical_mode(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.Tabs(id="tabs", value='tab-3', children=[
                dcc.Tab(label='Tab one', value='tab-1', id='tab-1', children=[
                    html.Div('Tab One Content')
                ]),
                dcc.Tab(label='Tab two', value='tab-2', id='tab-2', children=[
                    html.Div('Tab Two Content')
                ]),
                dcc.Tab(label='Tab three', value='tab-3', id='tab-3', children=[
                    html.Div('Tab Three Content')
                ]),
            ], vertical=True),
            html.Div(id='tabs-content')
        ])

        self.startServer(app=app)
        self.wait_for_text_to_equal('#tab-3', 'Tab three')

        self.snapshot('Tabs - vertical mode')

    def test_tabs_without_children(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.H1('Dash Tabs component demo'),
            dcc.Tabs(id="tabs", value='tab-2', children=[
                dcc.Tab(label='Tab one', value='tab-1', id='tab-1'),
                dcc.Tab(label='Tab two', value='tab-2', id='tab-2'),
            ]),
            html.Div(id='tabs-content')
        ])

        @app.callback(dash.dependencies.Output('tabs-content', 'children'),
                      [dash.dependencies.Input('tabs', 'value')])
        def render_content(tab):
            if tab == 'tab-1':
                return html.Div([
                    html.H3('Test content 1')
                ], id='test-tab-1')
            elif tab == 'tab-2':
                return html.Div([
                    html.H3('Test content 2')
                ], id='test-tab-2')

        self.startServer(app=app)

        self.wait_for_text_to_equal('#tabs-content', 'Test content 2')
        self.snapshot('initial tab - tab 2')

        selected_tab = self.wait_for_element_by_css_selector('#tab-1')
        selected_tab.click()
        time.sleep(1)
        self.wait_for_text_to_equal('#tabs-content', 'Test content 1')

    def test_tabs_with_children_undefined(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.H1('Dash Tabs component demo'),
            dcc.Tabs(id="tabs", value='tab-1'),
            html.Div(id='tabs-content')
        ])

        self.startServer(app=app)

        self.wait_for_element_by_css_selector('#tabs-content')

        self.snapshot('Tabs component with children undefined')

    def test_tabs_render_without_selected(self):
        app = dash.Dash(__name__)

        data = [
            {'id': 'one', 'value': 1},
            {'id': 'two', 'value': 2},
        ]

        menu = html.Div([
            html.Div('one', id='one'),
            html.Div('two', id='two')
        ])

        tabs_one = html.Div([
            dcc.Tabs([
                dcc.Tab(dcc.Graph(id='graph-one'), label='tab-one-one'),
            ])
        ], id='tabs-one', style={'display': 'none'})

        tabs_two = html.Div([
            dcc.Tabs([
                dcc.Tab(dcc.Graph(id='graph-two'), label='tab-two-one'),
            ])
        ], id='tabs-two', style={'display': 'none'})

        app.layout = html.Div([
            menu,
            tabs_one,
            tabs_two
        ])

        for i in ('one', 'two'):

            @app.callback(Output('tabs-{}'.format(i), 'style'),
                          [Input(i, 'n_clicks')])
            def on_click(n_clicks):
                if n_clicks is None:
                    raise PreventUpdate

                if n_clicks % 2 == 1:
                    return {'display': 'block'}
                return {'display': 'none'}

            @app.callback(Output('graph-{}'.format(i), 'figure'),
                          [Input(i, 'n_clicks')])
            def on_click(n_clicks):
                if n_clicks is None:
                    raise PreventUpdate

                return {
                    'data': [
                        {
                            'x': [1, 2, 3, 4],
                            'y': [4, 3, 2, 1]
                        }
                    ],
                    'layout': {
                        'width': 700,
                        'height': 450
                    }
                }

        self.startServer(app=app)

        button_one = self.wait_for_element_by_css_selector('#one')
        button_two = self.wait_for_element_by_css_selector('#two')

        button_one.click()

        # wait for tabs to be loaded after clicking
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-one .main-svg"))
        )

        time.sleep(1)
        self.snapshot("Tabs 1 rendered ")

        button_two.click()

        # wait for tabs to be loaded after clicking
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-two .main-svg"))
        )

        time.sleep(1)
        self.snapshot("Tabs 2 rendered ")

        # do some extra tests while we're here
        # and have access to Graph and plotly.js
        self.check_graph_config_shape()
        self.check_plotlyjs()

    def check_plotlyjs(self):
        # find plotly.js files in the dist folder, check that there's only one
        all_dist = os.listdir(dcc.__path__[0])
        js_re = r'^plotly-(.*)\.min\.js$'
        plotlyjs_dist = [fn for fn in all_dist if re.match(js_re, fn)]

        self.assertEqual(len(plotlyjs_dist), 1)

        # check that the version matches what we see in the page
        page_version = self.driver.execute_script('return Plotly.version;')
        dist_version = re.match(js_re, plotlyjs_dist[0]).groups()[0]
        self.assertEqual(page_version, dist_version)

    def check_graph_config_shape(self):
        config_schema = self.driver.execute_script(
            'return Plotly.PlotSchema.get().config;'
        )
        with open(os.path.join(dcc.__path__[0], 'metadata.json')) as meta:
            graph_meta = json.load(meta)['src/components/Graph.react.js']
            config_prop_shape = graph_meta['props']['config']['type']['value']

        ignored_config = [
            'setBackground',
            'showSources',
            'logging',
            'globalTransforms',
            'role'
        ]

        def crawl(schema, props):
            for prop_name in props:
                self.assertIn(prop_name, schema)

            for item_name, item in schema.items():
                if item_name in ignored_config:
                    continue

                self.assertIn(item_name, props)
                if 'valType' not in item:
                    crawl(item, props[item_name]['value'])

        crawl(config_schema, config_prop_shape)

    def test_tabs_without_value(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.H1('Dash Tabs component demo'),
            dcc.Tabs(id="tabs-without-value", children=[
                dcc.Tab(label='Tab One', value='tab-1'),
                dcc.Tab(label='Tab Two', value='tab-2'),
            ]),
            html.Div(id='tabs-content')
        ])

        @app.callback(Output('tabs-content', 'children'),
                      [Input('tabs-without-value', 'value')])
        def render_content(tab):
            if tab == 'tab-1':
                return html.H3('Default selected Tab content 1')
            elif tab == 'tab-2':
                return html.H3('Tab content 2')

        self.startServer(app=app)

        self.wait_for_text_to_equal('#tabs-content', 'Default selected Tab content 1')

        self.snapshot('Tab 1 should be selected by default')

    def test_graph_does_not_resize_in_tabs(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.H1('Dash Tabs component demo'),
            dcc.Tabs(id="tabs-example", value='tab-1-example', children=[
                dcc.Tab(label='Tab One', value='tab-1-example', id='tab-1'),
                dcc.Tab(label='Tab Two', value='tab-2-example', id='tab-2'),
            ]),
            html.Div(id='tabs-content-example')
        ])

        @app.callback(Output('tabs-content-example', 'children'),
                      [Input('tabs-example', 'value')])
        def render_content(tab):
            if tab == 'tab-1-example':
                return html.Div([
                    html.H3('Tab content 1'),
                    dcc.Graph(
                        id='graph-1-tabs',
                        figure={
                            'data': [{
                                'x': [1, 2, 3],
                                'y': [3, 1, 2],
                                'type': 'bar'
                            }]
                        }
                    )
                ])
            elif tab == 'tab-2-example':
                return html.Div([
                    html.H3('Tab content 2'),
                    dcc.Graph(
                        id='graph-2-tabs',
                        figure={
                            'data': [{
                                'x': [1, 2, 3],
                                'y': [5, 10, 6],
                                'type': 'bar'
                            }]
                        }
                    )
                ])
        self.startServer(app=app)

        tab_one = self.wait_for_element_by_css_selector('#tab-1')
        tab_two = self.wait_for_element_by_css_selector('#tab-2')

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab-2"))
        )

        self.snapshot("Tabs with Graph - initial (graph should not resize)")
        tab_two.click()

        # wait for Graph's internal svg to be loaded after clicking
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-2-tabs .main-svg"))
        )

        self.snapshot("Tabs with Graph - clicked tab 2 (graph should not resize)")

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tab-1"))
        )

        tab_one.click()

        # wait for Graph to be loaded after clicking
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph-1-tabs .main-svg"))
        )

        self.snapshot("Tabs with Graph - clicked tab 1 (graph should not resize)")

    def test_location_link(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Div(id='waitfor'),
            dcc.Location(id='test-location', refresh=False),

            dcc.Link(
                html.Button('I am a clickable button'),
                id='test-link',
                href='/test/pathname'),
            dcc.Link(
                html.Button('I am a clickable hash button'),
                id='test-link-hash',
                href='#test'),
            dcc.Link(
                html.Button('I am a clickable search button'),
                id='test-link-search',
                href='?testQuery=testValue',
                refresh=False),
            html.Button('I am a magic button that updates pathname',
                        id='test-button'),
            html.A('link to click', href='/test/pathname/a', id='test-a'),
            html.A('link to click', href='#test-hash', id='test-a-hash'),
            html.A('link to click', href='?queryA=valueA', id='test-a-query'),
            html.Div(id='test-pathname', children=[]),
            html.Div(id='test-hash', children=[]),
            html.Div(id='test-search', children=[]),
        ])

        @app.callback(
            output=Output(component_id='test-pathname',
                          component_property='children'),
            inputs=[Input(component_id='test-location', component_property='pathname')])
        def update_location_on_page(pathname):
            return pathname

        @app.callback(
            output=Output(component_id='test-hash',
                          component_property='children'),
            inputs=[Input(component_id='test-location', component_property='hash')])
        def update_location_on_page(hash_val):
            if hash_val is None:
                return ''

            return hash_val

        @app.callback(
            output=Output(component_id='test-search',
                          component_property='children'),
            inputs=[Input(component_id='test-location', component_property='search')])
        def update_location_on_page(search):
            if search is None:
                return ''

            return search

        @app.callback(
            output=Output(component_id='test-location',
                          component_property='pathname'),
            inputs=[Input(component_id='test-button',
                          component_property='n_clicks')],
            state=[State(component_id='test-location', component_property='pathname')])
        def update_pathname(n_clicks, current_pathname):
            if n_clicks is not None:
                return '/new/pathname'

            return current_pathname

        self.startServer(app=app)

        time.sleep(1)
        self.snapshot('link -- location')

        # Check that link updates pathname
        self.wait_for_element_by_css_selector('#test-link').click()
        self.assertEqual(
            self.driver.current_url.replace('http://localhost:8050', ''),
            '/test/pathname')
        self.wait_for_text_to_equal('#test-pathname', '/test/pathname')

        # Check that hash is updated in the Location
        self.wait_for_element_by_css_selector('#test-link-hash').click()
        self.wait_for_text_to_equal('#test-pathname', '/test/pathname')
        self.wait_for_text_to_equal('#test-hash', '#test')
        self.snapshot('link -- /test/pathname#test')

        # Check that search is updated in the Location -- note that this goes through href and therefore wipes the hash
        self.wait_for_element_by_css_selector('#test-link-search').click()
        self.wait_for_text_to_equal('#test-search', '?testQuery=testValue')
        self.wait_for_text_to_equal('#test-hash', '')
        self.snapshot('link -- /test/pathname?testQuery=testValue')

        # Check that pathname is updated through a Button click via props
        self.wait_for_element_by_css_selector('#test-button').click()
        self.wait_for_text_to_equal('#test-pathname', '/new/pathname')
        self.wait_for_text_to_equal('#test-search', '?testQuery=testValue')
        self.snapshot('link -- /new/pathname?testQuery=testValue')

        # Check that pathname is updated through an a tag click via props
        self.wait_for_element_by_css_selector('#test-a').click()
        try:
            self.wait_for_element_by_css_selector('#waitfor')
        except Exception as e:
            print(self.wait_for_element_by_css_selector(
                '#_dash-app-content').get_attribute('innerHTML'))
            raise e

        self.wait_for_text_to_equal('#test-pathname', '/test/pathname/a')
        self.wait_for_text_to_equal('#test-search', '')
        self.wait_for_text_to_equal('#test-hash', '')
        self.snapshot('link -- /test/pathname/a')

        # Check that hash is updated through an a tag click via props
        self.wait_for_element_by_css_selector('#test-a-hash').click()
        self.wait_for_text_to_equal('#test-pathname', '/test/pathname/a')
        self.wait_for_text_to_equal('#test-search', '')
        self.wait_for_text_to_equal('#test-hash', '#test-hash')
        self.snapshot('link -- /test/pathname/a#test-hash')

        # Check that hash is updated through an a tag click via props
        self.wait_for_element_by_css_selector('#test-a-query').click()
        self.wait_for_element_by_css_selector('#waitfor')
        self.wait_for_text_to_equal('#test-pathname', '/test/pathname/a')
        self.wait_for_text_to_equal('#test-search', '?queryA=valueA')
        self.wait_for_text_to_equal('#test-hash', '')
        self.snapshot('link -- /test/pathname/a?queryA=valueA')

    def test_link_scroll(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Location(id='test-url', refresh=False),

            html.Div(id='push-to-bottom', children=[], style={
                'display': 'block',
                'height': '200vh'
            }),
            html.Div(id='page-content'),
            dcc.Link('Test link', href='/test-link', id='test-link')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('page-content', 'children'),
                      [Input('test-url', 'pathname')])
        def display_page(pathname):
            call_count.value = call_count.value + 1
            return 'You are on page {}'.format(pathname)

        self.startServer(app=app)

        time.sleep(2)

        # callback is called twice when defined
        self.assertEqual(
            call_count.value,
            2
        )

        # test if link correctly scrolls back to top of page
        test_link = self.wait_for_element_by_css_selector('#test-link')
        test_link.send_keys(Keys.NULL)
        test_link.click()
        time.sleep(2)

        # test link still fires update on Location
        page_content = self.wait_for_element_by_css_selector('#page-content')
        self.assertNotEqual(page_content.text, 'You are on page /')

        self.wait_for_text_to_equal(
            '#page-content', 'You are on page /test-link')

        # test if rendered Link's <a> tag has a href attribute
        link_href = test_link.get_attribute("href")
        self.assertEqual(link_href, 'http://localhost:8050/test-link')

        # test if callback is only fired once (offset of 2)
        self.assertEqual(
            call_count.value,
            3
        )

    def test_candlestick(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Button(
                id='button',
                children='Update Candlestick',
                n_clicks=0
            ),
            dcc.Graph(id='graph')
        ])

        @app.callback(Output('graph', 'figure'), [Input('button', 'n_clicks')])
        def update_graph(n_clicks):
            return {
                'data': [{
                    'open': [1] * 5,
                    'high': [3] * 5,
                    'low': [0] * 5,
                    'close': [2] * 5,
                    'x': [n_clicks] * 5,
                    'type': 'candlestick'
                }]
            }
        self.startServer(app=app)

        button = self.wait_for_element_by_css_selector('#button')
        self.snapshot('candlestick - initial')
        button.click()
        time.sleep(1)
        self.snapshot('candlestick - 1 click')

        button.click()
        time.sleep(1)
        self.snapshot('candlestick - 2 click')

    def test_graphs_with_different_figures(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [2, 4, 5],
                         'type': 'bar', 'name': u'Montréal'},
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                }
            ),
            dcc.Graph(
                id='example-graph-2',
                figure={
                    'data': [
                        {'x': [20, 24, 33], 'y': [5, 2, 3],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [11, 22, 33], 'y': [22, 44, 55],
                         'type': 'bar', 'name': u'Montréal'},
                    ],
                    'layout': {
                        'title': 'Dash Data Visualization'
                    }
                }
            ),
            html.Div(id='restyle-data'),
            html.Div(id='relayout-data')
        ])

        @app.callback(Output('restyle-data', 'children'), [Input('example-graph', 'restyleData')])
        def show_restyle_data(data):
            if data is None:  # ignore initial
                return ''
            return json.dumps(data)

        @app.callback(Output('relayout-data', 'children'), [Input('example-graph', 'relayoutData')])
        def show_relayout_data(data):
            if data is None or 'autosize' in data:  # ignore initial & auto width
                return ''
            return json.dumps(data)

        self.startServer(app=app)

        # use this opportunity to test restyleData, since there are multiple
        # traces on this graph
        legendToggle = self.driver.find_element_by_css_selector('#example-graph .traces:first-child .legendtoggle')
        legendToggle.click()
        self.wait_for_text_to_equal('#restyle-data', '[{"visible": ["legendonly"]}, [0]]')

        # move snapshot after click, so it's more stable with the wait
        self.snapshot('2 graphs with different figures')

        # and test relayoutData while we're at it
        autoscale = self.driver.find_element_by_css_selector('#example-graph .ewdrag')
        autoscale.click()
        autoscale.click()
        self.wait_for_text_to_equal('#relayout-data', '{"xaxis.autorange": true}')

    def test_graphs_without_ids(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Graph(className='graph-no-id-1'),
            dcc.Graph(className='graph-no-id-2'),
        ])

        self.startServer(app=app)

        graph_1 = self.wait_for_element_by_css_selector('.graph-no-id-1')
        graph_2 = self.wait_for_element_by_css_selector('.graph-no-id-2')

        self.assertNotEqual(graph_1.get_attribute('id'), graph_2.get_attribute('id'))

    def test_datepickerrange_updatemodes(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date_placeholder_text='Select a start date!',
                end_date_placeholder_text='Select an end date!',
                updatemode='bothdates'
            ),
            html.Div(id='date-picker-range-output')
        ])

        @app.callback(
            dash.dependencies.Output('date-picker-range-output', 'children'),
            [dash.dependencies.Input('date-picker-range', 'start_date'),
             dash.dependencies.Input('date-picker-range', 'end_date')])
        def update_output(start_date, end_date):
            return '{} - {}'.format(start_date, end_date)

        self.startServer(app=app)

        start_date = self.wait_for_element_by_css_selector('#startDate')
        start_date.click()

        end_date = self.wait_for_element_by_css_selector('#endDate')
        end_date.click()

        self.wait_for_text_to_equal('#date-picker-range-output', 'None - None')

        # using mouse click with fixed day range, this can be improved
        # once we start refactoring the test structure
        start_date.click()

        sday = self.driver.find_element_by_xpath("//td[text()='1' and @tabindex='0']")
        sday.click()
        self.wait_for_text_to_equal('#date-picker-range-output', 'None - None')

        eday = self.driver.find_elements_by_xpath("//td[text()='28']")[1]
        eday.click()

        date_tokens = set(start_date.get_attribute('value').split('/'))
        date_tokens.update(end_date.get_attribute('value').split('/'))

        self.assertEqual(
            set(itertools.chain(*[
                _.split('-')
                for _ in self.driver.find_element_by_css_selector(
                    '#date-picker-range-output').text.split(' - ')])),
            date_tokens,
            "date should match the callback output")

    def test_interval(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            html.Div(id='output'),
            dcc.Interval(id='interval', interval=1, max_intervals=2)
        ])

        @app.callback(Output('output', 'children'),
                      [Input('interval', 'n_intervals')])
        def update_text(n):
            return "{}".format(n)

        self.startServer(app=app)

        # wait for interval to finish
        time.sleep(5)

        self.wait_for_text_to_equal('#output', '2')

    def test_if_interval_can_be_restarted(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Interval(
                id='interval',
                interval=100,
                n_intervals=0,
                max_intervals=-1
            ),

            html.Button('Start', id='start', n_clicks_timestamp=-1),
            html.Button('Stop', id='stop', n_clicks_timestamp=-1),

            html.Div(id='output')

        ])

        @app.callback(
            Output('interval', 'max_intervals'),
            [Input('start', 'n_clicks_timestamp'),
             Input('stop', 'n_clicks_timestamp')])
        def start_stop(start, stop):
            if start < stop:
                return 0
            else:
                return -1

        @app.callback(Output('output', 'children'), [Input('interval', 'n_intervals')])
        def display_data(n_intervals):
            return 'Updated {}'.format(n_intervals)

        self.startServer(app=app)

        start_button = self.wait_for_element_by_css_selector('#start')
        stop_button = self.wait_for_element_by_css_selector('#stop')

        # interval will start itself, we wait a second before pressing 'stop'
        time.sleep(1)

        # get the output after running it for a bit
        output = self.wait_for_element_by_css_selector('#output')
        stop_button.click()

        time.sleep(1)

        # get the output after it's stopped, it shouldn't be higher than before
        output_stopped = self.wait_for_element_by_css_selector('#output')

        self.wait_for_text_to_equal("#output", output_stopped.text)

        # This test logic is bad
        # same element check for same text will always be true.
        self.assertEqual(output.text, output_stopped.text)

    def _test_confirm(self, app, test_name, add_callback=True):
        count = Value('i', 0)

        if add_callback:
            @app.callback(Output('confirmed', 'children'),
                          [Input('confirm', 'submit_n_clicks'),
                           Input('confirm', 'cancel_n_clicks')],
                          [State('confirm', 'submit_n_clicks_timestamp'),
                           State('confirm', 'cancel_n_clicks_timestamp')])
            def _on_confirmed(submit_n_clicks, cancel_n_clicks,
                              submit_timestamp, cancel_timestamp):
                if not submit_n_clicks and not cancel_n_clicks:
                    return ''
                count.value += 1
                if (submit_timestamp and cancel_timestamp is None) or\
                        (submit_timestamp > cancel_timestamp):
                    return 'confirmed'
                else:
                    return 'canceled'

        self.startServer(app)
        button = self.wait_for_element_by_css_selector('#button')
        self.snapshot(test_name + ' -> initial')

        button.click()
        time.sleep(1)
        self.driver.switch_to.alert.accept()

        if add_callback:
            self.wait_for_text_to_equal('#confirmed', 'confirmed')
            self.snapshot(test_name + ' -> confirmed')

        button.click()
        time.sleep(0.5)
        self.driver.switch_to.alert.dismiss()
        time.sleep(0.5)

        if add_callback:
            self.wait_for_text_to_equal('#confirmed', 'canceled')
            self.snapshot(test_name + ' -> canceled')

        if add_callback:
            self.assertEqual(2, count.value,
                             'Expected 2 callback but got ' + str(count.value))

    def test_confirm(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='button', children='Send confirm', n_clicks=0),
            dcc.ConfirmDialog(id='confirm', message='Please confirm.'),
            html.Div(id='confirmed')
        ])

        @app.callback(Output('confirm', 'displayed'),
                      [Input('button', 'n_clicks')])
        def on_click_confirm(n_clicks):
            if n_clicks:
                return True

        self._test_confirm(app, 'ConfirmDialog')

    def test_confirm_dialog_provider(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            dcc.ConfirmDialogProvider(
                html.Button('click me', id='button'),
                id='confirm', message='Please confirm.'),
            html.Div(id='confirmed')
        ])

        self._test_confirm(app, 'ConfirmDialogProvider')

    def test_confirm_without_callback(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.ConfirmDialogProvider(
                html.Button('click me', id='button'),
                id='confirm', message='Please confirm.'),
            html.Div(id='confirmed')
        ])
        self._test_confirm(app, 'ConfirmDialogProviderWithoutCallback',
                           add_callback=False)

    def test_confirm_as_children(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='button', children='Send confirm'),
            html.Div(id='confirm-container'),
            dcc.Location(id='dummy-location')
        ])

        @app.callback(Output('confirm-container', 'children'),
                      [Input('button', 'n_clicks')])
        def on_click(n_clicks):
            if n_clicks:
                return dcc.ConfirmDialog(
                    displayed=True,
                    id='confirm',
                    key='confirm-{}'.format(time.time()),
                    message='Please confirm.')

        self.startServer(app)

        button = self.wait_for_element_by_css_selector('#button')

        button.click()
        time.sleep(2)

        self.driver.switch_to.alert.accept()

    def test_empty_graph(self):
        app = dash.Dash(__name__)

        app.layout = html.Div([
            html.Button(id='click', children='Click me'),
            dcc.Graph(
                id='graph',
                figure={
                    'data': [dict(x=[1, 2, 3], y=[1, 2, 3], type='scatter')]
                }
            )
        ])

        @app.callback(dash.dependencies.Output('graph', 'figure'),
                      [dash.dependencies.Input('click', 'n_clicks')],
                      [dash.dependencies.State('graph', 'figure')])
        def render_content(click, prev_graph):
            if click:
                return {}
            return prev_graph

        self.startServer(app)
        button = self.wait_for_element_by_css_selector('#click')
        button.click()
        time.sleep(2)  # Wait for graph to re-render
        self.snapshot('render-empty-graph')

    def test_graph_extend_trace(self):
        app = dash.Dash(__name__)

        def generate_with_id(id, data=None):
            if data is None:
                data = [{'x': [0, 1, 2, 3, 4],
                         'y': [0, .5, 1, .5, 0]
                         }]

            return html.Div([html.P(id),
                             dcc.Graph(id=id,
                                       figure=dict(data=data)),
                             html.Div(id='output_{}'.format(id))])

        figs = ['trace_will_extend',
                'trace_will_extend_with_no_indices',
                'trace_will_extend_with_max_points']

        layout = [generate_with_id(id) for id in figs]

        figs.append('trace_will_allow_repeated_extend')
        data = [{'y': [0, 0, 0]}]
        layout.append(generate_with_id(figs[-1], data))

        figs.append('trace_will_extend_selectively')
        data = [{'x': [0, 1, 2, 3, 4], 'y': [0, .5, 1, .5, 0]},
                {'x': [0, 1, 2, 3, 4], 'y': [1, 1, 1, 1, 1]}]
        layout.append(generate_with_id(figs[-1], data))

        layout.append(dcc.Interval(
            id='interval_extendablegraph_update',
            interval=10,
            n_intervals=0,
            max_intervals=1))

        layout.append(dcc.Interval(
            id='interval_extendablegraph_extendtwice',
            interval=500,
            n_intervals=0,
            max_intervals=2))

        app.layout = html.Div(layout)

        @app.callback(Output('trace_will_allow_repeated_extend', 'extendData'),
                      [Input('interval_extendablegraph_extendtwice', 'n_intervals')])
        def trace_will_allow_repeated_extend(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            return dict(y=[[.1, .2, .3, .4, .5]])

        @app.callback(Output('trace_will_extend', 'extendData'),
                      [Input('interval_extendablegraph_update', 'n_intervals')])
        def trace_will_extend(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [.1, .2, .3, .4, .5]
            return dict(x=[x_new], y=[y_new]), [0]

        @app.callback(Output('trace_will_extend_selectively', 'extendData'),
                      [Input('interval_extendablegraph_update', 'n_intervals')])
        def trace_will_extend_selectively(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [.1, .2, .3, .4, .5]
            return dict(x=[x_new], y=[y_new]), [1]

        @app.callback(Output('trace_will_extend_with_no_indices', 'extendData'),
                      [Input('interval_extendablegraph_update', 'n_intervals')])
        def trace_will_extend_with_no_indices(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [.1, .2, .3, .4, .5]
            return dict(x=[x_new], y=[y_new])

        @app.callback(Output('trace_will_extend_with_max_points', 'extendData'),
                      [Input('interval_extendablegraph_update', 'n_intervals')])
        def trace_will_extend_with_max_points(n_intervals):
            if n_intervals is None or n_intervals < 1:
                raise PreventUpdate

            x_new = [5, 6, 7, 8, 9]
            y_new = [.1, .2, .3, .4, .5]
            return dict(x=[x_new], y=[y_new]), [0], 7

        for id in figs:
            @app.callback(Output('output_{}'.format(id), 'children'),
                          [Input(id, 'extendData')],
                          [State(id, 'figure')])
            def display_data(trigger, fig):
                return json.dumps(fig['data'])

        self.startServer(app)

        comparison = json.dumps([
            dict(
                x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                y=[0, .5, 1, .5, 0, .1, .2, .3, .4, .5]
            )
        ])
        self.wait_for_text_to_equal('#output_trace_will_extend', comparison)
        self.wait_for_text_to_equal('#output_trace_will_extend_with_no_indices', comparison)
        comparison = json.dumps([
            dict(
                x=[0, 1, 2, 3, 4],
                y=[0, .5, 1, .5, 0]
            ),
            dict(
                x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                y=[1, 1, 1, 1, 1, .1, .2, .3, .4, .5]
            )
        ])
        self.wait_for_text_to_equal('#output_trace_will_extend_selectively', comparison)

        comparison = json.dumps([
            dict(
                x=[3, 4, 5, 6, 7, 8, 9],
                y=[.5, 0, .1, .2, .3, .4, .5]
            )
        ])
        self.wait_for_text_to_equal('#output_trace_will_extend_with_max_points', comparison)

        comparison = json.dumps([
            dict(
                y=[0, 0, 0, .1, .2, .3, .4, .5, .1, .2, .3, .4, .5]
            )
        ])
        self.wait_for_text_to_equal('#output_trace_will_allow_repeated_extend', comparison)

    def test_storage_component(self):
        app = dash.Dash(__name__)

        getter = 'return JSON.parse(window.{}.getItem("{}"));'
        clicked_getter = getter.format('localStorage', 'storage')
        dummy_getter = getter.format('sessionStorage', 'dummy')
        dummy_data = 'Hello dummy'

        app.layout = html.Div([
            dcc.Store(id='storage',
                      storage_type='local'),
            html.Button('click me', id='btn'),
            html.Button('clear', id='clear-btn'),
            html.Button('set-init-storage',
                        id='set-init-storage'),
            dcc.Store(id='dummy',
                      storage_type='session',
                      data=dummy_data),
            dcc.Store(id='memory',
                      storage_type='memory'),
            html.Div(id='memory-output'),
            dcc.Store(id='initial-storage',
                      storage_type='session'),
            html.Div(id='init-output')
        ])

        @app.callback(Output('storage', 'data'),
                      [Input('btn', 'n_clicks')],
                      [State('storage', 'data')])
        def on_click(n_clicks, storage):
            if n_clicks is None:
                return
            storage = storage or {}
            return {'clicked': storage.get('clicked', 0) + 1}

        @app.callback(Output('storage', 'clear_data'),
                      [Input('clear-btn', 'n_clicks')])
        def on_clear(n_clicks):
            if n_clicks is None:
                return
            return True

        @app.callback(Output('memory', 'data'), [Input('storage', 'data')])
        def on_memory(data):
            return data

        @app.callback(Output('memory-output', 'children'),
                      [Input('memory', 'data')])
        def on_memory2(data):
            if data is None:
                return ''
            return json.dumps(data)

        @app.callback(Output('initial-storage', 'data'),
                      [Input('set-init-storage', 'n_clicks')])
        def on_init(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            return 'initialized'

        @app.callback(Output('init-output', 'children'),
                      [Input('initial-storage', 'modified_timestamp')],
                      [State('initial-storage', 'data')])
        def init_output(ts, data):
            return json.dumps({'data': data, 'ts': ts})

        self.startServer(app)

        time.sleep(1)

        dummy = self.driver.execute_script(dummy_getter)
        self.assertEqual(dummy_data, dummy)

        click_btn = self.wait_for_element_by_css_selector('#btn')
        clear_btn = self.wait_for_element_by_css_selector('#clear-btn')
        mem = self.wait_for_element_by_css_selector('#memory-output')

        for i in range(1, 11):
            click_btn.click()
            time.sleep(1)

            click_data = self.driver.execute_script(clicked_getter)
            self.assertEqual(i, click_data.get('clicked'))
            self.assertEqual(i, int(json.loads(mem.text).get('clicked')))

        clear_btn.click()
        time.sleep(1)

        cleared_data = self.driver.execute_script(clicked_getter)
        self.assertTrue(cleared_data is None)
        # Did mem also got cleared ?
        self.assertFalse(mem.text)

        # Test initial timestamp output
        init_btn = self.wait_for_element_by_css_selector('#set-init-storage')
        init_btn.click()
        ts = int(time.time() * 1000)
        time.sleep(1)
        self.driver.refresh()
        time.sleep(2)
        init = self.wait_for_element_by_css_selector('#init-output')
        init = json.loads(init.text)
        self.assertAlmostEqual(ts, init.get('ts'), delta=1000)
        self.assertEqual('initialized', init.get('data'))

    def test_store_nested_data(self):
        app = dash.Dash(__name__)

        nested = {'nested': {'nest': 'much'}}
        nested_list = dict(my_list=[1, 2, 3])

        app.layout = html.Div([
            dcc.Store(id='store', storage_type='local'),
            html.Button('set object as key', id='obj-btn'),
            html.Button('set list as key', id='list-btn'),
            html.Output(id='output')
        ])

        @app.callback(Output('store', 'data'),
                      [Input('obj-btn', 'n_clicks_timestamp'),
                       Input('list-btn', 'n_clicks_timestamp')])
        def on_obj_click(obj_ts, list_ts):
            if obj_ts is None and list_ts is None:
                raise PreventUpdate

            # python 3 got the default props bug. plotly/dash#396
            if (obj_ts and not list_ts) or obj_ts > list_ts:
                return nested
            else:
                return nested_list

        @app.callback(Output('output', 'children'),
                      [Input('store', 'modified_timestamp')],
                      [State('store', 'data')])
        def on_ts(ts, data):
            if ts is None:
                raise PreventUpdate
            return json.dumps(data)

        self.startServer(app)

        obj_btn = self.wait_for_element_by_css_selector('#obj-btn')
        list_btn = self.wait_for_element_by_css_selector('#list-btn')

        obj_btn.click()
        time.sleep(1)
        self.wait_for_text_to_equal('#output', json.dumps(nested))
        # it would of crashed the app before adding the recursive check.

        list_btn.click()
        time.sleep(1)
        self.wait_for_text_to_equal('#output', json.dumps(nested_list))

    def test_user_supplied_css(self):
        app = dash.Dash(__name__)

        app.layout = html.Div(className="test-input-css", children=[dcc.Input()])

        self.startServer(app)

        self.wait_for_element_by_css_selector('.test-input-css')
        self.snapshot('styled input - width: 100%, border-color: hotpink')

    def test_logout_btn(self):
        app = dash.Dash(__name__)

        @app.server.route('/_logout', methods=['POST'])
        def on_logout():
            rep = flask.redirect('/logged-out')
            rep.set_cookie('logout-cookie', '', 0)
            return rep

        app.layout = html.Div([
            html.H2('Logout test'),
            dcc.Location(id='location'),
            html.Div(id='content'),
        ])

        @app.callback(Output('content', 'children'),
                      [Input('location', 'pathname')])
        def on_location(location_path):
            if location_path is None:
                raise PreventUpdate

            if 'logged-out' in location_path:
                return 'Logged out'
            else:

                @flask.after_this_request
                def _insert_cookie(rep):
                    rep.set_cookie('logout-cookie', 'logged-in')
                    return rep

                return dcc.LogoutButton(id='logout-btn', logout_url='/_logout')

        self.startServer(app)
        time.sleep(1)
        self.snapshot('Logout button')

        self.assertEqual(
            'logged-in',
            self.driver.get_cookie('logout-cookie')['value'])
        logout_button = self.wait_for_element_by_css_selector('#logout-btn')
        logout_button.click()
        self.wait_for_text_to_equal('#content', 'Logged out')

        self.assertFalse(self.driver.get_cookie('logout-cookie'))

    def test_state_and_inputs(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(value='Initial Input', id='input'),
            dcc.Input(value='Initial State', id='state'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'children'),
                      inputs=[Input('input', 'value')],
                      state=[State('state', 'value')])
        def update_output(input, state):
            call_count.value += 1
            return 'input="{}", state="{}"'.format(input, state)

        self.startServer(app)
        output = lambda: self.driver.find_element_by_id('output')  # noqa: E731
        input = lambda: self.driver.find_element_by_id('input')  # noqa: E731
        state = lambda: self.driver.find_element_by_id('state')  # noqa: E731

        # callback gets called with initial input
        wait_for(lambda: call_count.value == 1)
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

    def test_simple_callback(self):
        app = dash.Dash(__name__)
        app.layout = html.Div([
            dcc.Input(
                id='input',
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

        input1 = self.wait_for_element_by_css_selector('#input')
        input1.send_keys('hello world')
        output1 = self.wait_for_element_by_css_selector('#output-1')
        self.wait_for_text_to_equal('#output-1', 'hello world')
        output1.click()  # Lose focus, no callback sent for value.

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            # plus one for each hello world character
            1 + len('hello world')
        )

    def test_store_type_updates(self):
        app = dash.Dash(__name__)

        types = [
            ('str', 'hello'),
            ('number', 1),
            ('dict', {'data': [2, 3, None]}),
            ('list', [5, 6, 7]),
            ('null', None),
            ('bool', True),
            ('bool', False),
            ('empty-dict', {}),
        ]
        types_changes = list(
            itertools.chain(*itertools.combinations(types, 2))
        ) + [  # No combinations as it add much test time.
            ('list-dict-1', [1, 2, {'data': [55, 66, 77], 'dummy': 'dum'}]),
            ('list-dict-2', [1, 2, {'data': [111, 99, 88]}]),
            ('dict-3', {'a': 1, 'c': 1}),
            ('dict-2', {'a': 1, 'b': None}),
        ]

        app.layout = html.Div([
            html.Div(id='output'),
            html.Button('click', id='click'),
            dcc.Store(id='store')
        ])

        @app.callback(Output('output', 'children'),
                      [Input('store', 'modified_timestamp')],
                      [State('store', 'data')])
        def on_data(ts, data):
            if ts is None:
                raise PreventUpdate

            return json.dumps(data)

        @app.callback(Output('store', 'data'), [Input('click', 'n_clicks')])
        def on_click(n_clicks):
            if n_clicks is None:
                raise PreventUpdate

            return types_changes[n_clicks - 1][1]

        self.startServer(app)

        button = self.wait_for_element_by_css_selector('#click')

        for i, type_change in enumerate(types_changes):
            button.click()
            try:
                self.wait_for_text_to_equal(
                    '#output', json.dumps(type_change[1]),
                )
            except TimeoutException:
                raise Exception(
                    'Output type did not change from {} to {}'.format(
                        types_changes[i - 1],
                        type_change
                    )
                )
