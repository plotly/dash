import unittest
from dash.development.base_component import generate_class
import dash
import json
import plotly

Div = generate_class(
    'Div',
    ('content', 'style', 'className', 'id'),
    'html_components'
)

Input = generate_class(
    'Input',
    ('value', 'placeholder', 'style', 'className', 'id', 'dependencies'),
    'core_components'
)


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = dash.Dash('my-app')

        self.app.layout = Div([
            Div('Hello World', id='header', style={'color': 'red'}),
            Input(id='id1', placeholder='Type a value'),
            Input(id='id2', placeholder='Type a value')
        ])

        self.app.component_suites = [
            'html_components',
            'core_components'
        ]

        self.client = self.app.server.test_client()

        self.maxDiff = 100*1000

    def test_route_list(self):
        urls = [rule.rule for rule in self.app.server.url_map.iter_rules()]

        self.assertEqual(
            sorted(urls),
            sorted([
                '/interceptor',
                '/initialize',
                '/dependencies',
                '/',
                '/js/component-suites/<path:path>',
                '/static/<path:filename>'
            ])
        )

    def test_initialize_route(self):
        response = self.client.get('/initialize')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data),
            json.loads(
                json.dumps(self.app.layout, cls=plotly.utils.PlotlyJSONEncoder)
            )
        )

    def test_dependencies_route(self):
        self.app.react('header', ['id1'])
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

        self.app.react('header',
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
        self.app.react('header', state=state, events=events)
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



    def test_index_html(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_single_observer_returning_a_dict(self):
        @self.app.react('header', ['id1'])
        def update_header(input1):
            self.assertEqual({'value': 'New Value'}, input1)
            new_value = input1['value']
            return {
                'content': new_value,
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

    def test_single_observer_returning_a_component(self):
        @self.app.react('header', ['id1'])
        def update_header(input1):
            self.assertEqual({'value': 'New Value'}, input1)
            new_value = input1['value']
            return {
                'content': Div('New Component')
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
                            'content': 'New Component'
                        }
                    }
                }
            }
        )

    @unittest.skip("""Not supported yet.
        Right now, @react updates app.layout with the dependencies which
        end up getting served by /initialize.

        We should just serve app.react_map as part of /initialize
    """)
    def test_single_observer_updating_component_that_doesnt_exist(self):
        # It's possible to register callbacks for components that don't
        # exist in the initial layout because users could add them as
        # children in response to another callback
        @self.app.react('doesnt-exist-yet', ['id1'])
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

    def test_single_observer_with_multiple_controllers(self):
        @self.app.react('header', ['id1', 'id2'])
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
