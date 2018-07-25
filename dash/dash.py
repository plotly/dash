from __future__ import print_function

import os
import sys
import collections
import importlib
import json
import pkgutil
import warnings
import re

from functools import wraps

import plotly
import dash_renderer
import flask
from flask import Flask, Response
from flask_compress import Compress

from .dependencies import Event, Input, Output, State
from .resources import Scripts, Css
from .development.base_component import Component
from . import exceptions
from ._utils import AttributeDict as _AttributeDict
from ._utils import interpolate_str as _interpolate

_default_index = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
        </footer>
    </body>
</html>
'''

_app_entry = '''
<div id="react-entry-point">
    <div class="_dash-loading">
        Loading...
    </div>
</div>
'''

_re_index_entry = re.compile(r'{%app_entry%}')
_re_index_config = re.compile(r'{%config%}')
_re_index_scripts = re.compile(r'{%scripts%}')

_re_index_entry_id = re.compile(r'id="react-entry-point"')
_re_index_config_id = re.compile(r'id="_dash-config"')
_re_index_scripts_id = re.compile(r'src=".*dash[-_]renderer.*"')


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
class Dash(object):
    def __init__(
            self,
            name='__main__',
            server=None,
            static_folder='static',
            assets_folder=None,
            assets_url_path='/assets',
            include_assets_files=True,
            url_base_pathname='/',
            compress=True,
            meta_tags=None,
            index_string=_default_index,
            **kwargs):

        # pylint-disable: too-many-instance-attributes
        if 'csrf_protect' in kwargs:
            warnings.warn('''
                `csrf_protect` is no longer used,
                CSRF protection has been removed as it is no longer
                necessary.
                See https://github.com/plotly/dash/issues/141 for details.
                ''', DeprecationWarning)

        self._assets_folder = assets_folder or os.path.join(
            flask.helpers.get_root_path(name), 'assets'
        )

        # allow users to supply their own flask server
        self.server = server or Flask(name, static_folder=static_folder)

        self.server.register_blueprint(
            flask.Blueprint('assets', 'assets',
                            static_folder=self._assets_folder,
                            static_url_path=assets_url_path))

        self.url_base_pathname = url_base_pathname
        self.config = _AttributeDict({
            'suppress_callback_exceptions': False,
            'routes_pathname_prefix': url_base_pathname,
            'requests_pathname_prefix': url_base_pathname,
            'include_assets_files': include_assets_files,
            'assets_external_path': '',
        })

        # list of dependencies
        self.callback_map = {}

        self._index_string = ''
        self.index_string = index_string
        self._meta_tags = meta_tags or []
        self._favicon = None

        if compress:
            # gzip
            Compress(self.server)

        @self.server.errorhandler(exceptions.PreventUpdate)
        def _handle_error(error):
            """Handle a halted callback and return an empty 204 response"""
            print(error, file=sys.stderr)
            return ('', 204)

        # static files from the packages
        self.css = Css()
        self.scripts = Scripts()
        self.registered_paths = {}

        # urls

        def add_url(name, view_func, methods=('GET',)):
            self.server.add_url_rule(
                name,
                view_func=view_func,
                endpoint=name,
                methods=list(methods)
            )

        add_url(
            '{}_dash-layout'.format(self.config['routes_pathname_prefix']),
            self.serve_layout)

        add_url(
            '{}_dash-dependencies'.format(
                self.config['routes_pathname_prefix']),
            self.dependencies)

        add_url(
            '{}_dash-update-component'.format(
                self.config['routes_pathname_prefix']),
            self.dispatch,
            ['POST'])

        add_url((
            '{}_dash-component-suites'
            '/<string:package_name>'
            '/<path:path_in_package_dist>').format(
                self.config['routes_pathname_prefix']),
                self.serve_component_suites)

        add_url(
            '{}_dash-routes'.format(self.config['routes_pathname_prefix']),
            self.serve_routes)

        add_url(
            self.config['routes_pathname_prefix'],
            self.index)

        # catch-all for front-end routes
        add_url(
            '{}<path:path>'.format(self.config['routes_pathname_prefix']),
            self.index)

        self.server.before_first_request(self._setup_server)

        self._layout = None
        self._cached_layout = None
        self.routes = []

    @property
    def layout(self):
        return self._layout

    def _layout_value(self):
        if isinstance(self._layout, collections.Callable):
            self._cached_layout = self._layout()
        else:
            self._cached_layout = self._layout
        return self._cached_layout

    @layout.setter
    def layout(self, value):
        if (not isinstance(value, Component) and
                not isinstance(value, collections.Callable)):
            raise Exception(
                ''
                'Layout must be a dash component '
                'or a function that returns '
                'a dash component.')

        self._layout = value

        layout_value = self._layout_value()
        # pylint: disable=protected-access
        self.css._update_layout(layout_value)
        self.scripts._update_layout(layout_value)

    @property
    def index_string(self):
        return self._index_string

    @index_string.setter
    def index_string(self, value):
        checks = (
            (_re_index_entry.search(value), 'app_entry'),
            (_re_index_config.search(value), 'config',),
            (_re_index_scripts.search(value), 'scripts'),
        )
        missing = [missing for check, missing in checks if not check]
        if missing:
            raise Exception(
                'Did you forget to include {} in your index string ?'.format(
                    ', '.join('{%' + x + '%}' for x in missing)
                )
            )
        self._index_string = value

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
            'url_base_pathname': self.url_base_pathname,
            'requests_pathname_prefix': self.config['requests_pathname_prefix']
        }

    def serve_routes(self):
        return flask.Response(
            json.dumps(self.routes,
                       cls=plotly.utils.PlotlyJSONEncoder),
            mimetype='application/json'
        )

    def _collect_and_register_resources(self, resources):
        # now needs the app context.
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
                self.config['routes_pathname_prefix'],
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
                    'Serving files from absolute_path isn\'t supported yet'
                )
            elif 'asset_path' in resource:
                static_url = flask.url_for('assets.static',
                                           filename=resource['asset_path'])
                srcs.append(static_url)
        return srcs

    def _generate_css_dist_html(self):
        links = self._collect_and_register_resources(
            self.css.get_all_css()
        )
        return '\n'.join([
            '<link rel="stylesheet" href="{}">'.format(link)
            for link in links
        ])

    def _generate_scripts_html(self):
        # Dash renderer has dependencies like React which need to be rendered
        # before every other script. However, the dash renderer bundle
        # itself needs to be rendered after all of the component's
        # scripts have rendered.
        # The rest of the scripts can just be loaded after React but before
        # dash renderer.
        # pylint: disable=protected-access
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
            '<script src="{}"></script>'.format(src)
            for src in srcs
        ])

    def _generate_config_html(self):
        return (
            '<script id="_dash-config" type="application/json">'
            '{}'
            '</script>'
        ).format(json.dumps(self._config()))

    def _generate_meta_html(self):
        has_charset = any('charset' in x for x in self._meta_tags)

        tags = []
        if not has_charset:
            tags.append('<meta charset="UTF-8"/>')
        for meta in self._meta_tags:
            attributes = []
            for k, v in meta.items():
                attributes.append('{}="{}"'.format(k, v))
            tags.append('<meta {} />'.format(' '.join(attributes)))

        return '\n      '.join(tags)

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, path_in_package_dist):
        if package_name not in self.registered_paths:
            raise Exception(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, list(self.registered_paths.keys())))

        elif path_in_package_dist not in self.registered_paths[package_name]:
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

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta_html()
        title = getattr(self, 'title', 'Dash')
        if self._favicon:
            favicon = '<link rel="icon" type="image/x-icon" href="{}">'.format(
                flask.url_for('assets.static', filename=self._favicon))
        else:
            favicon = ''

        index = self.interpolate_index(
            metas=metas, title=title, css=css, config=config,
            scripts=scripts, app_entry=_app_entry, favicon=favicon)

        checks = (
            (_re_index_entry_id.search(index), '#react-entry-point'),
            (_re_index_config_id.search(index), '#_dash-configs'),
            (_re_index_scripts_id.search(index), 'dash-renderer'),
        )
        missing = [missing for check, missing in checks if not check]

        if missing:
            plural = 's' if len(missing) > 1 else ''
            raise Exception(
                'Missing element{pl} {ids} in index.'.format(
                    ids=', '.join(missing),
                    pl=plural
                )
            )

        return index

    def interpolate_index(self,
                          metas='', title='', css='', config='',
                          scripts='', app_entry='', favicon=''):
        """
        Called to create the initial HTML string that is loaded on page.
        Override this method to provide you own custom HTML.

        :Example:

            class MyDash(dash.Dash):
                def interpolate_index(self, **kwargs):
                    return '''
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <title>My App</title>
                        </head>
                        <body>
                            <div id="custom-header">My custom header</div>
                            {app_entry}
                            {config}
                            {scripts}
                            <div id="custom-footer">My custom footer</div>
                        </body>
                    </html>
                    '''.format(
                        app_entry=kwargs.get('app_entry'),
                        config=kwargs.get('config'),
                        scripts=kwargs.get('scripts'))

        :param metas: Collected & formatted meta tags.
        :param title: The title of the app.
        :param css: Collected & formatted css dependencies as <link> tags.
        :param config: Configs needed by dash-renderer.
        :param scripts: Collected & formatted scripts tags.
        :param app_entry: Where the app will render.
        :param favicon: A favicon <link> tag if found in assets folder.
        :return: The interpolated HTML string for the index.
        """
        return _interpolate(self.index_string,
                            metas=metas,
                            title=title,
                            css=css,
                            config=config,
                            scripts=scripts,
                            favicon=favicon,
                            app_entry=app_entry)

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

    # pylint: disable=unused-argument, no-self-use
    def react(self, *args, **kwargs):
        raise exceptions.DashException(
            'Yo! `react` is no longer used. \n'
            'Use `callback` instead. `callback` has a new syntax too, '
            'so make sure to call `help(app.callback)` to learn more.')

    def _validate_callback(self, output, inputs, state, events):
        # pylint: disable=too-many-branches
        layout = self._cached_layout or self._layout_value()

        if (layout is None and
                not self.config.first('suppress_callback_exceptions',
                                      'supress_callback_exceptions')):
            # Without a layout, we can't do validation on the IDs and
            # properties of the elements in the callback.
            raise exceptions.LayoutIsNotDefined('''
                Attempting to assign a callback to the application but
                the `layout` property has not been assigned.
                Assign the `layout` property before assigning callbacks.
                Alternatively, suppress this warning by setting
                `app.config['suppress_callback_exceptions']=True`
            '''.replace('    ', ''))

        for args, obj, name in [([output], Output, 'Output'),
                                (inputs, Input, 'Input'),
                                (state, State, 'State'),
                                (events, Event, 'Event')]:

            if not isinstance(args, list):
                raise exceptions.IncorrectTypeException(
                    'The {} argument `{}` is '
                    'not a list of `dash.dependencies.{}`s.'.format(
                        name.lower(), str(args), name
                    ))

            for arg in args:
                if not isinstance(arg, obj):
                    raise exceptions.IncorrectTypeException(
                        'The {} argument `{}` is '
                        'not of type `dash.{}`.'.format(
                            name.lower(), str(arg), name
                        ))

                if (not self.config.first('suppress_callback_exceptions',
                                          'supress_callback_exceptions') and
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
                        `app.config['suppress_callback_exceptions']=True`.
                    '''.format(
                        arg.component_id,
                        arg.component_id,
                        list(layout.keys()) + (
                            [] if not hasattr(layout, 'id') else
                            [layout.id]
                        )
                    ).replace('    ', ''))

                if not self.config.first('suppress_callback_exceptions',
                                         'supress_callback_exceptions'):

                    if getattr(layout, 'id', None) == arg.component_id:
                        component = layout
                    else:
                        component = layout[arg.component_id]

                    if (hasattr(arg, 'component_property') and
                            arg.component_property not in
                            component.available_properties and not
                            any(arg.component_property.startswith(w) for w in
                                component.available_wildcard_properties)):
                        raise exceptions.NonExistantPropException('''
                            Attempting to assign a callback with
                            the property "{}" but the component
                            "{}" doesn't have "{}" as a property.\n
                            Here is a list of the available properties in "{}":
                            {}
                        '''.format(
                            arg.component_property,
                            arg.component_id,
                            arg.component_property,
                            arg.component_id,
                            component.available_properties).replace(
                                '    ', ''))

                    if (hasattr(arg, 'component_event') and
                            arg.component_event not in
                            component.available_events):
                        raise exceptions.NonExistantEventException('''
                            Attempting to assign a callback with
                            the event "{}" but the component
                            "{}" doesn't have "{}" as an event.\n
                            Here is a list of the available events in "{}":
                            {}
                        '''.format(
                            arg.component_event,
                            arg.component_id,
                            arg.component_event,
                            arg.component_id,
                            component.available_events).replace('    ', ''))

        if state and not events and not inputs:
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

        callback_id = '{}.{}'.format(
            output.component_id, output.component_property)
        if callback_id in self.callback_map:
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
    # pylint: disable=dangerous-default-value
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
            @wraps(func)
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

    def dispatch(self):
        body = flask.request.get_json()
        inputs = body.get('inputs', [])
        state = body.get('state', [])
        output = body['output']

        target_id = '{}.{}'.format(output['id'], output['property'])
        args = []
        for component_registration in self.callback_map[target_id]['inputs']:
            args.append([
                c.get('value', None) for c in inputs if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        for component_registration in self.callback_map[target_id]['state']:
            args.append([
                c.get('value', None) for c in state if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        return self.callback_map[target_id]['callback'](*args)

    def _setup_server(self):
        if self.config.include_assets_files:
            self._walk_assets_directory()

        # Make sure `layout` is set before running the server
        value = getattr(self, 'layout')
        if value is None:
            raise exceptions.NoLayoutException(
                ''
                'The layout was `None` '
                'at the time that `run_server` was called. '
                'Make sure to set the `layout` attribute of your application '
                'before running the server.')

        self._generate_scripts_html()
        self._generate_css_dist_html()

    def _walk_assets_directory(self):
        walk_dir = self._assets_folder
        slash_splitter = re.compile(r'[\\/]+')

        def add_resource(p):
            res = {'asset_path': p}
            if self.config.assets_external_path:
                res['external_url'] = '{}{}'.format(
                    self.config.assets_external_path, path)
            return res

        for current, _, files in os.walk(walk_dir):
            if current == walk_dir:
                base = ''
            else:
                s = current.replace(walk_dir, '').lstrip('\\').lstrip('/')
                splitted = slash_splitter.split(s)
                if len(splitted) > 1:
                    base = '/'.join(slash_splitter.split(s))
                else:
                    base = splitted[0]

            for f in sorted(files):
                if base:
                    path = '/'.join([base, f])
                else:
                    path = f

                if f.endswith('js'):
                    self.scripts.append_script(add_resource(path))
                elif f.endswith('css'):
                    self.css.append_css(add_resource(path))
                elif f == 'favicon.ico':
                    self._favicon = path

    def run_server(self,
                   port=8050,
                   debug=False,
                   **flask_run_options):
        self.server.run(port=port, debug=debug, **flask_run_options)
