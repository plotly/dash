from dash.react import Dash
import dash
import dash_html_components as html
import dash_core_components
from IntegrationTests import IntegrationTests
import mock
from utils import wait_for
from multiprocessing import Value


class Tests(IntegrationTests):

    def test_initial_state(s):
        dash = Dash(__name__)
        dash.layout = html.Div([
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

        s.startServer(dash)

        el = s.driver.find_element_by_id('react-entry-point')

        rendered_dom = '''
        <div data-reactroot="">
            <!-- react-text: 3 -->
            Basic string
            <!-- /react-text -->

            <!-- react-text: 4 -->
            3.14
            <!-- /react-text -->

            <div class="my-class" id="p.c.3" title="tooltip" style="color: red; font-size: 30px;">
                Child div with basic string
            </div>
            <div id="p.c.4"></div>
            <div id="p.c.5">
                <div id="p.c.5.p.c.0">
                    Grandchild div
                </div>
                <div id="p.c.5.p.c.1">
                    <div id="p.c.5.p.c.1.p.c.0">
                        Great grandchild
                    </div>

                    <!-- react-text: 11 -->
                        3.14159
                    <!-- /react-text -->

                    <!-- react-text: 12 -->
                        another basic string
                    <!-- /react-text -->
                </div>
                <div id="p.c.5.p.c.2">
                    <div id="p.c.5.p.c.2.p.c.0">
                        <div id="p.c.5.p.c.2.p.c.0.p.c">
                            <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0">
                                <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.0">
                                </div>
                                <!-- react-text: 18 -->
                                <!-- /react-text -->
                                <div id="p.c.5.p.c.2.p.c.0.p.c.p.c.0.p.c.2">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        s.assertEqual(
            el.get_attribute('innerHTML'),
            rendered_dom.replace('\n', '').replace('    ', '')
        )

        # Check that no errors or warnings were displayed
        s.assertEqual(
            s.driver.execute_script(
                'return window.tests.console.error.length'
            ),
            0
        )
        s.assertEqual(
            s.driver.execute_script(
                'return window.tests.console.warn.length'
            ),
            0
        )

        # Check the initial stores

        # layout should just be the JSON-ified app.layout
        s.assertEqual(
            s.driver.execute_script(
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
        s.assertEqual(
            s.driver.execute_script(
                'return JSON.parse(JSON.stringify('
                'window.store.getState().graphs'
                '))'
            ),
            {
              "StateGraph": {
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
        s.assertEqual(
            s.driver.execute_script(
                'return JSON.parse(JSON.stringify('
                'window.store.getState().paths'
                '))'
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

        # Take a screenshot with percy
        # s.percy_runner.snapshot(name='dash_core_components')

    def test_simple_callback(s):
        dash = Dash(__name__)
        dash.layout = html.Div([
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

        @dash.react('output-1', ['input'])
        def update_output(input):
            call_count.value = call_count.value + 1
            return {'content': input['value']}

        s.startServer(dash)

        wait_for(lambda: s.driver.find_element_by_id(
            'output-1'
        ).text == 'initial value')

        input1 = s.driver.find_element_by_id('input')
        input1.clear()

        input1.send_keys('hello world')

        wait_for(lambda: s.driver.find_element_by_id(
            'output-1'
        ).text == 'hello world')

        s.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            1 +
            # one for each hello world character
            len('hello world')
        )

    def test_callbacks_generating_content(s):
        """ Modify the DOM tree by adding new
        components in the callbacks
        """

        dash = Dash(__name__)
        dash.layout = html.Div([
            dash_core_components.Input(
                id='input',
                value='initial value'
            ),
            html.Div(id='output')
        ])

        @dash.react('output', ['input'])
        def pad_output(input):
            return {
                'content': html.Div([
                    dash_core_components.Input(
                        id='sub-input-1',
                        value='sub input initial value'
                    ),
                    html.Div(id='sub-output-1')
                ])
            }

        call_count = Value('i', 0)

        # these components don't exist in the initial render
        @dash.react('sub-output-1', ['sub-input-1'])
        def update_input(input):
            call_count.value = call_count.value + 1
            return {
                'content': input['value']
            }

        s.startServer(dash)

        output = s.driver.find_element_by_id('output')
        output_html = output.get_attribute('innerHTML')

        wait_for(lambda: call_count.value == 1)

        # Adding new content to the layout should
        # call the callbacks immediately to set
        # the correct initial state
        wait_for(
            lambda *args: (
                s.driver.find_element_by_id('output')
                 .get_attribute('innerHTML')) ==
            '''
            <div>
                <input type="text/javascript" id="sub-input-1" value="sub input initial value">
                <div id="sub-output-1">sub input inital value</div>
            </div>'''.replace('\n', '').replace('    ', '')
        )

        # editing the input should modify the sub output
        sub_input = s.driver.find_element_by_id('sub-input-1')
        sub_input.send_keys('a')
        wait_for(
            lambda *args: (
                s.driver.find_element_by_id
                 .get_attribute('innerHTML')
            ) == 'a'
        )

        s.assertEqual(call_count.value, 1)
