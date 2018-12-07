from __future__ import print_function

import itertools
import os
import random
import sys
import collections
import importlib
import json
import pkgutil
import threading
import warnings
import re
import logging

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
from ._utils import format_tag as _format_tag
from ._utils import generate_hash as _generate_hash
from . import _watch
from ._utils import get_asset_path as _get_asset_path
from . import _configs


_default_index = '''<!DOCTYPE html>
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
</html>'''

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
# pylint: disable=too-many-arguments, too-many-locals
class Dash(object):
    def __init__(
            self,
            name='__main__',
            server=None,
            static_folder='static',
            assets_folder=None,
            assets_url_path='/assets',
            assets_ignore='',
            include_assets_files=True,
            url_base_pathname=None,
            assets_external_path=None,
            requests_pathname_prefix=None,
            routes_pathname_prefix=None,
            compress=True,
            meta_tags=None,
            index_string=_default_index,
            external_scripts=None,
            external_stylesheets=None,
            suppress_callback_exceptions=None,
            components_cache_max_age=None,
            **kwargs):

        # pylint-disable: too-many-instance-attributes
        if 'csrf_protect' in kwargs:
            warnings.warn('''
                `csrf_protect` is no longer used,
                CSRF protection has been removed as it is no longer
                necessary.
                See https://github.com/plotly/dash/issues/141 for details.
                ''', DeprecationWarning)

        name = name if server is None else server.name
        self._assets_folder = assets_folder or os.path.join(
            flask.helpers.get_root_path(name), 'assets'
        )
        self._assets_url_path = assets_url_path

        # allow users to supply their own flask server
        self.server = server or Flask(name, static_folder=static_folder)

        if 'assets' not in self.server.blueprints:
            self.server.register_blueprint(
                flask.Blueprint('assets', 'assets',
                                static_folder=self._assets_folder,
                                static_url_path=assets_url_path))

        env_configs = _configs.env_configs()

        url_base_pathname, routes_pathname_prefix, requests_pathname_prefix = \
            _configs.pathname_configs(
                url_base_pathname,
                routes_pathname_prefix,
                requests_pathname_prefix,
                environ_configs=env_configs)

        self.url_base_pathname = url_base_pathname
        self.config = _AttributeDict({
            'suppress_callback_exceptions': _configs.get_config(
                'suppress_callback_exceptions',
                suppress_callback_exceptions, env_configs, False
            ),
            'routes_pathname_prefix': routes_pathname_prefix,
            'requests_pathname_prefix': requests_pathname_prefix,
            'include_assets_files': _configs.get_config(
                'include_assets_files',
                include_assets_files,
                env_configs,
                True),
            'assets_external_path': _configs.get_config(
                'assets_external_path', assets_external_path, env_configs, ''),
            'components_cache_max_age': int(_configs.get_config(
                'components_cache_max_age', components_cache_max_age,
                env_configs, 2678400))
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

        self._external_scripts = external_scripts or []
        self._external_stylesheets = external_stylesheets or []

        self.assets_ignore = assets_ignore

        self.registered_paths = collections.defaultdict(set)

        # urls
        self.routes = []

        self._add_url(
            '{}_dash-layout'.format(self.config['routes_pathname_prefix']),
            self.serve_layout)

        self._add_url(
            '{}_dash-dependencies'.format(
                self.config['routes_pathname_prefix']),
            self.dependencies)

        self._add_url(
            '{}_dash-update-component'.format(
                self.config['routes_pathname_prefix']),
            self.dispatch,
            ['POST'])

        self._add_url((
            '{}_dash-component-suites'
            '/<string:package_name>'
            '/<path:path_in_package_dist>').format(
                self.config['routes_pathname_prefix']),
                      self.serve_component_suites)

        self._add_url(
            '{}_dash-routes'.format(self.config['routes_pathname_prefix']),
            self.serve_routes)

        self._add_url(
            self.config['routes_pathname_prefix'],
            self.index)

        self._add_url(
            '{}_reload-hash'.format(self.config['routes_pathname_prefix']),
            self.serve_reload_hash)

        # catch-all for front-end routes, used by dcc.Location
        self._add_url(
            '{}<path:path>'.format(self.config['routes_pathname_prefix']),
            self.index)

        self._add_url(
            '{}_favicon.ico'.format(self.config['routes_pathname_prefix']),
            self._serve_default_favicon)

        self.server.before_first_request(self._setup_server)

        self._layout = None
        self._cached_layout = None
        self._dev_tools = _AttributeDict({
            'serve_dev_bundles': False,
            'hot_reload': False,
            'hot_reload_interval': 3000,
            'hot_reload_watch_interval': 0.5,
            'hot_reload_max_retry': 8
        })

        # add a handler for components suites errors to return 404
        self.server.errorhandler(exceptions.InvalidResourceError)(
            self._invalid_resources_handler)

        self._assets_files = []

        # hot reload
        self._reload_hash = None
        self._hard_reload = False
        self._lock = threading.RLock()
        self._watch_thread = None
        self._changed_assets = []

        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    def _add_url(self, name, view_func, methods=('GET',)):
        self.server.add_url_rule(
            name,
            view_func=view_func,
            endpoint=name,
            methods=list(methods))

        # record the url in Dash.routes so that it can be accessed later
        # e.g. for adding authentication with flask_login
        self.routes.append(name)

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
        config = {
            'url_base_pathname': self.url_base_pathname,
            'requests_pathname_prefix': self.config['requests_pathname_prefix']
        }
        if self._dev_tools.hot_reload:
            config['hot_reload'] = {
                'interval': self._dev_tools.hot_reload_interval,
                'max_retry': self._dev_tools.hot_reload_max_retry
            }
        return config

    def serve_reload_hash(self):
        hard = self._hard_reload
        changed = self._changed_assets
        self._lock.acquire()
        self._hard_reload = False
        self._changed_assets = []
        self._lock.release()

        return flask.jsonify({
            'reloadHash': self._reload_hash,
            'hard': hard,
            'packages': list(self.registered_paths.keys()),
            'files': list(changed)
        })

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

            module_path = os.path.join(
                os.path.dirname(sys.modules[namespace].__file__),
                relative_package_path)

            modified = int(os.stat(module_path).st_mtime)

            return '{}_dash-component-suites/{}/{}?v={}&m={}'.format(
                self.config['requests_pathname_prefix'],
                namespace,
                relative_package_path,
                importlib.import_module(namespace).__version__,
                modified
            )

        srcs = []
        for resource in resources:
            is_dynamic_resource = resource.get('dynamic', False)

            if 'relative_package_path' in resource:
                paths = resource['relative_package_path']
                paths = [paths] if isinstance(paths, str) else paths

                for rel_path in paths:
                    self.registered_paths[resource['namespace']]\
                        .add(rel_path)

                    if not is_dynamic_resource:
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
                static_url = self.get_asset_url(resource['asset_path'])
                # Add a bust query param
                static_url += '?m={}'.format(resource['ts'])
                srcs.append(static_url)
        return srcs

    def _generate_css_dist_html(self):
        links = self._external_stylesheets + \
            self._collect_and_register_resources(self.css.get_all_css())

        return '\n'.join([
            _format_tag('link', link, opened=True)
            if isinstance(link, dict)
            else '<link rel="stylesheet" href="{}">'.format(link)
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
                dash_renderer._js_dist_dependencies,
                dev_bundles=self._dev_tools.serve_dev_bundles
            )) + self._external_scripts + self._collect_and_register_resources(
                self.scripts.get_all_scripts(
                    dev_bundles=self._dev_tools.serve_dev_bundles) +
                self.scripts._resources._filter_resources(
                    dash_renderer._js_dist,
                    dev_bundles=self._dev_tools.serve_dev_bundles
                ))

        return '\n'.join([
            _format_tag('script', src)
            if isinstance(src, dict)
            else '<script src="{}"></script>'.format(src)
            for src in srcs
        ])

    def _generate_config_html(self):
        return (
            '<script id="_dash-config" type="application/json">'
            '{}'
            '</script>'
        ).format(json.dumps(self._config()))

    def _generate_meta_html(self):
        has_ie_compat = any(
            x.get('http-equiv', '') == 'X-UA-Compatible'
            for x in self._meta_tags)
        has_charset = any('charset' in x for x in self._meta_tags)

        tags = []
        if not has_ie_compat:
            tags.append(
                '<meta http-equiv="X-UA-Compatible" content="IE=edge">'
            )
        if not has_charset:
            tags.append('<meta charset="UTF-8">')

        tags = tags + [
            _format_tag('meta', x, opened=True) for x in self._meta_tags
        ]

        return '\n      '.join(tags)

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, path_in_package_dist):
        if package_name not in self.registered_paths:
            raise exceptions.InvalidResourceError(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, list(self.registered_paths.keys())))

        elif path_in_package_dist not in self.registered_paths[package_name]:
            raise exceptions.InvalidResourceError(
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
            'css': 'text/css',
            'map': 'application/json'
        })[path_in_package_dist.split('.')[-1]]

        headers = {
            'Cache-Control': 'public, max-age={}'.format(
                self.config.components_cache_max_age)
        }

        return Response(
            pkgutil.get_data(package_name, path_in_package_dist),
            mimetype=mimetype,
            headers=headers
        )

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta_html()
        title = getattr(self, 'title', 'Dash')

        if self._favicon:
            favicon_mod_time = os.path.getmtime(
                os.path.join(self._assets_folder, self._favicon))
            favicon_url = self.get_asset_url(self._favicon) + '?m={}'.format(
                favicon_mod_time
            )
        else:
            favicon_url = '{}_favicon.ico'.format(
                self.config.requests_pathname_prefix)

        favicon = _format_tag('link', {
            'rel': 'icon',
            'type': 'image/x-icon',
            'href': favicon_url
        }, opened=True)

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
            } for k, v in self.callback_map.items()
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

    def _validate_callback_output(self, output_value, output):
        valid = [str, dict, int, float, type(None), Component]

        def _raise_invalid(bad_val, outer_val, bad_type, path, index=None,
                           toplevel=False):
            outer_id = "(id={:s})".format(outer_val.id) \
                if getattr(outer_val, 'id', False) else ''
            outer_type = type(outer_val).__name__
            raise exceptions.InvalidCallbackReturnValue('''
            The callback for property `{property:s}` of component `{id:s}`
            returned a {object:s} having type `{type:s}`
            which is not JSON serializable.

            {location_header:s}{location:s}
            and has string representation
            `{bad_val}`

            In general, Dash properties can only be
            dash components, strings, dictionaries, numbers, None,
            or lists of those.
            '''.format(
                property=output.component_property,
                id=output.component_id,
                object='tree with one value' if not toplevel else 'value',
                type=bad_type,
                location_header=(
                    'The value in question is located at'
                    if not toplevel else
                    '''The value in question is either the only value returned,
                    or is in the top level of the returned list,'''
                ),
                location=(
                    "\n" +
                    ("[{:d}] {:s} {:s}".format(index, outer_type, outer_id)
                     if index is not None
                     else ('[*] ' + outer_type + ' ' + outer_id))
                    + "\n" + path + "\n"
                ) if not toplevel else '',
                bad_val=bad_val).replace('    ', ''))

        def _value_is_valid(val):
            return (
                # pylint: disable=unused-variable
                any([isinstance(val, x) for x in valid]) or
                type(val).__name__ == 'unicode'
            )

        def _validate_value(val, index=None):
            # val is a Component
            if isinstance(val, Component):
                for p, j in val.traverse_with_paths():
                    # check each component value in the tree
                    if not _value_is_valid(j):
                        _raise_invalid(
                            bad_val=j,
                            outer_val=val,
                            bad_type=type(j).__name__,
                            path=p,
                            index=index
                        )

                    # Children that are not of type Component or
                    # list/tuple not returned by traverse
                    child = getattr(j, 'children', None)
                    if not isinstance(child, (tuple,
                                              collections.MutableSequence)):
                        if child and not _value_is_valid(child):
                            _raise_invalid(
                                bad_val=child,
                                outer_val=val,
                                bad_type=type(child).__name__,
                                path=p + "\n" + "[*] " + type(child).__name__,
                                index=index
                            )

                # Also check the child of val, as it will not be returned
                child = getattr(val, 'children', None)
                if not isinstance(child, (tuple, collections.MutableSequence)):
                    if child and not _value_is_valid(child):
                        _raise_invalid(
                            bad_val=child,
                            outer_val=val,
                            bad_type=type(child).__name__,
                            path=type(child).__name__,
                            index=index
                        )

            # val is not a Component, but is at the top level of tree
            else:
                if not _value_is_valid(val):
                    _raise_invalid(
                        bad_val=val,
                        outer_val=type(val).__name__,
                        bad_type=type(val).__name__,
                        path='',
                        index=index,
                        toplevel=True
                    )

        if isinstance(output_value, list):
            for i, val in enumerate(output_value):
                _validate_value(val, index=i)
        else:
            _validate_value(output_value)

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

                try:
                    jsonResponse = json.dumps(
                        response,
                        cls=plotly.utils.PlotlyJSONEncoder
                    )
                except TypeError:
                    self._validate_callback_output(output_value, output)
                    raise exceptions.InvalidCallbackReturnValue('''
                    The callback for property `{property:s}`
                    of component `{id:s}` returned a value
                    which is not JSON serializable.

                    In general, Dash properties can only be
                    dash components, strings, dictionaries, numbers, None,
                    or lists of those.
                    '''.format(property=output.component_property,
                               id=output.component_id))

                return flask.Response(
                    jsonResponse,
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

    def _validate_layout(self):
        if self.layout is None:
            raise exceptions.NoLayoutException(
                ''
                'The layout was `None` '
                'at the time that `run_server` was called. '
                'Make sure to set the `layout` attribute of your application '
                'before running the server.')

        to_validate = self._layout_value()

        layout_id = getattr(self.layout, 'id', None)

        component_ids = {layout_id} if layout_id else set()
        for component in to_validate.traverse():
            component_id = getattr(component, 'id', None)
            if component_id and component_id in component_ids:
                raise exceptions.DuplicateIdError(
                    'Duplicate component id found'
                    ' in the initial layout: `{}`'.format(component_id))
            component_ids.add(component_id)

    def _setup_server(self):
        if self.config.include_assets_files:
            self._walk_assets_directory()

        self._validate_layout()

        self._generate_scripts_html()
        self._generate_css_dist_html()

    def _add_assets_resource(self, url_path, file_path):
        res = {'asset_path': url_path, 'filepath': file_path}
        if self.config.assets_external_path:
            res['external_url'] = '{}{}'.format(
                self.config.assets_external_path, url_path)
        self._assets_files.append(file_path)
        return res

    def _walk_assets_directory(self):
        walk_dir = self._assets_folder
        slash_splitter = re.compile(r'[\\/]+')
        ignore_filter = re.compile(self.assets_ignore) \
            if self.assets_ignore else None

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

            files_gen = (x for x in files if not ignore_filter.search(x)) \
                if ignore_filter else files

            for f in sorted(files_gen):
                if base:
                    path = '/'.join([base, f])
                else:
                    path = f

                full = os.path.join(current, f)

                if f.endswith('js'):
                    self.scripts.append_script(
                        self._add_assets_resource(path, full))
                elif f.endswith('css'):
                    self.css.append_css(self._add_assets_resource(path, full))
                elif f == 'favicon.ico':
                    self._favicon = path

    def _invalid_resources_handler(self, err):
        return err.args[0], 404

    def _serve_default_favicon(self):
        headers = {
            'Cache-Control': 'public, max-age={}'.format(
                self.config.components_cache_max_age)
        }
        return flask.Response(pkgutil.get_data('dash', 'favicon.ico'),
                              headers=headers,
                              content_type='image/x-icon')

    def get_asset_url(self, path):
        asset = _get_asset_path(
            self.config.requests_pathname_prefix,
            self.config.routes_pathname_prefix,
            path,
            self._assets_url_path.lstrip('/')
        )

        return asset

    def enable_dev_tools(self,
                         debug=False,
                         dev_tools_serve_dev_bundles=None,
                         dev_tools_hot_reload=None,
                         dev_tools_hot_reload_interval=None,
                         dev_tools_hot_reload_watch_interval=None,
                         dev_tools_hot_reload_max_retry=None,
                         dev_tools_silence_routes_logging=None):
        """
        Activate the dev tools, called by `run_server`. If your application is
        served by wsgi and you want to activate the dev tools, you can call
        this method out of `__main__`.

        If an argument is not provided, it can be set with environment
        variables.

        Available dev_tools environment variables:

            - DASH_DEBUG
            - DASH_SERVE_DEV_BUNDLES
            - DASH_HOT_RELOAD
            - DASH_HOT_RELOAD_INTERVAL
            - DASH_HOT_RELOAD_WATCH_INTERVAL
            - DASH_HOT_RELOAD_MAX_RETRY
            - DASH_SILENCE_ROUTES_LOGGING

        :param debug: If True, then activate all the tools unless specifically
            disabled by the arguments or by environ variables. Available as
            `DASH_DEBUG` environment variable.
        :type debug: bool
        :param dev_tools_serve_dev_bundles: Serve the dev bundles. Available
            as `DASH_SERVE_DEV_BUNDLES` environment variable.
        :type dev_tools_serve_dev_bundles: bool
        :param dev_tools_hot_reload: Activate the hot reloading. Available as
            `DASH_HOT_RELOAD` environment variable.
        :type dev_tools_hot_reload: bool
        :param dev_tools_hot_reload_interval: Interval at which the client will
            request the reload hash. Available as `DASH_HOT_RELOAD_INTERVAL`
            environment variable.
        :type dev_tools_hot_reload_interval: int
        :param dev_tools_hot_reload_watch_interval: Interval at which the
            assets folder are walked for changes. Available as
            `DASH_HOT_RELOAD_WATCH_INTERVAL` environment variable.
        :type dev_tools_hot_reload_watch_interval: float
        :param dev_tools_hot_reload_max_retry: Maximum amount of retries before
            failing and display a pop up. Default 30. Available as
            `DASH_HOT_RELOAD_MAX_RETRY` environment variable.
        :type dev_tools_hot_reload_max_retry: int
        :param dev_tools_silence_routes_logging: Silence the `werkzeug` logger,
            will remove all routes logging. Available as
            `DASH_SILENCE_ROUTES_LOGGING` environment variable.
        :type dev_tools_silence_routes_logging: bool
        :return: debug
        """
        env = _configs.env_configs()
        debug = debug or _configs.get_config('debug', None, env, debug,
                                             is_bool=True)

        self._dev_tools['serve_dev_bundles'] = _configs.get_config(
            'serve_dev_bundles', dev_tools_serve_dev_bundles, env,
            default=debug,
            is_bool=True
        )
        self._dev_tools['hot_reload'] = _configs.get_config(
            'hot_reload', dev_tools_hot_reload, env,
            default=debug,
            is_bool=True
        )
        self._dev_tools['hot_reload_interval'] = int(_configs.get_config(
            'hot_reload_interval', dev_tools_hot_reload_interval, env,
            default=3000
        ))
        self._dev_tools['hot_reload_watch_interval'] = float(
            _configs.get_config(
                'hot_reload_watch_interval',
                dev_tools_hot_reload_watch_interval,
                env,
                default=0.5
            )
        )
        self._dev_tools['hot_reload_max_retry'] = int(
            _configs.get_config(
                'hot_reload_max_retry',
                dev_tools_hot_reload_max_retry,
                env,
                default=8
            )
        )
        self._dev_tools['silence_routes_logging'] = _configs.get_config(
            'silence_routes_logging', dev_tools_silence_routes_logging, env,
            default=debug,
            is_bool=True,
        )

        if self._dev_tools.silence_routes_logging:
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            self.logger.setLevel(logging.INFO)

        if self._dev_tools.hot_reload:
            self._reload_hash = _generate_hash()
            self._watch_thread = threading.Thread(
                target=lambda: _watch.watch(
                    [self._assets_folder],
                    self._on_assets_change,
                    sleep_time=self._dev_tools.hot_reload_watch_interval)
            )
            self._watch_thread.daemon = True
            self._watch_thread.start()

        if debug and self._dev_tools.serve_dev_bundles:
            # Dev bundles only works locally.
            self.scripts.config.serve_locally = True

        return debug

    # noinspection PyProtectedMember
    def _on_assets_change(self, filename, modified, deleted):
        self._lock.acquire()
        self._hard_reload = True
        self._reload_hash = _generate_hash()

        asset_path = os.path.relpath(
            filename, os.path.commonprefix([self._assets_folder, filename]))\
            .replace('\\', '/').lstrip('/')

        self._changed_assets.append({
            'url': self.get_asset_url(asset_path),
            'modified': int(modified),
            'is_css': filename.endswith('css')
        })

        if filename not in self._assets_files and not deleted:
            res = self._add_assets_resource(asset_path, filename)
            if filename.endswith('js'):
                self.scripts.append_script(res)
            elif filename.endswith('css'):
                self.css.append_css(res)

        if deleted:
            if filename in self._assets_files:
                self._assets_files.remove(filename)

            def delete_resource(resources):
                to_delete = None
                for r in resources:
                    if r.get('asset_path') == asset_path:
                        to_delete = r
                        break
                if to_delete:
                    resources.remove(to_delete)

            if filename.endswith('js'):
                # pylint: disable=protected-access
                delete_resource(self.scripts._resources._resources)
            elif filename.endswith('css'):
                # pylint: disable=protected-access
                delete_resource(self.css._resources._resources)

        self._lock.release()

    def run_server(self,
                   port=8050,
                   debug=False,
                   dev_tools_serve_dev_bundles=None,
                   dev_tools_hot_reload=None,
                   dev_tools_hot_reload_interval=None,
                   dev_tools_hot_reload_watch_interval=None,
                   dev_tools_hot_reload_max_retry=None,
                   dev_tools_silence_routes_logging=None,
                   **flask_run_options):
        """
        Start the flask server in local mode, you should not run this on a
        production server and use gunicorn/waitress instead.

        :param port: Port the application
        :type port: int
        :param debug: Set the debug mode of flask and enable the dev tools.
        :type debug: bool
        :param dev_tools_serve_dev_bundles: Serve the dev bundles of components
        :type dev_tools_serve_dev_bundles: bool
        :param dev_tools_hot_reload: Enable the hot reload.
        :type dev_tools_hot_reload: bool
        :param dev_tools_hot_reload_interval: Reload request interval.
        :type dev_tools_hot_reload_interval: int
        :param dev_tools_hot_reload_watch_interval:
        :type dev_tools_hot_reload_watch_interval: float
        :param dev_tools_hot_reload_max_retry: The number of times the reloader
            requests can fail before displaying an alert.
        :type dev_tools_hot_reload_max_retry: int
        :param dev_tools_silence_routes_logging: Silence the routes logs.
        :type dev_tools_silence_routes_logging: bool
        :param flask_run_options: Given to `Flask.run`
        :return:
        """
        debug = self.enable_dev_tools(
            debug,
            dev_tools_serve_dev_bundles,
            dev_tools_hot_reload,
            dev_tools_hot_reload_interval,
            dev_tools_hot_reload_watch_interval,
            dev_tools_hot_reload_max_retry,
            dev_tools_silence_routes_logging,
        )

        if self._dev_tools.silence_routes_logging:
            # Since it's silenced, the address don't show anymore.
            host = flask_run_options.get('host', '127.0.0.1')
            ssl_context = flask_run_options.get('ssl_context')
            self.logger.info(
                'Running on %s://%s:%s%s',
                'https' if ssl_context else 'http',
                host, port, self.config.requests_pathname_prefix
            )

            # Generate a debugger pin and log it to the screen.
            debugger_pin = os.environ['WERKZEUG_DEBUG_PIN'] = '-'.join(
                itertools.chain(
                    ''.join([str(random.randint(0, 9)) for _ in range(3)])
                    for _ in range(3))
            )

            self.logger.info(
                'Debugger PIN: %s',
                debugger_pin
            )

        self.server.run(port=port, debug=debug,
                        **flask_run_options)
