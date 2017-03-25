from dash import Dash
from dash.dependencies import Input, Output, State, Event
import dash
import dash_html_components as html
import dash_core_components
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
                                html.Div(id='p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0'),
                                '',
                                html.Div(id='p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2')
                            ], id='p.c.5.p.c.2.p.c.0.p.c.p.c.0')
                        ], id='p.c.5.p.c.2.p.c.0.p.c'),
                        id='p.c.5.p.c.2.p.c.0'
                    )
                ], id='p.c.5.p.c.2')
            ], id='p.c.5')
        ])

        self.startServer(app)

        el = self.driver.find_element_by_id('react-entry-point')

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
        # self.percy_runner.snapshot(name='dash_core_components')

        assert_clean_console(self)

    def test_simple_callback(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dash_core_components.Input(
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
            dash_core_components.Input(
                id='input',
                value='initial value'
            ),
            html.Div(id='output')
        ])

        @app.callback(Output('output', 'content'), [Input('input', 'value')])
        def pad_output(input):
            return html.Div([
                dash_core_components.Input(
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
        app = Dash(__name__)
        app.layout = html.Div([
            dash_core_components.RadioItems(
                options=[
                    {'label': 'Chapter 1', 'value': 'chapter1'},
                    {'label': 'Chapter 2', 'value': 'chapter2'},
                    {'label': 'Chapter 3', 'value': 'chapter3'}
                ],
                value='chapter1',
                id='toc'
            ),
            html.Div(id='body')
        ])
        for script in dash_core_components._js_dist:
            app.scripts.append_script(script)

        chapters = {
            'chapter1': html.Div([
                html.H1('Chapter 1', id='chapter1-header'),
                dash_core_components.Dropdown(
                    options=[{'label': i, 'value': i} for i in ['NYC', 'MTL', 'SF']],
                    value='NYC',
                    id='chapter1-controls'
                ),
                html.Label(id='chapter1-label'),
                dash_core_components.Graph(id='chapter1-graph')
            ]),
            # Chapter 2 has the some of the same components in the same order
            # as Chapter 1. This means that they won't get remounted
            # unless they set their own keys are differently.
            # Switching back and forth between 1 and 2 implicitly
            # tests how components update when they aren't remounted.
            'chapter2': html.Div([
                html.H1('Chapter 2', id='chapter2-header'),
                dash_core_components.RadioItems(
                    options=[{'label': i, 'value': i}
                             for i in ['USA', 'Canada']],
                    value='USA',
                    id='chapter2-controls'
                ),
                html.Label(id='chapter2-label'),
                dash_core_components.Graph(id='chapter2-graph')
            ]),
            # Chapter 3 has a different layout and so the components
            # should get rewritten
            'chapter3': [html.Div(
                html.Div([
                    html.H3('Chapter 3', id='chapter3-header'),
                    html.Label(id='chapter3-label'),
                    dash_core_components.Graph(id='chapter3-graph'),
                    dash_core_components.RadioItems(
                        options=[{'label': i, 'value': i}
                                 for i in ['Summer', 'Winter']],
                        value='Winter',
                        id='chapter3-controls'
                    )
                ])
            )]
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
        # import ipdb; ipdb.set_trace()
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

        # switch back to 1
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[0]).click()
        chapter1_assertions()

        ## HEY!!! WELCOME BACK!!
        # TODO - ADD A CHAPTER THAT IS JUST A STRING!

    def test_dependencies_on_components_that_dont_exist(self):
        app = Dash(__name__)
        app.layout = html.Div([
            dash_core_components.Input(id='input', value='initial value'),
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
