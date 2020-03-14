# -*- coding: utf-8 -*-
import os
import sys
from multiprocessing import Lock
import time
import dash
from dash.dependencies import Input, Output, State
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
        def update_test_pathname(pathname):
            return pathname

        @app.callback(
            output=Output(component_id='test-hash',
                          component_property='children'),
            inputs=[Input(component_id='test-location', component_property='hash')])
        def update_test_hash(hash_val):
            if hash_val is None:
                return ''

            return hash_val

        @app.callback(
            output=Output(component_id='test-search',
                          component_property='children'),
            inputs=[Input(component_id='test-location', component_property='search')])
        def update_test_search(search):
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
