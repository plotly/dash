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
import pprint

from functools import wraps

import flask
from flask import Flask, Response
from flask_compress import Compress

import plotly
import dash_renderer

from .dependencies import Input, Output, State
from .resources import Scripts, Css
from .development.base_component import Component, ComponentRegistry
from . import exceptions
from ._utils import AttributeDict as _AttributeDict
from ._utils import interpolate_str as _interpolate
from ._utils import format_tag as _format_tag
from ._utils import generate_hash as _generate_hash
from ._utils import patch_collections_abc as _patch_collections_abc
from . import _watch
from ._utils import get_asset_path as _get_asset_path
from ._utils import create_callback_id as _create_callback_id
from ._configs import (get_combined_config, pathname_configs)

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
            {%renderer%}
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
_re_renderer_scripts = re.compile(r'{%renderer%}')

_re_index_entry_id = re.compile(r'id="react-entry-point"')
_re_index_config_id = re.compile(r'id="_dash-config"')
_re_index_scripts_id = re.compile(r'src=".*dash[-_]renderer.*"')
_re_renderer_scripts_id = re.compile(r'id="_dash-renderer')


class _NoUpdate(object):
    # pylint: disable=too-few-public-methods
    pass


# Singleton signal to not update an output, alternative to PreventUpdate
no_update = _NoUpdate()


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments, too-many-locals
class Dash(object):
    def __init__(
            self,
            name='__main__',
            server=None,
            static_folder='static',
            assets_folder='assets',
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

        self._assets_folder = os.path.join(
            flask.helpers.get_root_path(name),
            assets_folder,
        )
        self._assets_url_path = assets_url_path

        # allow users to supply their own flask server
        self.server = server or Flask(name, static_folder=static_folder)

        url_base_pathname, routes_pathname_prefix, requests_pathname_prefix = \
            pathname_configs(
                url_base_pathname,
                routes_pathname_prefix,
                requests_pathname_prefix
            )

        self.url_base_pathname = url_base_pathname
        self.config = _AttributeDict({
            'suppress_callback_exceptions': get_combined_config(
                'suppress_callback_exceptions',
                suppress_callback_exceptions,
                False),
            'routes_pathname_prefix': routes_pathname_prefix,
            'requests_pathname_prefix': requests_pathname_prefix,
            'include_assets_files': get_combined_config(
                'include_assets_files', include_assets_files, True),
            'assets_external_path': get_combined_config(
                'assets_external_path', assets_external_path, ''),
            'components_cache_max_age': int(get_combined_config(
                'components_cache_max_age',
                components_cache_max_age,
                2678400))
        })

        assets_blueprint_name = '{}{}'.format(
            self.config.routes_pathname_prefix.replace('/', '_'),
            'dash_assets'
        )

        self.server.register_blueprint(
            flask.Blueprint(
                assets_blueprint_name, name,
                static_folder=self._assets_folder,
                static_url_path='{}{}'.format(
                    self.config.routes_pathname_prefix,
                    assets_url_path.lstrip('/')
                )
            )
        )

        # list of dependencies
        self.callback_map = {}

        self._index_string = ''
        self.index_string = index_string
        self._meta_tags = meta_tags or []
        self._favicon = None

        # default renderer string
        self.renderer = 'var renderer = new DashRenderer();'

        if compress:
            # gzip
            Compress(self.server)

        @self.server.errorhandler(exceptions.PreventUpdate)
        def _handle_error(_):
            """Handle a halted callback and return an empty 204 response"""
            return '', 204

        # static files from the packages
        self.css = Css()
        self.scripts = Scripts()

        self._external_scripts = external_scripts or []
        self._external_stylesheets = external_stylesheets or []

        self.assets_ignore = assets_ignore

        self.registered_paths = collections.defaultdict(set)

        # urls
        self.routes = []

        prefix = self.config['routes_pathname_prefix']

        self._add_url('{}_dash-layout'.format(prefix), self.serve_layout)

        self._add_url('{}_dash-dependencies'.format(prefix), self.dependencies)

        self._add_url(
            '{}_dash-update-component'.format(prefix),
            self.dispatch,
            ['POST'])

        self._add_url(
            (
                '{}_dash-component-suites'
                '/<string:package_name>'
                '/<path:path_in_package_dist>'
            ).format(prefix),
            self.serve_component_suites)

        self._add_url('{}_dash-routes'.format(prefix), self.serve_routes)

        self._add_url(prefix, self.index)

        self._add_url('{}_reload-hash'.format(prefix), self.serve_reload_hash)

        # catch-all for front-end routes, used by dcc.Location
        self._add_url('{}<path:path>'.format(prefix), self.index)

        self._add_url(
            '{}_favicon.ico'.format(prefix),
            self._serve_default_favicon)

        self.server.before_first_request(self._setup_server)

        self._layout = None
        self._cached_layout = None
        self._dev_tools = _AttributeDict({
            'serve_dev_bundles': False,
            'hot_reload': False,
            'hot_reload_interval': 3000,
            'hot_reload_watch_interval': 0.5,
            'hot_reload_max_retry': 8,
            'ui': False,
            'props_check': False,
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
        if isinstance(self._layout, _patch_collections_abc('Callable')):
            self._cached_layout = self._layout()
        else:
            self._cached_layout = self._layout
        return self._cached_layout

    @layout.setter
    def layout(self, value):
        if (not isinstance(value, Component) and
                not isinstance(value, _patch_collections_abc('Callable'))):
            raise exceptions.NoLayoutException(
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
            raise exceptions.InvalidIndexException(
                'Did you forget to include {} in your index string ?'.format(
                    ', '.join('{%' + x + '%}' for x in missing)
                )
            )
        self._index_string = value

    def serve_layout(self):
        layout = self._layout_value()

        # TODO - Set browser cache limit - pass hash into frontend
        return flask.Response(
            json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder),
            mimetype='application/json'
        )

    def _config(self):
        config = {
            'url_base_pathname': self.url_base_pathname,
            'requests_pathname_prefix': self.config.requests_pathname_prefix,
            'ui': self._dev_tools.ui,
            'props_check': self._dev_tools.props_check,
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
            json.dumps(self.routes, cls=plotly.utils.PlotlyJSONEncoder),
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
                if not is_dynamic_resource:
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

    def _generate_renderer(self):
        return (
            '<script id="_dash-renderer" type="application/javascript">'
            '{}'
            '</script>'
        ).format(self.renderer)

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
            raise exceptions.DependencyException(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, list(self.registered_paths.keys())))

        if path_in_package_dist not in self.registered_paths[package_name]:
            raise exceptions.DependencyException(
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
        renderer = self._generate_renderer()
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
            scripts=scripts, app_entry=_app_entry, favicon=favicon,
            renderer=renderer)

        checks = (
            (_re_index_entry_id.search(index), '#react-entry-point'),
            (_re_index_config_id.search(index), '#_dash-configs'),
            (_re_index_scripts_id.search(index), 'dash-renderer'),
            (_re_renderer_scripts_id.search(index), 'new DashRenderer'),
        )
        missing = [missing for check, missing in checks if not check]

        if missing:
            plural = 's' if len(missing) > 1 else ''
            raise exceptions.InvalidIndexException(
                'Missing element{pl} {ids} in index.'.format(
                    ids=', '.join(missing),
                    pl=plural
                )
            )

        return index

    def interpolate_index(self,
                          metas='', title='', css='', config='',
                          scripts='', app_entry='', favicon='', renderer=''):
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
                            {renderer}
                            <div id="custom-footer">My custom footer</div>
                        </body>
                    </html>
                    '''.format(
                        app_entry=kwargs.get('app_entry'),
                        config=kwargs.get('config'),
                        scripts=kwargs.get('scripts'),
                        renderer=kwargs.get('renderer'))

        :param metas: Collected & formatted meta tags.
        :param title: The title of the app.
        :param css: Collected & formatted css dependencies as <link> tags.
        :param config: Configs needed by dash-renderer.
        :param scripts: Collected & formatted scripts tags.
        :param renderer: A script tag that instantiates the DashRenderer.
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
                            renderer=renderer,
                            app_entry=app_entry)

    def dependencies(self):
        return flask.jsonify([
            {
                'output': k,
                'inputs': v['inputs'],
                'state': v['state'],
                'clientside_function': v.get('clientside_function', None)
            } for k, v in self.callback_map.items()
        ])

    def _validate_callback(self, output, inputs, state):
        # pylint: disable=too-many-branches
        layout = self._cached_layout or self._layout_value()
        is_multi = isinstance(output, (list, tuple))

        for i in inputs:
            bad = None
            if is_multi:
                for o in output:
                    if o == i:
                        bad = o
            else:
                if output == i:
                    bad = output
            if bad:
                raise exceptions.SameInputOutputException(
                    'Same output and input: {}'.format(bad)
                )

        if is_multi:
            if len(set(output)) != len(output):
                raise exceptions.DuplicateCallbackOutput(
                    'Same output was used in a'
                    ' multi output callback!\n Duplicates:\n {}'.format(
                        ',\n'.join(
                            k for k, v in
                            ((str(x), output.count(x)) for x in output)
                            if v > 1
                        )
                    )
                )

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

        for args, obj, name in [(output if isinstance(output, (list, tuple))
                                 else [output],
                                 (Output, list, tuple),
                                 'Output'),
                                (inputs, Input, 'Input'),
                                (state, State, 'State')]:

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

                invalid_characters = ['.']
                if any(x in arg.component_id for x in invalid_characters):
                    raise exceptions.InvalidComponentIdError('''The element
                    `{}` contains {} in its ID.
                    Periods are not allowed in IDs right now.'''.format(
                        arg.component_id,
                        invalid_characters
                    ))

                if (not self.config.first('suppress_callback_exceptions',
                                          'supress_callback_exceptions') and
                        arg.component_id not in layout and
                        arg.component_id != getattr(layout, 'id', None)):
                    raise exceptions.NonExistentIdException('''
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
                        raise exceptions.NonExistentPropException('''
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

                    if hasattr(arg, 'component_event'):
                        raise exceptions.NonExistentEventException('''
                            Events have been removed.
                            Use the associated property instead.
                        ''')

        if state and not inputs:
            raise exceptions.MissingInputsException('''
                This callback has {} `State` {}
                but no `Input` elements.\n
                Without `Input` elements, this callback
                will never get called.\n
                (Subscribing to input components will cause the
                callback to be called whenever their values change.)
            '''.format(
                len(state),
                'elements' if len(state) > 1 else 'element'
            ).replace('    ', ''))

        callback_id = _create_callback_id(output)

        callbacks = set(itertools.chain(*(
            x[2:-2].split('...')
            if x.startswith('..')
            else [x]
            for x in self.callback_map
        )))
        ns = {
            'duplicates': set()
        }
        if is_multi:
            def duplicate_check():
                ns['duplicates'] = callbacks.intersection(
                    str(y) for y in output
                )
                return ns['duplicates']
        else:
            def duplicate_check():
                return callback_id in callbacks
        if duplicate_check():
            if is_multi:
                msg = '''
                Multi output {} contains an `Output` object
                that was already assigned.
                Duplicates:
                {}
                '''.format(
                    callback_id,
                    pprint.pformat(ns['duplicates'])
                )
            else:
                msg = '''
                You have already assigned a callback to the output
                with ID "{}" and property "{}". An output can only have
                a single callback function. Try combining your inputs and
                callback functions together into one function.
                '''.format(
                    output.component_id,
                    output.component_property
                ).replace('    ', '')
            raise exceptions.DuplicateCallbackOutput(msg)

    @staticmethod
    def _validate_callback_output(output_value, output):
        valid = [str, dict, int, float, type(None), Component]

        def _raise_invalid(bad_val, outer_val, bad_type, path, index=None,
                           toplevel=False):
            outer_id = "(id={:s})".format(outer_val.id) \
                if getattr(outer_val, 'id', False) else ''
            outer_type = type(outer_val).__name__
            raise exceptions.InvalidCallbackReturnValue('''
            The callback for `{output:s}`
            returned a {object:s} having type `{type:s}`
            which is not JSON serializable.

            {location_header:s}{location:s}
            and has string representation
            `{bad_val}`

            In general, Dash properties can only be
            dash components, strings, dictionaries, numbers, None,
            or lists of those.
            '''.format(
                output=repr(output),
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

    # pylint: disable=dangerous-default-value
    def clientside_callback(
            self, clientside_function, output, inputs=[], state=[]):
        """
        Create a callback that updates the output by calling a clientside
        (JavaScript) function instead of a Python function.

        Unlike `@app.calllback`, `clientside_callback` is not a decorator:
        it takes a
        `dash.dependencies.ClientsideFunction(namespace, function_name)`
        argument that describes which JavaScript function to call
        (Dash will look for the JavaScript function at
        `window[namespace][function_name]`).

        For example:
        ```
        app.clientside_callback(
            ClientsideFunction('my_clientside_library', 'my_function'),
            Output('my-div' 'children'),
            [Input('my-input', 'value'),
             Input('another-input', 'value')]
        )
        ```

        With this signature, Dash's front-end will call
        `window.my_clientside_library.my_function` with the current
        values of the `value` properties of the components
        `my-input` and `another-input` whenever those values change.

        Include a JavaScript file by including it your `assets/` folder.
        The file can be named anything but you'll need to assign the
        function's namespace to the `window`. For example, this file might
        look like:
        ```
        window.my_clientside_library = {
            my_function: function(input_value_1, input_value_2) {
                return (
                    parseFloat(input_value_1, 10) +
                    parseFloat(input_value_2, 10)
                );
            }
        }
        ```
        """
        self._validate_callback(output, inputs, state)
        callback_id = _create_callback_id(output)

        self.callback_map[callback_id] = {
            'inputs': [
                {'id': c.component_id, 'property': c.component_property}
                for c in inputs
            ],
            'state': [
                {'id': c.component_id, 'property': c.component_property}
                for c in state
            ],
            'clientside_function': {
                'namespace': clientside_function.namespace,
                'function_name': clientside_function.function_name
            }
        }

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
    def callback(self, output, inputs=[], state=[]):
        self._validate_callback(output, inputs, state)

        callback_id = _create_callback_id(output)
        multi = isinstance(output, (list, tuple))

        self.callback_map[callback_id] = {
            'inputs': [
                {'id': c.component_id, 'property': c.component_property}
                for c in inputs
            ],
            'state': [
                {'id': c.component_id, 'property': c.component_property}
                for c in state
            ],
        }

        def wrap_func(func):
            @wraps(func)
            def add_context(*args, **kwargs):
                output_value = func(*args, **kwargs)
                if multi:
                    if not isinstance(output_value, (list, tuple)):
                        raise exceptions.InvalidCallbackReturnValue(
                            'The callback {} is a multi-output.\n'
                            'Expected the output type to be a list'
                            ' or tuple but got {}.'.format(
                                callback_id, repr(output_value)
                            )
                        )

                    if not len(output_value) == len(output):
                        raise exceptions.InvalidCallbackReturnValue(
                            'Invalid number of output values for {}.\n'
                            ' Expected {} got {}'.format(
                                callback_id,
                                len(output),
                                len(output_value)
                            )
                        )

                    component_ids = collections.defaultdict(dict)
                    has_update = False
                    for i, o in enumerate(output):
                        val = output_value[i]
                        if val is not no_update:
                            has_update = True
                            o_id, o_prop = o.component_id, o.component_property
                            component_ids[o_id][o_prop] = val

                    if not has_update:
                        raise exceptions.PreventUpdate

                    response = {
                        'response': component_ids,
                        'multi': True
                    }
                else:
                    if output_value is no_update:
                        raise exceptions.PreventUpdate

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

                return jsonResponse

            self.callback_map[callback_id]['callback'] = add_context

            return add_context

        return wrap_func

    def dispatch(self):
        body = flask.request.get_json()
        inputs = body.get('inputs', [])
        state = body.get('state', [])
        output = body['output']

        args = []

        flask.g.input_values = input_values = {
            '{}.{}'.format(x['id'], x['property']): x.get('value')
            for x in inputs
        }
        flask.g.state_values = {
            '{}.{}'.format(x['id'], x['property']): x.get('value')
            for x in state
        }
        changed_props = body.get('changedPropIds')
        flask.g.triggered_inputs = [
            {'prop_id': x, 'value': input_values[x]}
            for x in changed_props
        ] if changed_props else []

        response = flask.g.dash_response = flask.Response(
            mimetype='application/json')

        for component_registration in self.callback_map[output]['inputs']:
            args.append([
                c.get('value', None) for c in inputs if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        for component_registration in self.callback_map[output]['state']:
            args.append([
                c.get('value', None) for c in state if
                c['property'] == component_registration['property'] and
                c['id'] == component_registration['id']
            ][0])

        response.set_data(self.callback_map[output]['callback'](*args))
        return response

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

    @staticmethod
    def _invalid_resources_handler(err):
        return err.args[0], 404

    def _serve_default_favicon(self):
        headers = {
            'Cache-Control': 'public, max-age={}'.format(
                self.config.components_cache_max_age)
        }
        return flask.Response(
            pkgutil.get_data('dash', 'favicon.ico'),
            headers=headers,
            content_type='image/x-icon',
        )

    def get_asset_url(self, path):
        asset = _get_asset_path(
            self.config.requests_pathname_prefix,
            path,
            self._assets_url_path.lstrip('/')
        )

        return asset

    def enable_dev_tools(self,
                         debug=False,
                         dev_tools_ui=None,
                         dev_tools_props_check=None,
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
            - DASH_UI
            - DASH_PROPS_CHECK
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
        :param dev_tools_ui: Switch the dev tools UI in debugger mode
        :type dev_tools_ui: bool
        :param dev_tools_props_check: Validate the properties of
            the Dash components
        :type dev_tools_props_check: bool
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
        debug = debug or get_combined_config('debug', None, debug)

        self._dev_tools['ui'] = get_combined_config(
            'ui', dev_tools_ui, default=debug
        )
        self._dev_tools['props_check'] = get_combined_config(
            'props_check', dev_tools_props_check, default=debug
        )
        self._dev_tools['serve_dev_bundles'] = get_combined_config(
            'serve_dev_bundles', dev_tools_serve_dev_bundles, default=debug)

        self._dev_tools['hot_reload'] = get_combined_config(
            'hot_reload', dev_tools_hot_reload, default=debug)
        self._dev_tools['hot_reload_interval'] = int(get_combined_config(
            'hot_reload_interval', dev_tools_hot_reload_interval, default=3000
        ))
        self._dev_tools['hot_reload_watch_interval'] = float(
            get_combined_config(
                'hot_reload_watch_interval',
                dev_tools_hot_reload_watch_interval,
                default=0.5
            )
        )
        self._dev_tools['hot_reload_max_retry'] = int(
            get_combined_config(
                'hot_reload_max_retry',
                dev_tools_hot_reload_max_retry,
                default=8
            )
        )
        self._dev_tools['silence_routes_logging'] = get_combined_config(
            'silence_routes_logging',
            dev_tools_silence_routes_logging,
            default=debug,
        )

        if self._dev_tools.silence_routes_logging:
            logging.getLogger('werkzeug').setLevel(logging.ERROR)
            self.logger.setLevel(logging.INFO)

        if self._dev_tools.hot_reload:
            self._reload_hash = _generate_hash()

            component_packages_dist = [
                os.path.dirname(package.path)
                if hasattr(package, 'path')
                else package.filename
                for package in (
                    pkgutil.find_loader(x) for x in
                    list(ComponentRegistry.registry) + ['dash_renderer']
                )
            ]

            self._watch_thread = threading.Thread(
                target=lambda: _watch.watch(
                    [self._assets_folder] + component_packages_dist,
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

        if self._assets_folder in filename:
            asset_path = os.path.relpath(
                filename, os.path.commonprefix([self._assets_folder, filename])
            ).replace('\\', '/').lstrip('/')

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
                   dev_tools_ui=None,
                   dev_tools_props_check=None,
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
        :param dev_tools_ui: Switch the dev tools UI in debugger mode
        :type dev_tools_ui: bool
        :param dev_tools_props_check: Validate the properties of
            the Dash components
        :type dev_tools_props_check: bool
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
            dev_tools_ui,
            dev_tools_props_check,
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

            self.logger.info('Debugger PIN: %s', debugger_pin)

        self.server.run(port=port, debug=debug, **flask_run_options)
