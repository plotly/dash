import unittest
import json
import pkgutil
import plotly
import dash_core_components as dcc
from dash_html_components import Div
import dash_renderer
import dash

from dash.dependencies import Event, Input, Output, State
from dash import exceptions


def generate_css(css_links):
    return '\n'.join([
        '<link rel="stylesheet" href="{}">'.format(l)
        for l in css_links
    ])


def generate_js(js_links):
    return '\n'.join([
        '<script src="{}"></script>'.format(l)
        for l in js_links
    ])


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = dash.Dash('my-app')
        self.app.layout = Div([
            Div('Hello World', id='header', style={'color': 'red'}),
            dcc.Input(id='id1', placeholder='Type a value'),
            dcc.Input(id='id2', placeholder='Type a value')
        ])

        self.client = self.app.server.test_client()

        self.maxDiff = 100*1000

    @unittest.skip('')
    def test_route_list(self):
        urls = [rule.rule for rule in self.app.server.url_map.iter_rules()]

        self.assertEqual(
            sorted(urls),
            sorted([
                '/interceptor',
                '/initialize',
                '/dependencies',
                '/',
                '/component-suites/<path:path>',
                '/static/<path:filename>'
            ])
        )

    @unittest.skip('')
    def test_initialize_route(self):
        response = self.client.get('/initialize')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data),
            json.loads(
                json.dumps(self.app.layout, cls=plotly.utils.PlotlyJSONEncoder)
            )
        )

    @unittest.skip('')
    def test_dependencies_route(self):
        self.app.callback('header', ['id1'])
        response = self.client.get('/dependencies')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data), {
                'header': {
                    'state': [{'id': 'id1'}],
                    'events': [{'id': 'id1'}]
                }
            }
        )

        self.app.callback(
            'header',
            state=[{'id': 'id1'}],
            events=[{'id': 'id1'}])
        response = self.client.get('/dependencies')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data), {
                'header': {
                    'state': [{'id': 'id1'}],
                    'events': [{'id': 'id1'}]
                }
            }
        )

        state = [
            {'id': 'id1', 'prop': 'value'},

            # Multiple properties from a single component
            {'id': 'id1', 'prop': 'className'},

            # Nested state
            {'id': 'id1', 'prop': ['style', 'color']}
        ]
        events = [
            {'id': 'id1', 'event': 'click'},
            {'id': 'id1', 'event': 'submit'}
        ]
        self.app.callback('header', state=state, events=events)
        response = self.client.get('/dependencies')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data), {
                'header': {
                    'state': state,
                    'events': events
                }
            }
        )

    @unittest.skip('')
    def test_index_html(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @unittest.skip('')
    def test_single_observer_returning_a_dict(self):
        @self.app.callback('header', ['id1'])
        def update_header(input1):
            self.assertEqual({'value': 'New Value'}, input1)
            new_value = input1['value']
            return {
                'children': new_value,
                'style.color': 'red',
                'className': 'active',
                'width': None
            }

        response = self.client.post(
            '/interceptor',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                # TODO - Why not just `target: id`?
                'target': {
                    'props': {
                        'id': 'header'
                    }
                },
                'parents': {
                    'id1': {
                        'props': {
                            'value': 'New Value'
                        }
                    }
                }
            })
        )

        self.assertEqual(
            json.loads(response.data),
            {
                'response': {
                    'children': 'New Value',
                    'props': {
                        'id': 'header',
                        'style.color': 'red',
                        'className': 'active',
                        'width': None
                    }
                }
            }
        )

    @unittest.skip('')
    def test_single_observer_returning_a_component(self):
        @self.app.callback('header', ['id1'])
        def update_header(input1):
            self.assertEqual({'value': 'New Value'}, input1)
            return {
                'children': Div('New Component')
            }

        response = self.client.post(
            '/interceptor',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'target': {
                    'props': {
                        'id': 'header'
                    }
                },
                'parents': {
                    'id1': {
                        'props': {
                            'value': 'New Value'
                        }
                    }
                }
            })
        )

        self.assertEqual(
            json.loads(response.data),
            {
                'response': {
                    'props': {
                        'id': 'header'
                    },
                    'children': {
                        'type': 'Div',
                        'namespace': 'html_components',
                        'props': {
                            'children': 'New Component'
                        }
                    }
                }
            }
        )

    @unittest.skip('')
    def test_single_observer_updating_component_that_doesnt_exist(self):
        # It's possible to register callbacks for components that don't
        # exist in the initial layout because users could add them as
        # children in response to another callback
        @self.app.callback('doesnt-exist-yet', ['id1'])
        def update_header(input1):
            self.assertEqual({
                'value': 'New Value'
            }, input1)

            new_value = input1['value']
            return {
                'value': new_value
            }

        response = self.client.post(
            '/interceptor',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'target': {
                    'props': {
                        'id': 'header'
                    }
                },
                'parents': {
                    'id1': {
                        'props': {
                            'value': 'New Value'
                        }
                    }
                }
            })
        )

        self.assertEqual(
            json.loads(response.data),
            {
                'response': {
                    'props': {
                        'id': 'doesnt-exit-yet',
                        'value': 'New Value'
                    },
                }
            }
        )

    @unittest.skip('')
    def test_single_observer_with_multiple_controllers(self):
        @self.app.callback('header', ['id1', 'id2'])
        def update_header(input1, input2):
            self.assertEqual({
                'value': 'New Value'
            }, input1)
            self.assertEqual({}, input2)

            new_value = input1['value']
            return {
                'value': new_value
            }

        response = self.client.post(
            '/interceptor',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'target': {
                    'props': {
                        'id': 'header'
                    }
                },
                'parents': {
                    'id1': {
                        'props': {
                            'value': 'New Value'
                        }
                    },
                    'id2': {
                        'props': {}
                    }
                }
            })
        )

        self.assertEqual(
            json.loads(response.data),
            {
                'response': {
                    'props': {
                        'id': 'header',
                        'value': 'New Value'
                    },
                }
            }
        )

    def test_serving_scripts(self):
        self.app.scripts.config.serve_locally = True
        self.app._setup_server()
        response = self.client.get(
            ('/_dash-component-suites/'
             'dash_renderer/bundle.js?v={}').format(dash_renderer.__version__)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            pkgutil.get_data('dash_renderer', 'bundle.js')
        )


class TestCallbacks(unittest.TestCase):
    def test_callback_registry(self):
        app = dash.Dash('')
        input = dcc.Input(id='input')
        input._events = ['blur', 'change']

        app.layout = Div([
            input,
            Div(id='output-1'),
            Div(id='output-2'),
            Div(id='output-3')
        ], id='body')

        app.callback(
            Output('body', 'children'),
            [Input('input', 'value')]
        )
        app.callback(
            Output('output-1', 'children'),
            [Input('input', 'value')]
        )
        app.callback(
            Output('output-2', 'children'),
            [Input('input', 'value')],
            state=[State('input', 'value')],
        )
        app.callback(
            Output('output-3', 'children'),
            [Input('input', 'value')],
            state=[State('input', 'value')],
            events=[Event('input', 'blur')],
        )

    def test_no_layout_exception(self):
        app = dash.Dash('')
        self.assertRaises(
            exceptions.LayoutIsNotDefined,
            app.callback,
            Output('body', 'children'),
            [Input('input', 'value')]
        )

    def test_exception_id_not_in_layout(self):
        app = dash.Dash('')
        app.layout = Div('', id='test')
        self.assertRaises(
            exceptions.NonExistantIdException,
            app.callback,
            Output('output', 'children'),
            [Input('input', 'value')]
        )

    def test_exception_prop_not_in_component(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input'),
            Div(id='output')
        ], id='body')

        self.assertRaises(
            exceptions.NonExistantPropException,
            app.callback,
            Output('output', 'non-there'),
            [Input('input', 'value')]
        )

        self.assertRaises(
            exceptions.NonExistantPropException,
            app.callback,
            Output('output', 'children'),
            [Input('input', 'valuez')]
        )

        self.assertRaises(
            exceptions.NonExistantPropException,
            app.callback,
            Output('body', 'childrenz'),
            [Input('input', 'value')]
        )

    def test_exception_event_not_in_component(self):
        app = dash.Dash('')
        app.layout = Div([
            Div(id='button'),
            Div(id='output'),
            Div(id='graph-output'),
            dcc.Graph(id='graph')
        ], id='body')

        for id in ['output', 'body']:
            self.assertRaises(
                exceptions.NonExistantEventException,
                app.callback,
                Output(id, 'children'),
                events=[Event(id, 'style')]
            )
            app.callback(
                Output(id, 'children'),
                events=[Event(id, 'click')]
            )

        self.assertRaises(
            exceptions.NonExistantEventException,
            app.callback,
            Output('output', 'children'),
            events=[Event('graph', 'zoom')]
        )
        app.callback(
            Output('graph-output', 'children'),
            events=[Event('graph', 'click')]
        )

    def test_exception_component_is_not_right_type(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input'),
            Div(id='output')
        ], id='body')

        test_args = [
            ['asdf', ['asdf'], [], []],
            [Output('output', 'children'), Input('input', 'value'), [], []],
            [Output('output', 'children'), [], State('input', 'value'), []],
            [Output('output', 'children'), [], [], Event('input', 'click')],
        ]
        for args in test_args:
            self.assertRaises(
                exceptions.IncorrectTypeException,
                app.callback,
                *args
            )

    def test_suppress_callback_exception(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input'),
            Div(id='output')
        ], id='body')
        self.assertRaises(
            exceptions.NonExistantIdException,
            app.callback,
            Output('id-not-there', 'children'),
            [Input('input', 'value')]
        )
        app.config.supress_callback_exceptions = True
        app.callback(Output('id-not-there', 'children'),
                     [Input('input', 'value')])

    def test_missing_input_and_events(self):
        app = dash.Dash('')
        app.layout = Div([
            dcc.Input(id='input')
        ], id='body')
        self.assertRaises(
            exceptions.MissingEventsException,
            app.callback,
            Output('body', 'children'),
            [],
            [State('input', 'value')]
        )
