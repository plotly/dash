from dash import Dash
from dash.dependencies import Input, Output, State, Event
import dash
import dash_html_components as html
import dash_core_components as dcc
from IntegrationTests import IntegrationTests
import mock
from utils import assert_clean_console, wait_for
from multiprocessing import Value
import time


class Tests(IntegrationTests):

    def test_initial_state(self):
        app = Dash(__name__)
        app.layout = html.Div([
            'Basic string',
            3.14,
            None,
            html.Div('Child div with basic string',
                     id='p.c.3',
                     className="my-class",
                     title='tooltip',
                     style={'color': 'red', 'fontSize': 30, 'font-size': 10}
                     ),
            html.Div(id='p.c.4'),
            html.Div([
                html.Div('Grandchild div', id='p.c.5.p.c.0'),
                html.Div([
                    html.Div('Great grandchild', id='p.c.5.p.c.1.p.c.0'),
                    3.14159,
                    'another basic string'
                ], id='p.c.5.p.c.1'),
                html.Div([
                    html.Div(
                        html.Div([
                            html.Div([
                                html.Div(
                                    id='p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0'
                                ),
                                '',
                                html.Div(
                                    id='p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2'
                                )
                            ], id='p.c.5.p.c.2.p.c.0.p.c.p.c.0')
                        ], id='p.c.5.p.c.2.p.c.0.p.c'),
                        id='p.c.5.p.c.2.p.c.0'
                    )
                ], id='p.c.5.p.c.2')
            ], id='p.c.5')
        ])

        self.startServer(app)
        el = self.driver.find_element_by_id('_dash-app-content')

        rendered_dom = '''
            <div data-reactroot="">
                <div>
                    <!-- react-text: 5 -->
                        Basic string
                    <!-- /react-text -->

                    <!-- react-text: 6 -->
                        3.14
                    <!-- /react-text -->

                    <div class="my-class" id="p.c.3" title="tooltip" style="color: red; font-size: 30px;">
                        Child div with basic string
                    </div>

                    <div id="p.c.4">
                    </div>

                    <div id="p.c.5">
                        <div id="p.c.5.p.c.0">
                            Grandchild div
                        </div>

                        <div id="p.c.5.p.c.1">
                            <div id="p.c.5.p.c.1.p.c.0">
                                Great grandchild
                            </div>

                            <!-- react-text: 13 -->
                                3.14159
                            <!-- /react-text -->

                            <!-- react-text: 14 -->
                                another basic string
                            <!-- /react-text -->
                        </div>

                        <div id="p.c.5.p.c.2">
                            <div id="p.c.5.p.c.2.p.c.0">
                                <div id="p.c.5.p.c.2.p.c.0.p.c">
                                    <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0">

                                        <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0">
                                        </div>

                                        <!-- react-text: 20 -->
                                        <!-- /react-text -->

                                        <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2">
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
                <!-- react-empty: 3 -->
            </div>
        '''
        self.assertEqual(
            el.get_attribute('innerHTML'),
            rendered_dom.replace('\n', '').replace('    ', '')
        )

        # Check that no errors or warnings were displayed
        self.assertEqual(
            self.driver.execute_script(
                'return window.tests.console.error.length'
            ),
            0
        )
        self.assertEqual(
            self.driver.execute_script(
                'return window.tests.console.warn.length'
            ),
            0
        )

        # Check the initial stores

        # layout should just be the JSON-ified app.layout
        self.assertEqual(
            self.driver.execute_script(
                'return JSON.parse(JSON.stringify('
                'window.store.getState().layout'
                '))'
            ),
            {
                "namespace": "dash_html_components",
                "props": {
                  "content": [
                    "Basic string",
                    3.14,
                    None,
                    {
                      "namespace": "dash_html_components",
                      "props": {
                        "content": "Child div with basic string",
                        "id": "p.c.3",
                         'className': "my-class",
                         'title': 'tooltip',
                         'style': {
                            'color': 'red', 'fontSize': 30, 'font-size': 10
                         }
                      },
                      "type": "Div"
                    },
                    {
                      "namespace": "dash_html_components",
                      "props": {
                        "content": None,
                        "id": "p.c.4"
                      },
                      "type": "Div"
                    },
                    {
                      "namespace": "dash_html_components",
                      "props": {
                        "content": [
                          {
                            "namespace": "dash_html_components",
                            "props": {
                              "content": "Grandchild div",
                              "id": "p.c.5.p.c.0"
                            },
                            "type": "Div"
                          },
                          {
                            "namespace": "dash_html_components",
                            "props": {
                              "content": [
                                {
                                  "namespace": "dash_html_components",
                                  "props": {
                                    "content": "Great grandchild",
                                    "id": "p.c.5.p.c.1.p.c.0"
                                  },
                                  "type": "Div"
                                },
                                3.14159,
                                "another basic string"
                              ],
                              "id": "p.c.5.p.c.1"
                            },
                            "type": "Div"
                          },
                          {
                            "namespace": "dash_html_components",
                            "props": {
                              "content": [
                                {
                                  "namespace": "dash_html_components",
                                  "props": {
                                    "content": {
                                      "namespace": "dash_html_components",
                                      "props": {
                                        "content": [
                                          {
                                            "namespace": "dash_html_components",
                                            "props": {
                                              "content": [
                                                {
                                                  "namespace": "dash_html_components",
                                                  "props": {
                                                    "content": None,
                                                    "id": "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0"
                                                  },
                                                  "type": "Div"
                                                },
                                                "",
                                                {
                                                  "namespace": "dash_html_components",
                                                  "props": {
                                                    "content": None,
                                                    "id": "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2"
                                                  },
                                                  "type": "Div"
                                                }
                                              ],
                                              "id": "p.c.5.p.c.2.p.c.0.p.c.p.c.0"
                                            },
                                            "type": "Div"
                                          }
                                        ],
                                        "id": "p.c.5.p.c.2.p.c.0.p.c"
                                      },
                                      "type": "Div"
                                    },
                                    "id": "p.c.5.p.c.2.p.c.0"
                                  },
                                  "type": "Div"
                                }
                              ],
                              "id": "p.c.5.p.c.2"
                            },
                            "type": "Div"
                          }
                        ],
                        "id": "p.c.5"
                      },
                      "type": "Div"
                    }
                  ]
                },
                "type": "Div"
            }
        )

        # graphs should just be empty since there are no dependencies
        self.assertEqual(
            self.driver.execute_script(
                'return JSON.parse(JSON.stringify('
                'window.store.getState().graphs'
                '))'
            ),
            {
              "InputGraph": {
                "nodes": {},
                "outgoingEdges": {},
                "incomingEdges": {}
              },
              "EventGraph": {
                "nodes": {},
                "outgoingEdges": {},
                "incomingEdges": {}
              }
            }
        )

        # paths is just a lookup table of the components's IDs and their
        # placement in the tree.
        # in this case the IDs are just abbreviations of the path to make
        # things easy to verify.
        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().paths'
            ),
            {
                "p.c.3": [
                    "props",  "content",  3
                ],
                "p.c.4": [
                    "props",  "content",  4
                ],
                "p.c.5": [
                    "props",  "content",  5
                ],
                "p.c.5.p.c.0": [
                    "props",  "content",  5,
                    "props",  "content",  0
                ],
                "p.c.5.p.c.1": [
                    "props",  "content",  5,
                    "props",  "content",  1
                ],
                "p.c.5.p.c.1.p.c.0": [
                    "props",  "content",  5,
                    "props",  "content",  1,
                    "props",  "content",  0
                ],
                "p.c.5.p.c.2": [
                    "props",  "content",  5,
                    "props",  "content",  2
                ],
                "p.c.5.p.c.2.p.c.0": [
                    "props",  "content",  5,
                    "props",  "content",  2,
                    "props",  "content",  0
                ],
                "p.c.5.p.c.2.p.c.0.p.c": [
                    "props",  "content",  5,
                    "props",  "content",  2,
                    "props",  "content",  0,
                    "props",  "content"
                ],
                "p.c.5.p.c.2.p.c.0.p.c.p.c.0": [
                    "props",  "content",  5,
                    "props",  "content",  2,
                    "props",  "content",  0,
                    "props",  "content",
                    "props",  "content",  0
                ],
                "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0": [
                    "props",  "content",  5,
                    "props",  "content",  2,
                    "props",  "content",  0,
                    "props",  "content",
                    "props",  "content",  0,
                    "props",  "content",  0
                ],
                "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2": [
                    "props",  "content",  5,
                    "props",  "content",  2,
                    "props",  "content",  0,
                    "props",  "content",
                    "props",  "content",  0,
                    "props",  "content",  2
                ]
            }
        )

        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().requestQueue'
            ),
            []
        )

        # Take a screenshot with percy
        # self.percy_runner.snapshot(name='dcc')

        assert_clean_console(self)

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

        @app.callback(Output('output-1', 'content'), [Input('input', 'value')])
        def update_output(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        wait_for(lambda: self.driver.find_element_by_id(
            'output-1'
        ).text == 'initial value')

        input1 = self.driver.find_element_by_id('input')
        input1.clear()

        input1.send_keys('hello world')

        wait_for(lambda: self.driver.find_element_by_id(
            'output-1'
        ).text == 'hello world')

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            1 +
            # one for each hello world character
            len('hello world')
        )

        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().requestQueue'
            ),
            []
        )

        assert_clean_console(self)

    def test_callbacks_generating_content(self):
        """ Modify the DOM tree by adding new
        components in the callbacks
        """

        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(
                id='input',
                value='initial value'
            ),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'content'), [Input('input', 'value')])
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
            Output('sub-output-1', 'content'),
            [Input('sub-input-1', 'value')]
        )
        def update_input(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        output = self.driver.find_element_by_id('output')
        output_html = output.get_attribute('innerHTML')

        wait_for(lambda: call_count.value == 1)

        # Adding new content to the layout should
        # call the callbacks immediately to set
        # the correct initial state
        wait_for(
            lambda: (
                self.driver.find_element_by_id('output')
                .get_attribute('innerHTML') == '''
                <div>
                    <input id="sub-input-1" value="sub input initial value">
                    <div id="sub-output-1">
                        sub input initial value
                    </div>
                </div>'''.replace('\n', '').replace('  ', '')
            )
        )

        # the paths should include these new output IDs
        self.assertEqual(
            self.driver.execute_script('return window.store.getState().paths'),
            {
                u'input': [
                    u'props', u'content', 0
                ],
                u'output': [u'props', u'content', 1],
                u'sub-input-1': [
                    u'props', u'content', 1,
                    u'props', u'content',
                    u'props', u'content', 0
                ],
                u'sub-output-1': [
                    u'props', u'content', 1,
                    u'props', u'content',
                    u'props', u'content', 1
                ]
            }
        )

        # editing the input should modify the sub output
        sub_input = self.driver.find_element_by_id('sub-input-1')
        sub_input.send_keys('a')
        wait_for(
            lambda: (
                self.driver.find_element_by_id('sub-output-1').text
            ) == 'sub input initial valuea'
        )

        self.assertEqual(call_count.value, 2)

        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().requestQueue'
            ),
            []
        )

        assert_clean_console(self)

    def test_radio_buttons_callbacks_generating_content(self):
        self.maxDiff = 100 * 1000
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.RadioItems(
                options=[
                    {'label': 'Chapter 1', 'value': 'chapter1'},
                    {'label': 'Chapter 2', 'value': 'chapter2'},
                    {'label': 'Chapter 3', 'value': 'chapter3'},
                    {'label': 'Chapter 4', 'value': 'chapter4'}
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
            'chapter4': 'Just a string'
        }

        call_counts = {
            'body': Value('i', 0),
            'chapter1-graph': Value('i', 0),
            'chapter1-label': Value('i', 0),
            'chapter2-graph': Value('i', 0),
            'chapter2-label': Value('i', 0),
            'chapter3-graph': Value('i', 0),
            'chapter3-label': Value('i', 0)
        }

        @app.callback(Output('body', 'content'), [Input('toc', 'value')])
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
                Output('{}-label'.format(chapter), 'content'),
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
            wait_for(
                lambda: (
                    self.driver.find_element_by_id(
                        '{}-label'.format(chapter)
                    ).text
                    == value
                )
            )
            wait_for(
                lambda: (
                    self.driver.execute_script(
                        'return document.'
                        'getElementById("{}-graph").'.format(chapter) +
                        'layout.title'
                    ) == value
                )
            )

            self.assertEqual(
                self.driver.execute_script(
                    'return window.store.getState().requestQueue'
                ),
                []
            )

        def chapter1_assertions():
            paths = self.driver.execute_script(
                'return window.store.getState().paths'
            )
            self.assertEqual(paths, {
                'toc': ['props', 'content', 0],
                'body': ['props', 'content', 1],
                'chapter1-header': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 0
                ],
                'chapter1-controls': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 1
                ],
                'chapter1-label': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 2
                ],
                'chapter1-graph': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 3
                ]
            })
            generic_chapter_assertions('chapter1')

        chapter1_assertions()

        # switch chapters
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[1]).click()

        # sleep just to make sure that no calls happen after our check
        time.sleep(2)
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
                'toc': ['props', 'content', 0],
                'body': ['props', 'content', 1],
                'chapter2-header': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 0
                ],
                'chapter2-controls': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 1
                ],
                'chapter2-label': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 2
                ],
                'chapter2-graph': [
                    'props', 'content', 1,
                    'props', 'content',
                    'props', 'content', 3
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
                'toc': ['props', 'content', 0],
                'body': ['props', 'content', 1],
                'chapter3-header': [
                    'props', 'content', 1,
                    'props', 'content', 0,
                    'props', 'content',
                    'props', 'content', 0
                ],
                'chapter3-label': [
                    'props', 'content', 1,
                    'props', 'content', 0,
                    'props', 'content',
                    'props', 'content', 1
                ],
                'chapter3-graph': [
                    'props', 'content', 1,
                    'props', 'content', 0,
                    'props', 'content',
                    'props', 'content', 2
                ],
                'chapter3-controls': [
                    'props', 'content', 1,
                    'props', 'content', 0,
                    'props', 'content',
                    'props', 'content', 3
                ]
            })
            generic_chapter_assertions('chapter3')

        chapter3_assertions()

        # switch to 4
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[3]).click()
        wait_for(lambda: (
            self.driver.find_element_by_id('body').text ==
            'Just a string'
        ))
        # each element should exist in the dom
        paths = self.driver.execute_script(
            'return window.store.getState().paths'
        )
        for key in paths:
            self.driver.find_element_by_id(key)
        self.assertEqual(paths, {
            'toc': ['props', 'content', 0],
            'body': ['props', 'content', 1]
        })

        # switch back to 1
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[0]).click()
        time.sleep(0.5)
        chapter1_assertions()

    def test_dependencies_on_components_that_dont_exist(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dcc.Input(id='input', value='initial value'),
            html.Div(id='output-1')
        ])

        # standard callback
        output_1_call_count = Value('i', 0)

        @app.callback(Output('output-1', 'content'), [Input('input', 'value')])
        def update_output(value):
            output_1_call_count.value += 1
            return value

        # callback for component that doesn't yet exist in the dom
        # in practice, it might get added by some other callback
        app.config.supress_callback_exceptions = True
        output_2_call_count = Value('i', 0)

        @app.callback(
            Output('output-2', 'content'),
            [Input('input', 'value')]
        )
        def update_output_2(value):
            output_2_call_count.value += 1
            return value

        self.startServer(app)

        wait_for(lambda: self.driver.find_element_by_id('output-1').text
                 == 'initial value')
        time.sleep(1.0)
        self.assertEqual(output_1_call_count.value, 1)
        self.assertEqual(output_2_call_count.value, 0)

        input = self.driver.find_element_by_id('input')

        input.send_keys('a')
        wait_for(lambda: self.driver.find_element_by_id('output-1').text
                 == 'initial valuea')
        time.sleep(1.0)
        self.assertEqual(output_1_call_count.value, 2)
        self.assertEqual(output_2_call_count.value, 0)

        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().requestQueue'
            ),
            []
        )

        assert_clean_console(self)

    def test_events(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button('Click Me', id='button'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'content'),
                      events=[Event('button', 'click')])
        def update_output():
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

    def test_events_and_state(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button('Click Me', id='button'),
            dcc.Input(value='Initial State', id='state'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'content'),
                      state=[State('state', 'value')],
                      events=[Event('button', 'click')])
        def update_output(value):
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

    def test_events_state_and_inputs(self):
        app = Dash(__name__)
        app.layout = html.Div([
            html.Button('Click Me', id='button'),
            dcc.Input(value='Initial Input', id='input'),
            dcc.Input(value='Initial State', id='state'),
            html.Div(id='output')
        ])

        call_count = Value('i', 0)

        @app.callback(Output('output', 'content'),
                      inputs=[Input('input', 'value')],
                      state=[State('state', 'value')],
                      events=[Event('button', 'click')])
        def update_output(input, state):
            call_count.value += 1
            return 'input="{}", state="{}"'.format(input, state)

        self.startServer(app)
        btn = lambda: self.driver.find_element_by_id('button')
        output = lambda: self.driver.find_element_by_id('output')
        input = lambda: self.driver.find_element_by_id('input')
        state = lambda: self.driver.find_element_by_id('state')

        # callback gets called with initial input
        self.assertEqual(call_count.value, 1)
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

        @app.callback(Output('output', 'content'),
                      inputs=[Input('input', 'value')],
                      state=[State('state', 'value')])
        def update_output(input, state):
            call_count.value += 1
            return 'input="{}", state="{}"'.format(input, state)

        self.startServer(app)
        output = lambda: self.driver.find_element_by_id('output')
        input = lambda: self.driver.find_element_by_id('input')
        state = lambda: self.driver.find_element_by_id('state')

        # callback gets called with initial input
        self.assertEqual(call_count.value, 1)
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

    def test_chained_dependencies(self):
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

        @app.callback(Output('output', 'content'), [
            Input('input-1', 'value'),
            Input('input-2', 'value')
        ])
        def update_output(input1, input2):
            call_counts['output'].value += 1
            return '{} + {}'.format(input1, input2)

        self.startServer(app)

        wait_for(lambda: call_counts['output'].value == 1)
        wait_for(lambda: call_counts['input-2'].value == 1)
        self.assertEqual(input1().get_attribute('value'), u'input 1')
        self.assertEqual(input2().get_attribute('value'), u'<<input 1>>')
        self.assertEqual(output().text, 'input 1 + <<input 1>>')

        input1().send_keys('x')
        wait_for(lambda: call_counts['output'].value == 2)
        wait_for(lambda: call_counts['input-2'].value == 2)
        self.assertEqual(input1().get_attribute('value'), u'input 1x')
        self.assertEqual(input2().get_attribute('value'), u'<<input 1x>>')
        self.assertEqual(output().text, 'input 1x + <<input 1x>>')

        input2().send_keys('y')
        wait_for(lambda: call_counts['output'].value == 3)
        wait_for(lambda: call_counts['input-2'].value == 2)
        self.assertEqual(input1().get_attribute('value'), u'input 1x')
        self.assertEqual(input2().get_attribute('value'), u'<<input 1x>>y')
        self.assertEqual(output().text, 'input 1x + <<input 1x>>y')

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

        @app.callback(Output('body', 'content'), [Input('toc', 'value')])
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
            Output('button-output', 'content'),
            events=[Event('button', 'click')])
        def this_callback_takes_forever():
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
            self.assertEqual(
                self.driver.execute_script(
                    'return JSON.parse(JSON.stringify('
                    'window.store.getState().layout'
                    '))'
                ),
                {
                    "namespace": "dash_html_components",
                    "type": "Div",
                    "props": {
                        "content": [
                            {
                                "namespace": "dash_core_components",
                                "type": "RadioItems",
                                "props": {
                                    "value": "2",
                                    "options": app.layout['toc'].options,
                                    "id": app.layout['toc'].id,
                                }
                            },
                            {
                                "namespace": "dash_html_components",
                                "type": "Div",
                                "props": {
                                    "id": "body",
                                    "content": "Chapter 2"
                                }
                            }
                        ]
                    }
                }
            )
            self.assertEqual(
                self.driver.execute_script(
                    'return JSON.parse(JSON.stringify('
                    'window.store.getState().paths'
                    '))'
                ),
                {
                    "toc": ["props", "content", 0],
                    "body": ["props", "content", 1]
                }
            )
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[1]).click()
        chapter2_assertions()
        time.sleep(5)
        wait_for(lambda: call_counts['button-output'].value == 1)
        time.sleep(2)  # liberally wait for the front-end to process request
        chapter2_assertions()
        assert_clean_console(self)
