from __future__ import print_function

import os
import sys
import collections
import importlib
import json
import pprint
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
from .development.validator import (DashValidator,
                                    generate_validation_error_message)
from . import exceptions
from ._utils import AttributeDict as _AttributeDict
from ._utils import interpolate_str as _interpolate
from ._utils import format_tag as _format_tag
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
            disable_component_validation=None,
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
            'disable_component_validation': _configs.get_config(
                'disable_component_validation',
                disable_component_validation, env_configs, False
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

        self.registered_paths = {}
        self.namespaces = {}

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
            'serve_dev_bundles': False
        })

        # add a handler for components suites errors to return 404
        self.server.errorhandler(exceptions.InvalidResourceError)(
            self._invalid_resources_handler)

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
            'css': 'text/css'
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

    def _validate_callback_definition(self, output, inputs, state, events):
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

    def _debug_callback_serialization_error(self, output_value, output):
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
                    # collections.MutableSequence not returned by traverse
                    child = getattr(j, 'children', None)
                    if not isinstance(child, collections.MutableSequence):
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
                if not isinstance(child, collections.MutableSequence):
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
        self._validate_callback_definition(output, inputs, state, events)

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
            def add_context(validated_output):
                response = {
                    'response': {
                        'props': {
                            output.component_property: validated_output
                        }
                    }
                }

                try:
                    jsonResponse = json.dumps(
                        response,
                        cls=plotly.utils.PlotlyJSONEncoder
                    )
                except TypeError:
                    self._debug_callback_serialization_error(
                        validated_output,
                        output
                    )
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

            self.callback_map[callback_id]['func'] = func
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

        output_value = self.callback_map[target_id]['func'](*args)

        # Only validate if we get required information from renderer
        # and validation is not turned off by user
        if (
                (not self.config.disable_component_validation) and
                'namespace' in output and
                'type' in output
        ):
            # Python2.7 might make these keys and values unicode
            namespace = str(output['namespace'])
            component_type = str(output['type'])
            component_id = str(output['id'])
            component_property = str(output['property'])
            callback_func_name = self.callback_map[target_id]['func'].__name__
            self._validate_callback_output(namespace, component_type,
                                           component_id, component_property,
                                           callback_func_name,
                                           args, output_value)

        return self.callback_map[target_id]['callback'](output_value)

    def _validate_callback_output(self, namespace, component_type,
                                  component_id, component_property,
                                  callback_func_name, args, value):
        if namespace not in self.namespaces:
            self.namespaces[namespace] =\
                importlib.import_module(namespace)
        namespace = self.namespaces[namespace]
        component = getattr(namespace, component_type)
        # pylint: disable=protected-access
        validator = DashValidator({
            component_property: component._schema.get(component_property, {})
        })
        valid = validator.validate({component_property: value})
        if not valid:
            error_message = """


                A Dash Callback produced an invalid value!

                Dash tried to update the `{component_property}` prop of the
                `{component_name}` with id `{component_id}` by calling the
                `{callback_func_name}` function with `{args}` as arguments.

                This function call returned `{value}`, which did not pass
                validation tests for the `{component_name}` component.

                The expected schema for the `{component_property}` prop of the
                `{component_name}` component is:

                ***************************************************************
                {component_schema}
                ***************************************************************

            """.replace('    ', '').format(
                component_property=component_property,
                component_name=component.__name__,
                component_id=component_id,
                callback_func_name=callback_func_name,
                args='({})'.format(", ".join(map(repr, args))),
                value=value,
                component_schema=pprint.pformat(
                    component._schema[component_property]
                )
            )
            error_message +=\
                "The errors in validation are as follows:\n\n"

            raise exceptions.CallbackOutputValidationError(
                generate_validation_error_message(
                    validator.errors, 0, error_message))
        # Must also validate initialization of newly created components
        if component_property == 'children':
            if isinstance(value, Component):
                value.validate()
                for component in value.traverse():
                    if isinstance(component, Component):
                        component.validate()

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
            if (
                    not self.config.disable_component_validation and
                    isinstance(component, Component)
            ):
                component.validate()
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

    def _walk_assets_directory(self):
        walk_dir = self._assets_folder
        slash_splitter = re.compile(r'[\\/]+')
        ignore_filter = re.compile(self.assets_ignore) \
            if self.assets_ignore else None

        def add_resource(p, filepath):
            res = {'asset_path': p, 'filepath': filepath}
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
                        add_resource(path, full))
                elif f.endswith('css'):
                    self.css.append_css(add_resource(path, full))
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
                         dev_tools_serve_dev_bundles=None):
        """
        Activate the dev tools, called by `run_server`. If your application is
        served by wsgi and you want to activate the dev tools, you can call
        this method out of `__main__`.

        :param debug: If True, then activate all the tools unless specified.
        :type debug: bool
        :param dev_tools_serve_dev_bundles: Serve the dev bundles.
        :type dev_tools_serve_dev_bundles: bool
        :return:
        """
        env = _configs.env_configs()
        debug = debug or _configs.get_config('debug', None, env, debug,
                                             is_bool=True)

        self._dev_tools['serve_dev_bundles'] = _configs.get_config(
            'serve_dev_bundles', dev_tools_serve_dev_bundles, env,
            default=debug,
            is_bool=True
        )
        return debug

    def run_server(self,
                   port=8050,
                   debug=False,
                   dev_tools_serve_dev_bundles=None,
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
        :param flask_run_options: Given to `Flask.run`
        :return:
        """
        debug = self.enable_dev_tools(debug, dev_tools_serve_dev_bundles)
        self.server.run(port=port, debug=debug,
                        **flask_run_options)
