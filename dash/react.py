import flask
import json
import plotly
from flask import Flask, url_for, send_from_directory
from flask.ext.cors import CORS
from dependency_resolver import Resolver


class Dash(object):
    def __init__(self, name=None, url_namespace='', server=None):

        self.layout = None

        # Resolve site-packages location by using plotly as canonical
        # dependency.
        self.resolver = Resolver(plotly, 'plotly')

        self.react_map = {}

        if server is not None:
            self.server = server
        else:
            self.server = Flask(name)

        # The name and port number of the server.
        # Required for subdomain support (e.g.: 'myapp.dev:5000')
        self.server.config['SERVER_NAME'] = 'localhost:8050'

        CORS(self.server)  # TODO: lock this down to dev node server port

        self.server.add_url_rule(
            '{}/'.format(url_namespace),
            endpoint='{}_{}'.format(url_namespace, 'index'),
            view_func=self.index)

        # TODO - Rename "initialize". Perhaps just "GET /components"
        self.server.add_url_rule(
            '{}/initialize'.format(url_namespace),
            view_func=self.initialize,
            endpoint='{}_{}'.format(url_namespace, 'initialize'))

        self.server.add_url_rule(

        # TODO - A different name for "interceptor".
        # TODO - Should the "interceptor"'s API be keyed by component ID?
        # For example: POST dash.com/components/my-id/update
            '{}/interceptor'.format(url_namespace),
            view_func=self.interceptor,
            endpoint='{}_{}'.format(url_namespace, 'interceptor'),
            methods=['POST'])

        self.server.add_url_rule(
            '{}/js/component-suites/<path:path>'.format(url_namespace),
            endpoint='{}_{}'.format(url_namespace, 'js'),
            view_func=self.component_suites)

        # Serve up the main dash bundle with the treeRenderer
        with self.server.app_context():
            url_for('static', filename='bundle.js')

    def component_suites(self, path):
        name = self.resolver.resolve_dependency_name(path)
        return send_from_directory(self.resolver.site_packages_path, name)

    def index(self):
        scripts = ', '.join([
            '"{}/js/component-suites/{}/bundle.js"'.format(
                self.url_namespace, suite
            )
            for suite in self.component_suites
        ])
        return ('''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8" />
                <script
                    src="https://cdn.rawgit.com/ded/script.js/master/dist/script.min.js"
                    type="text/javascript"
                ></script>
            </head>
            <body>
                <div id="react-entry-point"></div>
            </body>

            <footer>

                <!-- TODO: Move this logic into a bundle? -->
                <script type="text/javascript">
                    $script([
                        "https://unpkg.com/react@15/dist/react.js",
                        "https://unpkg.com/react-dom@15/dist/react-dom.js"
                    ], function() {{

                        $script([{}], function() {{

                            $script("{}/js/component-suites/dash_renderer/bundle.js");

                        }});

                    }});
                </script>

            </footer>
        </html>
        '''.format(scripts, self.url_namespace))

    def initialize(self):
        return flask.jsonify(json.loads(json.dumps(self.layout,
                             cls=plotly.utils.PlotlyJSONEncoder)))

    def interceptor(self):
        body = json.loads(flask.request.get_data())
        target = body['target']
        target_id = target['props']['id']
        parent_json = body['parents']
        parents = []
        for pid in self.react_map[target_id]['parents']:
            component_json = parent_json[pid]

            # TODO: Update the component in the layout.
            #       This fails.
            #
            #     self.layout[component_id] = component_json
            #   File "/Users/per/dev/plotly/dash2/dash/dash/development/base_component.py", line 44, in __setitem__
            #     self.content.__setitem__(index, component)
            # TypeError: list indices must be integers, not unicode
            #
            #component_id = component_json['props']['id']
            #self.layout[component_id] = component_json

            parents.append(component_json)

        return self.react_map[target_id]['callback'](*parents)

    def run_server(self, port=8050, debug=True, component_suites=[]):
        self.component_suites = component_suites
        self.server.run(port=port, debug=debug)

    def react(self, component_id, parents=[]):
        def wrap_func(func):
            def add_context(*args, **kwargs):

                new_component_props = func(*args, **kwargs)
                new_component_props['id'] = component_id
                component_json = {}
                if 'content' in new_component_props:
                    component_json['children'] = \
                        new_component_props.pop('content')
                component_json['props'] = new_component_props

                response = {'response': component_json}
                return flask.jsonify(json.loads(json.dumps(response,
                                     cls=plotly.utils.PlotlyJSONEncoder)))

            self.react_map[component_id] = {
                'callback': add_context,
                'parents': parents
            }

            self.layout[component_id].dependencies = parents
            return add_context

        return wrap_func
