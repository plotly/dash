import unittest
from dash.development.base_component import generate_class
import dash
import json
import plotly
from dash_core_components import Input
from dash_html_components import Div
import pkgutil
import warnings


def generate_css(css_links):
    return '\n'.join([
        '<link rel="stylesheet" href="{}"></link>'.format(l)
        for l in css_links
    ])


def generate_js(js_links):
    return '\n'.join([
        '<script type="text/javascript" src="{}"></script>'.format(l)
        for l in js_links
    ])


class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = dash.Dash('my-app')

        self.app.layout = Div([
            Div('Hello World', id='header', style={'color': 'red'}),
            Input(id='id1', placeholder='Type a value'),
            Input(id='id2', placeholder='Type a value')
        ])

        self.client = self.app.server.test_client()

        self.maxDiff = 100*1000

    @unittest.skip("")
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

    @unittest.skip("")
    def test_initialize_route(self):
        response = self.client.get('/initialize')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.data),
            json.loads(
                json.dumps(self.app.layout, cls=plotly.utils.PlotlyJSONEncoder)
            )
        )

    @unittest.skip("")
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

    @unittest.skip("")
    def test_index_html(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @unittest.skip("")
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

    @unittest.skip("")
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

    @unittest.skip("")
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

    @unittest.skip("")
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

    def test_serving_scripts(self):
        self.app.scripts.config.serve_locally = True
        self.app._setup_server()
        response = self.client.get('/component-suites/dash_renderer/bundle.js?v=0.2.9')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            pkgutil.get_data('dash_renderer', 'bundle.js')
        )

    def test_css(self):
        self.app.css.config.serve_locally = False
        self.assertEqual(
            self.app._generate_css_dist_html(),
            generate_css([
                "https://unpkg.com/react-select@1.0.0-rc.3/dist/react-select.min.css",
                "https://unpkg.com/rc-slider@6.1.2/assets/index.css"
            ])
        )

        self.app.css.config.serve_locally = True
        self.assertEqual(
            self.app._generate_css_dist_html(),
            generate_css([
                "/component-suites/dash_core_components/react-select@1.0.0-rc.3.min.css?v=0.2.11",
                "/component-suites/dash_core_components/rc-slider@6.1.2.css?v=0.2.11"
            ])
        )

        self.app.css.append_css({
            'external_url': ['/this', '/that']
        })
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                self.app._generate_css_dist_html(),
                generate_css([
                    "/component-suites/dash_core_components/react-select@1.0.0-rc.3.min.css?v=0.2.11",
                    "/component-suites/dash_core_components/rc-slider@6.1.2.css?v=0.2.11"
                ])
            )
            assert len(w) == 1

        self.app.css.config.serve_locally = False
        self.assertEqual(
            self.app._generate_css_dist_html(),
            generate_css([
                "https://unpkg.com/react-select@1.0.0-rc.3/dist/react-select.min.css",
                "https://unpkg.com/rc-slider@6.1.2/assets/index.css",
                '/this',
                '/that'
            ])
        )


    def test_js(self):
        self.app.scripts.config.serve_locally = False
        self.assertEqual(
            self.app._generate_scripts_html(),
            generate_js([
                "https://unpkg.com/react@15.4.2/dist/react.min.js",
                "https://unpkg.com/react-dom@15.4.2/dist/react-dom.min.js",
                "https://unpkg.com/dash-html-components@0.3.8/dash_html_components/bundle.js",
                "https://unpkg.com/dash-core-components@0.2.11/dash_core_components/bundle.js",
                "/component-suites/dash_renderer/bundle.js?v=0.2.9"
            ])
        )

        self.app.scripts.config.serve_locally = True
        self.assertEqual(
            self.app._generate_scripts_html(),
            generate_js([
                "/component-suites/dash_renderer/react@15.4.2.min.js?v=0.2.9",
                "/component-suites/dash_renderer/react-dom@15.4.2.min.js?v=0.2.9",
                "/component-suites/dash_html_components/bundle.js?v=0.3.8",
                "/component-suites/dash_core_components/bundle.js?v=0.2.11",
                "/component-suites/dash_renderer/bundle.js?v=0.2.9"
            ])
        )

        self.app.scripts.append_script({
            'external_url': ['/this', '/that']
        })
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                self.app._generate_scripts_html(),
                generate_js([
                    "/component-suites/dash_renderer/react@15.4.2.min.js?v=0.2.9",
                    "/component-suites/dash_renderer/react-dom@15.4.2.min.js?v=0.2.9",
                    "/component-suites/dash_html_components/bundle.js?v=0.3.8",
                    "/component-suites/dash_core_components/bundle.js?v=0.2.11",
                    "/component-suites/dash_renderer/bundle.js?v=0.2.9"
                ])
            )
            print(len(w))
            assert len(w) == 1

        self.app.scripts.config.serve_locally = False
        self.assertEqual(
            self.app._generate_scripts_html(),
            generate_js([
                "https://unpkg.com/react@15.4.2/dist/react.min.js",
                "https://unpkg.com/react-dom@15.4.2/dist/react-dom.min.js",
                "https://unpkg.com/dash-html-components@0.3.8/dash_html_components/bundle.js",
                "https://unpkg.com/dash-core-components@0.2.11/dash_core_components/bundle.js",
                '/this',
                '/that',
                "/component-suites/dash_renderer/bundle.js?v=0.2.9",
            ])
        )
