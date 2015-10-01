import flask
import plotly
import json
from flask.ext.cors import CORS
import components


class Dash(dict):
    def __init__(self, name):
        self.layout = None

        self.react_map = {}

        self.server = flask.Flask(name)
        CORS(self.server)

        self.server.add_url_rule('/initialize', view_func=self.initialize)
        self.server.add_url_rule('/interceptor', view_func=self.interceptor,
                                 methods=['POST'])

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
            component = getattr(components, component_json['type'])(
                **component_json['props'])
            parents.append(component)
        return self.react_map[target_id]['callback'](*parents)

    def react(self, component_id, parents=[]):
        def wrap_func(func):
            def add_context(*args, **kwargs):

                new_component_props = func(*args, **kwargs)
                new_component_props['id'] = component_id
                response = {'response': new_component_props}
                return flask.jsonify(json.loads(json.dumps(response,
                                     cls=plotly.utils.PlotlyJSONEncoder)))

            self.react_map[component_id] = {
                'callback': add_context,
                'parents': parents
            }
            self.layout[component_id].dependencies = parents
            return add_context

        return wrap_func
