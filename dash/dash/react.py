import flask
import plotly
import json
from flask import Flask
from flask.ext.cors import CORS


class Dash(object):
    def __init__(self, name=None, url_namespace='', server=None):
        self.layout = None

        self.react_map = {}

        if server is not None:
            self.server = server
        else:
            self.server = flask.Flask(name)

        CORS(self.server) # TODO: lock this down to dev node server port

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
            '{}/'.format(url_namespace),
            endpoint='{}_{}'.format(url_namespace, 'index'),
            view_func=self.index)

    def index(self):
        return flask.render_template('index.html')

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

            # TODO - Get the component from the layout instead of the
            # components module. This used to be:
            # component = getattr(components, component_json['type'])(
            #      **component_json['props'])
            # and now it should be something like:
            component = self.layout[component_json['id']]

            parents.append(component)
        return self.react_map[target_id]['callback'](*parents)

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
