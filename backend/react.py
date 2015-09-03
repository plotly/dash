import flask
import plotly
import json
from flask.ext.cors import CORS


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
        parents = body['parents']

        if target['props']['id'] in self.react_map:
            return self.react_map[target_id]['callback'](*[
                parents[pid]['props'] for pid in
                self.react_map[target_id]['parents']])

    def react(self, component_id, parents=[]):
        def wrap_func(func):
            def add_context(*args, **kwargs):
                component_props = func(*args, **kwargs)
                component = self._get_component(component_id)
                for prop_name, prop in component_props.iteritems():
                    component['props'][prop_name] = prop
                response = {'response': component}
                return flask.jsonify(json.loads(json.dumps(response,
                                     cls=plotly.utils.PlotlyJSONEncoder)))

            self.react_map[component_id] = {
                'callback': add_context,
                'parents': parents
            }
            self._add_dependencies_to_component(component_id, parents)
            return add_context

        return wrap_func

    def _get_component(self, component_id):
        def walk_tree(d, component_id):
            if d.get('props', {}).get('id', '') == component_id:
                return d
            else:
                for k, v in d.iteritems():
                    if isinstance(v, dict):
                        if walk_tree(v, component_id):
                            return v
                    if isinstance(v, list):
                        for vi in v:
                            if isinstance(vi, dict):
                                if walk_tree(vi, component_id):
                                    return vi
        return walk_tree(self.layout, component_id)

    def _add_dependencies_to_component(self, component_id, parents):
        # yikes
        def apply_key_to_nested_dict(d, id, key, value):
            if d.get('props', {}).get('id', '') == id:
                d['props'][key] = value
                return True
            else:
                for k, v in d.iteritems():
                    if isinstance(v, dict):
                        if apply_key_to_nested_dict(v, id, key, value):
                            return True
                    if isinstance(v, list):
                        for vi in v:
                            if isinstance(vi, dict):
                                if apply_key_to_nested_dict(vi, id, key, value):
                                    return True

        component_exists = apply_key_to_nested_dict(self.layout, component_id,
                                                    'dependencies', parents)
        if not component_exists:
            raise Exception("component id {} doesn't exist in layout, "
                            "so I can't assign a listener to it.".format(
                                component_id))
