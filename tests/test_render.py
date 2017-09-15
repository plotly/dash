from dash import Dash
from dash.dependencies import Input, Output, State, Event
import dash
import dash_html_components as html
import dash_core_components as dcc
from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console, invincible, wait_for
from multiprocessing import Value
import time
import re
import itertools
import json


class Tests(IntegrationTests):
    def setUp(self):
        def wait_for_element_by_id(id):
            wait_for(lambda: None is not invincible(
                lambda: self.driver.find_element_by_id(id)
            ))
            return self.driver.find_element_by_id(id)
        self.wait_for_element_by_id = wait_for_element_by_id

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
                     style={'color': 'red', 'fontSize': 30}
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

        el = self.wait_for_element_by_id('_dash-app-content')

        # TODO - Make less fragile with http://lxml.de/lxmlhtml.html#html-diff
        rendered_dom = '''
            <div>
                Basic string

                3.14

                <div PERMUTE>
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

                        3.14159

                        another basic string
                    </div>

                    <div id="p.c.5.p.c.2">
                        <div id="p.c.5.p.c.2.p.c.0">
                            <div id="p.c.5.p.c.2.p.c.0.p.c">
                                <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0">

                                    <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0">
                                    </div>


                                    <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2">
                                    </div>

                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        '''
        # React wraps text and numbers with e.g. <!-- react-text: 20 -->
        # Remove those
        comment_regex = '<!--[^\[](.*?)-->'

        # Somehow the html attributes are unordered.
        # Try different combinations (they're all valid html)
        style_permutations = [
            'style="color: red; font-size: 30px;"',
            'style="font-size: 30px; color: red;"'
        ]
        permutations = itertools.permutations([
            'id="p.c.3"',
            'class="my-class"',
            'title="tooltip"',
        ], 3)
        passed = False
        for permutation in permutations:
            for style in style_permutations:
                actual_cleaned = re.sub(comment_regex, '', el.get_attribute('innerHTML'))
                expected_cleaned = re.sub(
                    comment_regex,
                    '',
                    rendered_dom.replace('\n', '')
                                .replace('    ', '')
                                .replace('PERMUTE', ' '.join(list(permutation) + [style]))
                )
                passed = passed or (actual_cleaned == expected_cleaned)
        if not passed:
            raise Exception(
                'HTML does not match\nActual:\n{}\n\nExpected:\n{}'.format(
                    actual_cleaned,
                    expected_cleaned
                )
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
                  "children": [
                    "Basic string",
                    3.14,
                    None,
                    {
                      "namespace": "dash_html_components",
                      "props": {
                        "children": "Child div with basic string",
                        "id": "p.c.3",
                         'className': "my-class",
                         'title': 'tooltip',
                         'style': {
                            'color': 'red', 'fontSize': 30
                         }
                      },
                      "type": "Div"
                    },
                    {
                      "namespace": "dash_html_components",
                      "props": {
                        "children": None,
                        "id": "p.c.4"
                      },
                      "type": "Div"
                    },
                    {
                      "namespace": "dash_html_components",
                      "props": {
                        "children": [
                          {
                            "namespace": "dash_html_components",
                            "props": {
                              "children": "Grandchild div",
                              "id": "p.c.5.p.c.0"
                            },
                            "type": "Div"
                          },
                          {
                            "namespace": "dash_html_components",
                            "props": {
                              "children": [
                                {
                                  "namespace": "dash_html_components",
                                  "props": {
                                    "children": "Great grandchild",
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
                              "children": [
                                {
                                  "namespace": "dash_html_components",
                                  "props": {
                                    "children": {
                                      "namespace": "dash_html_components",
                                      "props": {
                                        "children": [
                                          {
                                            "namespace": "dash_html_components",
                                            "props": {
                                              "children": [
                                                {
                                                  "namespace": "dash_html_components",
                                                  "props": {
                                                    "children": None,
                                                    "id": "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0"
                                                  },
                                                  "type": "Div"
                                                },
                                                "",
                                                {
                                                  "namespace": "dash_html_components",
                                                  "props": {
                                                    "children": None,
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
                    "props",  "children",  3
                ],
                "p.c.4": [
                    "props",  "children",  4
                ],
                "p.c.5": [
                    "props",  "children",  5
                ],
                "p.c.5.p.c.0": [
                    "props",  "children",  5,
                    "props",  "children",  0
                ],
                "p.c.5.p.c.1": [
                    "props",  "children",  5,
                    "props",  "children",  1
                ],
                "p.c.5.p.c.1.p.c.0": [
                    "props",  "children",  5,
                    "props",  "children",  1,
                    "props",  "children",  0
                ],
                "p.c.5.p.c.2": [
                    "props",  "children",  5,
                    "props",  "children",  2
                ],
                "p.c.5.p.c.2.p.c.0": [
                    "props",  "children",  5,
                    "props",  "children",  2,
                    "props",  "children",  0
                ],
                "p.c.5.p.c.2.p.c.0.p.c": [
                    "props",  "children",  5,
                    "props",  "children",  2,
                    "props",  "children",  0,
                    "props",  "children"
                ],
                "p.c.5.p.c.2.p.c.0.p.c.p.c.0": [
                    "props",  "children",  5,
                    "props",  "children",  2,
                    "props",  "children",  0,
                    "props",  "children",
                    "props",  "children",  0
                ],
                "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0": [
                    "props",  "children",  5,
                    "props",  "children",  2,
                    "props",  "children",  0,
                    "props",  "children",
                    "props",  "children",  0,
                    "props",  "children",  0
                ],
                "p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2": [
                    "props",  "children",  5,
                    "props",  "children",  2,
                    "props",  "children",  0,
                    "props",  "children",
                    "props",  "children",  0,
                    "props",  "children",  2
                ]
            }
        )

        self.assertEqual(
            self.driver.execute_script(
                'return window.store.getState().requestQueue'
            ),
            []
        )

        self.percy_runner.snapshot(name='layout')

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

        @app.callback(Output('output-1', 'children'), [Input('input', 'value')])
        def update_output(value):
            call_count.value = call_count.value + 1
            return value

        self.startServer(app)

        output1 = self.wait_for_element_by_id('output-1')
        wait_for(lambda: output1.text == 'initial value')
        self.percy_runner.snapshot(name='simple-callback-1')

        input1 = self.wait_for_element_by_id('input')
        input1.clear()

        input1.send_keys('hello world')

        output1 = lambda: self.wait_for_element_by_id('output-1')
        wait_for(lambda: output1().text == 'hello world')
        self.percy_runner.snapshot(name='simple-callback-2')

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

    def test_callbacks_generating_children(self):
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

        output = self.driver.find_element_by_id('output')
        output_html = output.get_attribute('innerHTML')

        wait_for(lambda: call_count.value == 1)

        # Adding new children to the layout should
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
        self.percy_runner.snapshot(name='callback-generating-function-1')

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
        self.percy_runner.snapshot(name='callback-generating-function-2')

        assert_clean_console(self)

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

            # Chapter 5 contains elements that are bound with events
            'chapter5': [html.Div([
                html.Button(id='chapter5-button'),
                html.Div(id='chapter5-output')
            ])]
        }

        call_counts = {
            'body': Value('i', 0),
            'chapter1-graph': Value('i', 0),
            'chapter1-label': Value('i', 0),
            'chapter2-graph': Value('i', 0),
            'chapter2-label': Value('i', 0),
            'chapter3-graph': Value('i', 0),
            'chapter3-label': Value('i', 0),
            'chapter5-output': Value('i', 0)
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

        chapter5_output_children = 'Button clicked'

        @app.callback(Output('chapter5-output', 'children'),
                      events=[Event('chapter5-button', 'click')])
        def display_output():
            call_counts['chapter5-output'].value += 1
            return chapter5_output_children

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
        self.percy_runner.snapshot(name='chapter-1')

        # switch chapters
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[1]).click()

        # sleep just to make sure that no calls happen after our check
        time.sleep(2)
        self.percy_runner.snapshot(name='chapter-2')
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
        self.percy_runner.snapshot(name='chapter-3')
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
        wait_for(lambda: (
            self.driver.find_element_by_id('body').text ==
            'Just a string'
        ))
        self.percy_runner.snapshot(name='chapter-4')

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
        self.percy_runner.snapshot(name='chapter-1-again')

        # switch to 5
        (self.driver.find_elements_by_css_selector(
            'input[type="radio"]'
        )[4]).click()
        time.sleep(1)
        # click on the button and check the output div before and after
        chapter5_div = lambda: self.driver.find_element_by_id(
            'chapter5-output'
        )
        chapter5_button = lambda: self.driver.find_element_by_id(
            'chapter5-button'
        )
        self.assertEqual(chapter5_div().text, '')
        chapter5_button().click()
        wait_for(lambda: chapter5_div().text == chapter5_output_children)
        time.sleep(0.5)
        self.percy_runner.snapshot(name='chapter-5')
        self.assertEqual(call_counts['chapter5-output'].value, 1)

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

        el = self.wait_for_element_by_id('output-1')
        wait_for(lambda: el.text == 'initial value')
        self.percy_runner.snapshot(name='dependencies')
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

        @app.callback(Output('output', 'children'),
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

        @app.callback(Output('output', 'children'),
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

        @app.callback(Output('output', 'children'),
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

        @app.callback(Output('output', 'children'),
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

    def test_event_creating_inputs(self):
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
            events=[Event(ids['button'], 'click')])
        def display():
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
                        "children": [
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
                                    "children": "Chapter 2"
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
                    "toc": ["props", "children", 0],
                    "body": ["props", "children", 1]
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

        self.percy_runner.snapshot(name='layout')

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
            print('display_output ' + str(n_clicks))
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

        self.wait_for_element_by_id('display-content').click()

        time.sleep(5)

        self.percy_runner.snapshot(name='layout')

        self.assertEqual(call_count.value, 1)
