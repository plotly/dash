import flask
import json
import plotly
from flask import Flask, url_for, send_from_directory
from flask.ext.cors import CORS
from dependency_resolver import Resolver
import os
import importlib


class Dash(object):
    def __init__(self, name=None, url_namespace='', server=None):

        self.url_namespace = url_namespace
        self.layout = None

        # Resolve site-packages location by using plotly as canonical
        # dependency.
        self.resolver = Resolver(plotly, 'plotly')

        self.react_map = {}

        if server is not None:
            self.server = server
        else:
            self.server = Flask(name)

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
            '{}/dependencies'.format(url_namespace),
            view_func=self.dependencies,
            endpoint='{}_{}'.format(url_namespace, 'dependencies'))


        # TODO - A different name for "interceptor".
        # TODO - Should the "interceptor"'s API be keyed by component ID?
        # For example: POST dash.com/components/my-id/update
        self.server.add_url_rule(
            '{}/interceptor'.format(url_namespace),
            view_func=self.interceptor,
            endpoint='{}_{}'.format(url_namespace, 'interceptor'),
            methods=['POST'])

        self.server.add_url_rule(
            '{}/js/component-suites/<path:path>'.format(url_namespace),
            endpoint='{}_{}'.format(url_namespace, 'js'),
            view_func=self.serve_component_suites)

    # Serve the JS bundles for each package
    def serve_component_suites(self, path):
        # path is like 'dash_html_components/bundle.js'
        package, bundle_name = path.split('/')
        if (package not in self.component_suites and
           package != 'dash_renderer'):

            raise Exception(
                'Attempting to server {} but {} '.format(path, package) +
                'was not defined in component_suites')

        directory = os.path.join(self.resolver.site_packages_path, package)
        return send_from_directory(directory, bundle_name)

    def index(self):
        # template in the necessary component suite JS bundles
        # add the version number of the package as a query parameter
        # for cache busting
        scripts = '\n'.join([
            '<script type="text/javascript" src="{}/js/component-suites/{}/bundle.js?v={}"></script>'.format(
                self.url_namespace,
                suite,
                importlib.import_module(suite).__version__
            )
            for suite in self.component_suites + ['dash_renderer']
        ])
        return ('''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8" />
                <title>Dash</title>
            </head>
            <body>
                <div id="react-entry-point"></div>
            </body>

            <footer>

                <script type="text/javascript" src="https://unpkg.com/react@15.4.2/dist/react.min.js"></script>
                <script type="text/javascript" src="https://unpkg.com/react-dom@15.4.2/dist/react-dom.min.js"></script>
                {}
            </footer>
        </html>
        '''.format(
            scripts
        ))

    def initialize(self):
        return flask.jsonify(json.loads(json.dumps(self.layout,
                             cls=plotly.utils.PlotlyJSONEncoder)))

    def dependencies(self):
        return flask.jsonify({
            k: {
                i: j for i, j in v.iteritems() if i != 'callback'
            } for k, v in self.react_map.iteritems()
        })

    def interceptor(self):
        body = json.loads(flask.request.get_data())
        # TODO - This should include which event triggered this function
        target_id = body['id']
        # TODO - Rename 'parents' to 'state'
        # TODO - Include 'events' object
        state = body['state']

        args = []
        for component_registration in self.react_map[target_id]['state']:
            component_id = component_registration['id']
            component_state = state[component_id]
            registered_prop = component_registration['prop']
            if registered_prop == '*':
                args.append(state[component_id])
            else:
                args.append(state[component_id][registered_prop])

        return self.react_map[target_id]['callback'](*args)

    # TODO - Rename "react" to avoid ambiguity with the JS library?
    # Perhaps "update", "respond", ...
    # TODO - Update nomenclature.
    # "Parents" and "Children" should refer to the DOM tree
    # and not the dependency tree.
    # The dependency tree should use the nomenclature
    # "observer" and "controller".
    # "observers" listen for changes from their "controllers". For example,
    # if a graph depends on a dropdown, the graph is the "observer" and the
    # dropdown is a "controller". In this case the graph's "dependency" is
    # the dropdown.
    # TODO - Check this map for recursive or other ill-defined non-tree
    # relationships
    def react(self, component_id, parents=[], state=[], events=[]):
        self.react_map[component_id] = {
            'state': [{'id': p, 'prop': '*'} for p in parents] + state,
            'events': [{'id': p, 'event': 'propChange'} for p in parents] + events
        }

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

            self.react_map[component_id]['callback'] = add_context

            return add_context

        return wrap_func

    def run_server(self, port=8050,
                   debug=True, component_suites=[],
                   **flask_run_options):
        self.component_suites = component_suites
        self.server.run(port=port, debug=debug, **flask_run_options)
