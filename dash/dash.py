import flask
import json
import plotly
from flask import Flask, url_for, send_from_directory, Response
from flask_compress import Compress
import os
import importlib
from resources import Scripts, Css
from development.base_component import Component
import pkgutil
import dash_renderer
from dependencies import Event, Input, Output, State
import exceptions


class Dash(object):
    def __init__(self, name=None, url_namespace='', server=None):

        self.url_namespace = url_namespace

        # list of dependencies
        self.react_map = {}

        # allow users to supply their own flask server
        if server is not None:
            self.server = server
        else:
            self.server = Flask(name)

        # gzip
        Compress(self.server)

        # static files from the packages
        self.css = Css()
        self.scripts = Scripts()
        self.registered_paths = {}

        # urls
        self.server.add_url_rule(
            '{}/'.format(url_namespace),
            endpoint='{}_{}'.format(url_namespace, 'index'),
            view_func=self.index)

        # TODO - Rename "initialize". Perhaps just "GET /components"
        self.server.add_url_rule(
            '{}/initialize'.format(url_namespace),
            view_func=self.serve_layout,
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
            methods=['POST'])

        self.server.add_url_rule(
            '{}'
            '/component-suites'
            '/<string:package_name>'
            '/<path:path_in_package_dist>'.format(url_namespace),
            view_func=self.serve_component_suites)

        self._layout = None

    class config:
        supress_callback_exceptions = False

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        if not isinstance(value, Component) and not callable(value):
            raise Exception(
                ''
                'Layout must be a dash component '
                'or a function that returns '
                'a dash component.')

        self._layout = value
        self.css._update_layout(value)
        self.scripts._update_layout(value)
        self._collect_and_register_resources(
            self.scripts.get_all_scripts()
        )
        self._collect_and_register_resources(
            self.css.get_all_css()
        )

    def serve_layout(self):
        if callable(self.layout):
            layout = self.layout()
        else:
            layout = self.layout

        # TODO - Set browser cache limit - pass hash into frontend
        return flask.Response(
            json.dumps(layout,
                       cls=plotly.utils.PlotlyJSONEncoder),
            mimetype='application/json'
        )

    def _collect_and_register_resources(self, resources):
        # template in the necessary component suite JS bundles
        # add the version number of the package as a query parameter
        # for cache busting
        def _relative_url_path(relative_package_path='', namespace=''):

            # track the registered packages
            if namespace in self.registered_paths:
                self.registered_paths[namespace].append(relative_package_path)
            else:
                self.registered_paths[namespace] = [relative_package_path]

            return '{}/component-suites/{}/{}?v={}'.format(
                self.url_namespace,
                namespace,
                relative_package_path,
                importlib.import_module(namespace).__version__
            )

        srcs = []
        for resource in resources:
            if 'relative_package_path' in resource:
                if isinstance(resource['relative_package_path'], basestring):
                    srcs.append(_relative_url_path(**resource))
                else:
                    for rel_path in resource['relative_package_path']:
                        srcs.append(_relative_url_path(
                            relative_package_path=rel_path,
                            namespace=resource['namespace']
                        ))
            elif 'external_url' in resource:
                if isinstance(resource['external_url'], basestring):
                    srcs.append(resource['external_url'])
                else:
                    for url in resource['external_url']:
                        srcs.append(url)
            elif 'absolute_path' in resource:
                raise Exception(
                    'Serving files form absolute_path isn\'t supported yet'
                )
        return srcs

    def _generate_css_dist_html(self):
        links = self._collect_and_register_resources(
            self.css.get_all_css()
        )
        return '\n'.join([
            '<link rel="stylesheet" href="{}"></link>'.format(link)
            for link in links
        ])

    def _generate_scripts_html(self):
        # Dash renderer has dependencies like React which need to be rendered
        # before every other script. However, the dash renderer bundle
        # itself needs to be rendered after all of the component's
        # scripts have rendered.
        # The rest of the scripts can just be loaded after React but before
        # dash renderer.
        srcs = self._collect_and_register_resources(
            self.scripts._resources._filter_resources(
                dash_renderer._js_dist_dependencies
            ) +
            self.scripts.get_all_scripts() +
            self.scripts._resources._filter_resources(
                dash_renderer._js_dist
            )
        )

        return '\n'.join([
            '<script type="text/javascript" src="{}"></script>'.format(src)
            for src in srcs
        ])

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, path_in_package_dist):
        if (package_name not in self.registered_paths):
            raise Exception(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, self.registered_paths.keys()))

        elif (path_in_package_dist not in self.registered_paths[package_name]):
            raise Exception(
                '"{}" is registered but the path requested is not valid.\n'
                'The path requested: "{}"\n'
                'List of registered paths: {}'
                .format(
                    package_name,
                    path_in_package_dist,
                    self.registered_paths
                )
            )

        mimetype = ({
            'js': 'application/javascript',
            'css': 'text/css'
        })[path_in_package_dist.split('.')[-1]]
        return Response(
            pkgutil.get_data(package_name, path_in_package_dist),
            mimetype=mimetype
        )

    def index(self):
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        return ('''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8"/>
                <title>Dash</title>
                {}
            </head>
            <body>
                <div id="react-entry-point">Loading...</div>
            </body>

            <footer>
                {}
            </footer>
        </html>
        '''.format(css, scripts))

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

    def react(self, *args, **kwargs):
        raise DashException(
            'Yo! `react` is no longer used. \n'
            'Use `callback` instead. `callback` has a new syntax too, '
            'so make sure to call `help(app.callback)` to learn more.')

    def _validate_callback(self, output, inputs, state, events):
        if self.layout is None:
            # Without a layout, we can't do validation on the IDs and
            # properties of the elements in the callback.
            raise exceptions.LayoutIsNotDefined('''
                Attempting to assign a callback to the application but
                the `layout` property has not been assigned.
                Assign the `layout` property before assigning callbacks.
            '''.replace('    ', ''))

        for args, object, name in [([output], Output, 'Output'),
                                   (inputs, Input, 'Input'),
                                   (state, State, 'State'),
                                   (events, Event, 'Event')]:

            if not isinstance(args, list):
                raise exceptions.IncorrectTypeException(
                    'The {} argument `{}` is '
                    'not a list of `dash.{}`s.'.format(
                        name.lower(), str(arg), name
                    ))

            for arg in args:
                if not isinstance(arg, object):
                    raise exceptions.IncorrectTypeException(
                        'The {} argument `{}` is '
                        'not of type `dash.{}`.'.format(
                            name.lower(), str(arg), name
                        ))

                if (arg.component_id not in self.layout and
                        arg.component_id != getattr(self.layout, 'id', None)
                        and not self.config.supress_callback_exceptions):
                    raise exceptions.NonExistantIdException('''
                        Attempting to assign a callback to the
                        component with the id "{}" but no
                        components with id "{}" exist in the
                        app\'s layout.\n\n
                        Here is a list of IDs in layout:\n{}\n\n
                        If you are assigning callbacks to components
                        that are generated by other callbacks
                        (and therefore not in the initial layout), then
                        you can suppress this exception by setting
                        `app.config.supress_callback_exceptions=False`.
                    '''.format(
                        arg.component_id,
                        arg.component_id,
                        self.layout.keys() + (
                            [] if not hasattr(self.layout, 'id') else
                            [self.layout.id]
                        )
                    ).replace('    ', ''))

                if not self.config.supress_callback_exceptions:
                    if getattr(self.layout, 'id', None) == arg.component_id:
                        component = self.layout
                    else:
                        component = self.layout[arg.component_id]
                    if (hasattr(arg, 'component_property') and
                            arg.component_property not in
                            component._prop_names):
                        raise exceptions.NonExistantPropException('''
                            Attempting to assign a callback with
                            the property "{}" but the component
                            "{}" doesn't have "{}" as a property.\n
                            Here is a list of the available properties in "{}":
                            {}
                        '''.format(arg.component_property,
                                   arg.component_id,
                                   arg.component_property,
                                   arg.component_id,
                                   component._prop_names).replace('    ', ''))
                    if (hasattr(arg, 'component_event') and
                            arg.component_event not in
                            # TODO - Rename `_prop_names` to `available_props`
                            # and add `available_events` to components
                            getattr(component, 'available_events', ['click', 'blur'])):
                        raise exceptions.NonExistantPropException('''
                            Attempting to assign a callback with
                            the property "{}" but the component
                            "{}" doesn't have "{}" as a property.\n
                            Here is a list of the available properties in "{}":
                            {}
                        '''.format(arg.component_property,
                                   arg.component_id,
                                   arg.component_property,
                                   arg.component_id,
                                   component._prop_names).replace('    ', ''))

        if len(state) > 0 and len(events) == 0 and len(inputs) == 0:
            raise exceptions.MissingEventsException('''
                This callback has {} `State` {}
                but no `Input` elements or `Event` elements.\n
                Without `Input` or `Event` elements, this callback
                will never get called.\n
                (Subscribing to input components will cause the
                callback to be called whenver their values
                change and subscribing to an event will cause the
                callback to be called whenever the event is fired.)
            '''.format(
                len(state),
                'elements' if len(state) > 1 else 'element'
            ).replace('    ', ''))


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
    def callback(self, output, inputs=[], state=[], events=[]):
        self._validate_callback(output, inputs, state, events)

        return

        self.react_map[component_id] = {
            'state': [{'id': p, 'prop': '*'} for p in parents] + state,
            'events': [
                {'id': p, 'event': 'propChange'}
                for p in parents
            ] + events
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
                return flask.Response(
                    json.dumps(response,
                               cls=plotly.utils.PlotlyJSONEncoder),
                    mimetype='application/json'
                )

            self.react_map[component_id]['callback'] = add_context

            return add_context

        return wrap_func

    def _setup_server(self):
        self._generate_scripts_html()
        self._generate_css_dist_html()

    def run_server(self,
                   port=8050,
                   debug=True,
                   threaded=True,
                   **flask_run_options):
        # TODO - If users run the server directly
        # through app.server, then this _setup_server won't get
        # called unless they call it explicitly
        self._setup_server()
        self.server.run(port=port, debug=debug, **flask_run_options)
