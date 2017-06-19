import flask
import json
import plotly
from flask import Flask, url_for, send_from_directory, Response
from flask_compress import Compress
from flask_seasurf import SeaSurf
import os
import importlib
import requests
import pkgutil
from functools import wraps
import datetime
import collections

import dash_renderer

from .dependencies import Event, Input, Output, State
from .resources import Scripts, Css
from .development.base_component import Component
from .dependencies import Event, Input, Output, State
from . import plotly_api
from . import authentication
from . import exceptions


class Dash(object):
    def __init__(
        self,
        name=None,
        server=None,
        filename=None,
        sharing=None,
        app_url=None,
        url_base_pathname='/'
    ):
        # allow users to supply their own flask server
        if server is not None:
            self.server = server
        else:
            if name is None:
                name = 'dash'
            self.server = Flask(name)

        if self.server.secret_key is None:
            # If user supplied their own server, they might've supplied a
            # secret_key with it
            secret_key_name = 'dash_{}_secret_key'.format(
                # TODO - check for other illegal characters
                name.replace('.', '_')
            )
            secret_key = os.environ.get(
                secret_key_name, SeaSurf()._generate_token()
            )
            os.environ[secret_key_name] = secret_key
            self.server.secret_key = secret_key

        if filename is not None:
            fid = plotly_api.create_or_overwrite_dash_app(
                filename, sharing, app_url
            )
            self.fid = fid
            self.app_url = app_url
            self.sharing = sharing
            self.access_codes = self.create_access_codes()
        else:
            self.fid = None
            self.access_codes = None

        self.url_base_pathname = url_base_pathname

        # list of dependencies
        self.callback_map = {}

        # gzip
        Compress(self.server)

        # csrf protect
        self._csrf = SeaSurf(self.server)

        # static files from the packages
        self.css = Css()
        self.scripts = Scripts()
        self.registered_paths = {}

        # urls
        self.server.add_url_rule(
            '{}_dash-login'.format(self.url_base_pathname),
            view_func=authentication.login,
            methods=['post']
        )

        self.server.add_url_rule(
            '{}_dash-layout'.format(self.url_base_pathname),
            view_func=self.serve_layout)

        self.server.add_url_rule(
            '{}_dash-dependencies'.format(self.url_base_pathname),
            view_func=self.dependencies)

        self.server.add_url_rule(
            '{}_dash-update-component'.format(self.url_base_pathname),
            view_func=self.dispatch,
            methods=['POST'])

        self.server.add_url_rule((
            '{}_dash-component-suites'
            '/<string:package_name>'
            '/<path:path_in_package_dist>').format(self.url_base_pathname),
            view_func=self.serve_component_suites)

        self.server.add_url_rule(
            '{}_dash-routes'.format(self.url_base_pathname),
            view_func=self.serve_routes
        )

        self.server.add_url_rule(self.url_base_pathname, view_func=self.index)

        # catch-all for front-end routes
        self.server.add_url_rule(
            '{}<path:path>'.format(self.url_base_pathname),
            view_func=self.index
        )

        self.server.before_first_request(self._setup_server)

        self._layout = None
        self.routes = []

    def _requires_auth(f):
        def class_decorator(*args, **kwargs):
            self = args[0]
            self.auth_cookie_name = (
                'dash_access_{}'.format(self.fid.replace(':', '_'))
            ) if self.fid else ''
            return authentication.create_requires_auth(
                f,
                # cookies don't allow comma, semicolon, white space
                # those characters are already excluded from plotly usernames
                self.fid,
                self.access_codes,
                self.create_access_codes,
                self.auth_cookie_name,
                *args,
                **kwargs
            )
        class_decorator.__name__ = f.__name__
        return class_decorator

    def create_access_codes(self):
        token = SeaSurf()._generate_token()
        new_access_codes = {
            'access_granted': token,
            'expiration': (
                datetime.datetime.now() + datetime.timedelta(
                    seconds=self.config.permissions_cache_expiry
                )
            )
        }
        self.access_codes = new_access_codes
        return self.access_codes

    class config:
        supress_callback_exceptions = False
        permissions_cache_expiry = 5 * 60

    @property
    def layout(self):
        return self._layout

    def _layout_value(self):
        if isinstance(self._layout, collections.Callable):
            return self._layout()
        else:
            return self._layout

    @layout.setter
    def layout(self, value):
        if not isinstance(value, Component) and not isinstance(value, collections.Callable):
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

    @_requires_auth
    def serve_layout(self):
        layout = self._layout_value()

        # TODO - Set browser cache limit - pass hash into frontend
        return flask.Response(
            json.dumps(layout,
                       cls=plotly.utils.PlotlyJSONEncoder),
            mimetype='application/json'
        )

    def _config(self):
        return {
            'fid': self.fid,
            'plotly_domain': (
                plotly.config.get_config()['plotly_domain']
            ),
            'oauth_client_id': 'RcXzjux4DGfb8bWG9UNGpJUGsTaS0pUVHoEf7Ecl',
            'redirect_uri': 'http://localhost:9595',
            'url_base_pathname': self.url_base_pathname
        }

    @_requires_auth
    def serve_routes(self):
        return flask.Response(
            json.dumps(self.routes,
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

            return '{}_dash-component-suites/{}/{}?v={}'.format(
                self.url_base_pathname,
                namespace,
                relative_package_path,
                importlib.import_module(namespace).__version__
            )

        srcs = []
        for resource in resources:
            if 'relative_package_path' in resource:
                if isinstance(resource['relative_package_path'], str):
                    srcs.append(_relative_url_path(**resource))
                else:
                    for rel_path in resource['relative_package_path']:
                        srcs.append(_relative_url_path(
                            relative_package_path=rel_path,
                            namespace=resource['namespace']
                        ))
            elif 'external_url' in resource:
                if isinstance(resource['external_url'], str):
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
            '<script type="text/JavaScript" src="{}"></script>'.format(src)
            for src in srcs
        ])

    def _generate_config_html(self):
        return (
            '<script id="_dash-config" type="application/json">'
            '{}'
            '</script>'
        ).format(json.dumps(self._config()))

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, path_in_package_dist):
        if (package_name not in self.registered_paths):
            raise Exception(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, list(self.registered_paths.keys())))

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
            'js': 'application/JavaScript',
            'css': 'text/css'
        })[path_in_package_dist.split('.')[-1]]
        return Response(
            pkgutil.get_data(package_name, path_in_package_dist),
            mimetype=mimetype
        )


    def index(self, *args, **kwargs):
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        return ('''
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8"/>
                <title>Dash</title>
                {}
            </head>
            <body>
                <div id="react-entry-point">
                    <div class="_dash-loading">
                        Loading...
                    </div>
                </div>
            </body>

            <footer>
                {}
                {}
            </footer>
        </html>
        '''.format(css, config, scripts))

    @_requires_auth
    def dependencies(self):
        return flask.jsonify([
            {
                'output': {
                    'id': k.split('.')[0],
                    'property': k.split('.')[1]
                },
                'inputs': v['inputs'],
                'state': v['state'],
                'events': v['events']
            } for k, v in list(self.callback_map.items())
        ])

    def react(self, *args, **kwargs):
        raise DashException(
            'Yo! `react` is no longer used. \n'
            'Use `callback` instead. `callback` has a new syntax too, '
            'so make sure to call `help(app.callback)` to learn more.')

    def _validate_callback(self, output, inputs, state, events):
        layout = self._layout_value()
        if (layout is None and
                not self.config.supress_callback_exceptions):
            # Without a layout, we can't do validation on the IDs and
            # properties of the elements in the callback.
            raise exceptions.LayoutIsNotDefined('''
                Attempting to assign a callback to the application but
                the `layout` property has not been assigned.
                Assign the `layout` property before assigning callbacks.
                Alternatively, supress this warning by setting
                `app.config.supress_callback_exceptions=True`
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

                if (not self.config.supress_callback_exceptions and
                        arg.component_id not in layout and
                        arg.component_id != getattr(layout, 'id', None)):
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
                        `app.config.supress_callback_exceptions=True`.
                    '''.format(
                        arg.component_id,
                        arg.component_id,
                        list(layout.keys()) + (
                            [] if not hasattr(layout, 'id') else
                            [layout.id]
                        )
                    ).replace('    ', ''))

                if not self.config.supress_callback_exceptions:

                    if getattr(layout, 'id', None) == arg.component_id:
                        component = layout
                    else:
                        component = layout[arg.component_id]

                    if (hasattr(arg, 'component_property') and
                            arg.component_property not in
                            component.available_properties):
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
                                   component.available_properties
                                   ).replace('    ', ''))

                    if (hasattr(arg, 'component_event') and
                            arg.component_event not in
                            component.available_events):
                        raise exceptions.NonExistantEventException('''
                            Attempting to assign a callback with
                            the event "{}" but the component
                            "{}" doesn't have "{}" as an event.\n
                            Here is a list of the available events in "{}":
                            {}
                        '''.format(arg.component_event,
                                   arg.component_id,
                                   arg.component_event,
                                   arg.component_id,
                                   component.available_events
                                   ).replace('    ', ''))

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

        if '.' in output.component_id:
            raise exceptions.IDsCantContainPeriods('''The Output element
            `{}` contains a period in its ID.
            Periods are not allowed in IDs right now.'''.format(
                output.component_id
            ))

        callback_id = '{}.{}'.format(output.component_id, output.component_property)
        if (callback_id in self.callback_map):
            raise exceptions.CantHaveMultipleOutputs('''
                You have already assigned a callback to the output
                with ID "{}" and property "{}". An output can only have
                a single callback function. Try combining your inputs and
                callback functions together into one function.
            '''.format(
                output.component_id,
                output.component_property).replace('    ', ''))


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

        callback_id = '{}.{}'.format(
            output.component_id, output.component_property
        )
        self.callback_map[callback_id] = {
            'inputs': [
                {'id': c.component_id, 'property': c.component_property}
                for c in inputs
            ],
            'state': [
                {'id': c.component_id, 'property': c.component_property}
                for c in state
            ],
            'events': [
                {'id': c.component_id, 'event': c.component_event}
                for c in events
            ]
        }

        def wrap_func(func):
            def add_context(*args, **kwargs):

                output_value = func(*args, **kwargs)
                response = {
                    'response': {
                        'props': {
                            output.component_property: output_value
                        }
                    }
                }

                return flask.Response(
                    json.dumps(response,
                               cls=plotly.utils.PlotlyJSONEncoder),
                    mimetype='application/json'
                )

            self.callback_map[callback_id]['callback'] = add_context

            return add_context

        return wrap_func

    @_requires_auth
    def dispatch(self):
        body = flask.request.get_json()
        inputs = body.get('inputs', [])
        state = body.get('state', [])
        output = body['output']
        event = body.get('event', {})

        target_id = '{}.{}'.format(output['id'], output['property'])
        args = []
        for component_registration in self.callback_map[target_id]['inputs']:
            component_id = component_registration['id']
            args.append([
                c.get('value', None) for c in inputs if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        for component_registration in self.callback_map[target_id]['state']:
            component_id = component_registration['id']
            args.append([
                c.get('value', None) for c in state if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        return self.callback_map[target_id]['callback'](*args)

    def _setup_server(self):
        self._generate_scripts_html()
        self._generate_css_dist_html()

    def run_server(self,
                   port=8050,
                   debug=True,
                   threaded=True,
                   **flask_run_options):
        self.server.run(port=port, debug=debug, **flask_run_options)
