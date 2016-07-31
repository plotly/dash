import flask
import json
from os import path, listdir
import plotly
from flask import Flask, url_for, send_from_directory
from flask.ext.cors import CORS

# Get local path for site-packages
plotly_module_path = path.abspath(plotly.__file__)
plotly_module_name = 'plotly'
plotly_name_index = plotly_module_path.index(plotly_module_name)
site_packages_path = plotly_module_path[:plotly_name_index]
# TEMP: check path
print('site_packages_path: ' + site_packages_path)

# TODO: figure out how we can support local module installations
# using `python setup.py install`, where the module directory has
# appended `-[MODULE_VERSION]-[pyVERSTION].egg`
# e.g. dash_core_components-0.1.4-py2.7.egg
# IDEA:
# 1. Traverse site-packages looking for comp. suite root names;
# 2. map root names to real directory names;
# 3. use mapping in the `component_suites` req. handler.
#
# dash_component_suites = [f for f in listdir(dir)
#     if f.startswith('dash_') and
#     not f.endswith('dist-info')
# ]

class Dash(object):
    def __init__(self, name=None, url_namespace='', server=None):

        self.layout = None

        self.react_map = {}

        if server is not None:
            self.server = server
        else:
            self.server = Flask(name)

        # The name and port number of the server.
        # Required for subdomain support (e.g.: 'myapp.dev:5000')
        self.server.config['SERVER_NAME'] = 'localhost:8050'

        CORS(self.server) # TODO: lock this down to dev node server port

        self.server.add_url_rule(
            '{}/'.format(url_namespace),
            endpoint='{}_{}'.format(url_namespace, 'index'),
            view_func=self.index)

        self.server.add_url_rule(
            '{}/initialize'.format(url_namespace),
            view_func=self.initialize,
            endpoint='{}_{}'.format(url_namespace, 'initialize'))

        self.server.add_url_rule(
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
        # http://localhost:8050/js/component-suites/dash_core_components-0.1.4-py2.7.egg/bundle.js
        print(site_packages_path + path)
        return send_from_directory(site_packages_path, path)

    def index(self):
        return flask.render_template(
            'index.html',
            component_suites=self.component_suites
        )

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
