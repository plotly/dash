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
import re
import logging
import pprint

from functools import wraps
from textwrap import dedent

import flask
from flask_compress import Compress
from werkzeug.debug.tbtools import get_current_traceback

import plotly
import dash_renderer

from .dependencies import Input, Output, State
from .fingerprint import build_fingerprint, check_fingerprint
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
from ._utils import get_relative_path as _get_relative_path
from ._utils import strip_relative_path as _strip_relative_path
from ._configs import get_combined_config, pathname_configs
from .version import __version__

_default_index = """<!DOCTYPE html>
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
</html>"""

_app_entry = """
<div id="react-entry-point">
    <div class="_dash-loading">
        Loading...
    </div>
</div>
"""

_re_index_entry = re.compile(r"{%app_entry%}")
_re_index_config = re.compile(r"{%config%}")
_re_index_scripts = re.compile(r"{%scripts%}")
_re_renderer_scripts = re.compile(r"{%renderer%}")

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
    """Dash is a framework for building analytical web applications.
    No JavaScript required.

    If a parameter can be set by an environment variable, that is listed as:
        env: ``DASH_****``
    Values provided here take precedence over environment variables.

    :param name: The name Flask should use for your app. Even if you provide
        your own ``server``, ``name`` will be used to help find assets.
        Typically ``__name__`` (the magic global var, not a string) is the
        best value to use. Default ``'__main__'``, env: ``DASH_APP_NAME``
    :type name: string

    :param server: Sets the Flask server for your app. There are three options:
        ``True`` (default): Dash will create a new server
        ``False``: The server will be added later via ``app.init_app(server)``
            where ``server`` is a ``flask.Flask`` instance.
        ``flask.Flask``: use this pre-existing Flask server.
    :type server: boolean or flask.Flask

    :param assets_folder: a path, relative to the current working directory,
        for extra files to be used in the browser. Default ``'assets'``.
        All .js and .css files will be loaded immediately unless excluded by
        ``assets_ignore``, and other files such as images will be served if
        requested.
    :type assets_folder: string

    :param assets_url_path: The local urls for assets will be:
        ``requests_pathname_prefix + assets_url_path + '/' + asset_path``
        where ``asset_path`` is the path to a file inside ``assets_folder``.
        Default ``'assets'``.
    :type asset_url_path: string

    :param assets_ignore: A regex, as a string to pass to ``re.compile``, for
        assets to omit from immediate loading. Ignored files will still be
        served if specifically requested. You cannot use this to prevent access
        to sensitive files.
    :type assets_ignore: string

    :param assets_external_path: an absolute URL from which to load assets.
        Use with ``serve_locally=False``. Dash can still find js and css to
        automatically load if you also keep local copies in your assets
        folder that Dash can index, but external serving can improve
        performance and reduce load on the Dash server.
        env: ``DASH_ASSETS_EXTERNAL_PATH``
    :type assets_external_path: string

    :param include_assets_files: Default ``True``, set to ``False`` to prevent
        immediate loading of any assets. Assets will still be served if
        specifically requested. You cannot use this to prevent access
        to sensitive files. env: ``DASH_INCLUDE_ASSETS_FILES``
    :type include_assets_files: boolean

    :param url_base_pathname: A local URL prefix to use app-wide.
        Default ``'/'``. Both `requests_pathname_prefix` and
        `routes_pathname_prefix` default to `url_base_pathname`.
        env: ``DASH_URL_BASE_PATHNAME``
    :type url_base_pathname: string

    :param requests_pathname_prefix: A local URL prefix for file requests.
        Defaults to `url_base_pathname`, and must end with
        `routes_pathname_prefix`. env: ``DASH_REQUESTS_PATHNAME_PREFIX``
    :type requests_pathname_prefix: string

    :param routes_pathname_prefix: A local URL prefix for JSON requests.
        Defaults to ``url_base_pathname``, and must start and end
        with ``'/'``. env: ``DASH_ROUTES_PATHNAME_PREFIX``
    :type routes_pathname_prefix: string

    :param serve_locally: If ``True`` (default), assets and dependencies
        (Dash and Component js and css) will be served from local URLs.
        If ``False`` we will use CDN links where available.
    :type serve_locally: boolean

    :param compress: Use gzip to compress files and data served by Flask.
        Default ``True``
    :type compress: boolean

    :param meta_tags: html <meta> tags to be added to the index page.
        Each dict should have the attributes and values for one tag, eg:
        ``{'name': 'description', 'content': 'My App'}``
    :type meta_tags: list of dicts

    :param index_string: Override the standard Dash index page.
        Must contain the correct insertion markers to interpolate various
        content into it depending on the app config and components used.
        See https://dash.plot.ly/external-resources for details.
    :type index_string: string

    :param external_scripts: Additional JS files to load with the page.
        Each entry can be a string (the URL) or a dict with ``src`` (the URL)
        and optionally other ``<script>`` tag attributes such as ``integrity``
        and ``crossorigin``.
    :type external_scripts: list of strings or dicts

    :param external_stylesheets: Additional CSS files to load with the page.
        Each entry can be a string (the URL) or a dict with ``href`` (the URL)
        and optionally other ``<link>`` tag attributes such as ``rel``,
        ``integrity`` and ``crossorigin``.
    :type external_stylesheets: list of strings or dicts

    :param suppress_callback_exceptions: Default ``False``: check callbacks to
        ensure referenced IDs exist and props are valid. Set to ``True``
        if your layout is dynamic, to bypass these checks.
        env: ``DASH_SUPPRESS_CALLBACK_EXCEPTIONS``
    :type suppress_callback_exceptions: boolean

    :param show_undo_redo: Default ``False``, set to ``True`` to enable undo
        and redo buttons for stepping through the history of the app state.
    :type show_undo_redo: boolean

    :param plugins: Extend Dash functionality by passing a list of objects
        with a ``plug`` method, taking a single argument: this app, which will
        be called after the Flask server is attached.
    :type plugins: list of objects
    """

    def __init__(
        self,
        name=None,
        server=True,
        assets_folder="assets",
        assets_url_path="assets",
        assets_ignore="",
        assets_external_path=None,
        eager_loading=False,
        include_assets_files=True,
        url_base_pathname=None,
        requests_pathname_prefix=None,
        routes_pathname_prefix=None,
        serve_locally=True,
        compress=None,
        meta_tags=None,
        index_string=_default_index,
        external_scripts=None,
        external_stylesheets=None,
        suppress_callback_exceptions=None,
        show_undo_redo=False,
        plugins=None,
        **obsolete
    ):
        for key in obsolete:
            if key in ["components_cache_max_age", "static_folder"]:
                raise exceptions.ObsoleteKwargException(
                    key + " is no longer a valid keyword argument in Dash "
                    "since v1.0. See https://dash.plot.ly for details."
                )
            # any other kwarg mimic the built-in exception
            raise TypeError(
                "Dash() got an unexpected keyword argument '" + key + "'"
            )

        # We have 3 cases: server is either True (we create the server), False
        # (defer server creation) or a Flask app instance (we use their server)
        if isinstance(server, flask.Flask):
            self.server = server
            if name is None:
                name = getattr(server, "name", "__main__")
        elif isinstance(server, bool):
            name = name if name else "__main__"
            self.server = flask.Flask(name) if server else None
        else:
            raise ValueError("server must be a Flask app or a boolean")

        base_prefix, routes_prefix, requests_prefix = pathname_configs(
            url_base_pathname, routes_pathname_prefix, requests_pathname_prefix
        )

        self.config = _AttributeDict(
            name=name,
            assets_folder=os.path.join(
                flask.helpers.get_root_path(name), assets_folder
            ),
            assets_url_path=assets_url_path,
            assets_ignore=assets_ignore,
            assets_external_path=get_combined_config(
                "assets_external_path", assets_external_path, ""
            ),
            eager_loading=eager_loading,
            include_assets_files=get_combined_config(
                "include_assets_files", include_assets_files, True
            ),
            url_base_pathname=base_prefix,
            routes_pathname_prefix=routes_prefix,
            requests_pathname_prefix=requests_prefix,
            serve_locally=serve_locally,
            compress=get_combined_config(
                "compress", compress, True
            ),
            meta_tags=meta_tags or [],
            external_scripts=external_scripts or [],
            external_stylesheets=external_stylesheets or [],
            suppress_callback_exceptions=get_combined_config(
                "suppress_callback_exceptions",
                suppress_callback_exceptions,
                False,
            ),
            show_undo_redo=show_undo_redo,
        )
        self.config.set_read_only(
            [
                "name",
                "assets_folder",
                "assets_url_path",
                "eager_loading",
                "url_base_pathname",
                "routes_pathname_prefix",
                "requests_pathname_prefix",
                "serve_locally",
                "compress",
            ],
            "Read-only: can only be set in the Dash constructor",
        )
        self.config.finalize(
            "Invalid config key. Some settings are only available "
            "via the Dash constructor"
        )

        # list of dependencies
        self.callback_map = {}

        # list of inline scripts
        self._inline_scripts = []

        # index_string has special setter so can't go in config
        self._index_string = ""
        self.index_string = index_string
        self._favicon = None

        # default renderer string
        self.renderer = "var renderer = new DashRenderer();"

        # static files from the packages
        self.css = Css(serve_locally)
        self.scripts = Scripts(serve_locally, eager_loading)

        self.registered_paths = collections.defaultdict(set)

        # urls
        self.routes = []

        self._layout = None
        self._cached_layout = None

        self._setup_dev_tools()
        self._hot_reload = _AttributeDict(
            hash=None,
            hard=False,
            lock=threading.RLock(),
            watch_thread=None,
            changed_assets=[],
        )

        self._assets_files = []

        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))

        if isinstance(plugins, _patch_collections_abc("Iterable")):
            for plugin in plugins:
                plugin.plug(self)

        if self.server is not None:
            self.init_app()

    def init_app(self, app=None):
        """Initialize the parts of Dash that require a flask app."""
        config = self.config

        if app is not None:
            self.server = app

        assets_blueprint_name = "{}{}".format(
            config.routes_pathname_prefix.replace("/", "_"), "dash_assets"
        )

        self.server.register_blueprint(
            flask.Blueprint(
                assets_blueprint_name,
                config.name,
                static_folder=self.config.assets_folder,
                static_url_path="{}{}".format(
                    config.routes_pathname_prefix,
                    self.config.assets_url_path.lstrip("/"),
                ),
            )
        )

        if config.compress:
            # gzip
            Compress(self.server)

        @self.server.errorhandler(exceptions.PreventUpdate)
        def _handle_error(_):
            """Handle a halted callback and return an empty 204 response."""
            return "", 204

        prefix = config.routes_pathname_prefix

        self.server.before_first_request(self._setup_server)

        # add a handler for components suites errors to return 404
        self.server.errorhandler(exceptions.InvalidResourceError)(
            self._invalid_resources_handler
        )

        self._add_url("{}_dash-layout".format(prefix), self.serve_layout)

        self._add_url("{}_dash-dependencies".format(prefix), self.dependencies)

        self._add_url(
            "{}_dash-update-component".format(prefix), self.dispatch, ["POST"]
        )

        self._add_url(
            (
                "{}_dash-component-suites"
                "/<string:package_name>"
                "/<path:path_in_package_dist>"
            ).format(prefix),
            self.serve_component_suites,
        )

        self._add_url("{}_dash-routes".format(prefix), self.serve_routes)

        self._add_url(prefix, self.index)

        self._add_url("{}_reload-hash".format(prefix), self.serve_reload_hash)

        # catch-all for front-end routes, used by dcc.Location
        self._add_url("{}<path:path>".format(prefix), self.index)

        self._add_url(
            "{}_favicon.ico".format(prefix), self._serve_default_favicon
        )

    def _add_url(self, name, view_func, methods=("GET",)):
        self.server.add_url_rule(
            name, view_func=view_func, endpoint=name, methods=list(methods)
        )

        # record the url in Dash.routes so that it can be accessed later
        # e.g. for adding authentication with flask_login
        self.routes.append(name)

    @property
    def layout(self):
        return self._layout

    def _layout_value(self):
        if isinstance(self._layout, _patch_collections_abc("Callable")):
            self._cached_layout = self._layout()
        else:
            self._cached_layout = self._layout
        return self._cached_layout

    @layout.setter
    def layout(self, value):
        if not isinstance(value, Component) and not isinstance(
            value, _patch_collections_abc("Callable")
        ):
            raise exceptions.NoLayoutException(
                "Layout must be a dash component "
                "or a function that returns "
                "a dash component."
            )

        self._cached_layout = None
        self._layout = value

    @property
    def index_string(self):
        return self._index_string

    @index_string.setter
    def index_string(self, value):
        checks = (
            (_re_index_entry.search(value), "app_entry"),
            (_re_index_config.search(value), "config"),
            (_re_index_scripts.search(value), "scripts"),
        )
        missing = [missing for check, missing in checks if not check]
        if missing:
            raise exceptions.InvalidIndexException(
                "Did you forget to include {} in your index string ?".format(
                    ", ".join("{%" + x + "%}" for x in missing)
                )
            )
        self._index_string = value

    def serve_layout(self):
        layout = self._layout_value()

        # TODO - Set browser cache limit - pass hash into frontend
        return flask.Response(
            json.dumps(layout, cls=plotly.utils.PlotlyJSONEncoder),
            mimetype="application/json",
        )

    def _config(self):
        # pieces of config needed by the front end
        config = {
            "url_base_pathname": self.config.url_base_pathname,
            "requests_pathname_prefix": self.config.requests_pathname_prefix,
            "ui": self._dev_tools.ui,
            "props_check": self._dev_tools.props_check,
            "show_undo_redo": self.config.show_undo_redo,
        }
        if self._dev_tools.hot_reload:
            config["hot_reload"] = {
                # convert from seconds to msec as used by js `setInterval`
                "interval": int(self._dev_tools.hot_reload_interval * 1000),
                "max_retry": self._dev_tools.hot_reload_max_retry,
            }
        return config

    def serve_reload_hash(self):
        _reload = self._hot_reload
        with _reload.lock:
            hard = _reload.hard
            changed = _reload.changed_assets
            _hash = _reload.hash
            _reload.hard = False
            _reload.changed_assets = []

        return flask.jsonify(
            {
                "reloadHash": _hash,
                "hard": hard,
                "packages": list(self.registered_paths.keys()),
                "files": list(changed),
            }
        )

    def serve_routes(self):
        return flask.Response(
            json.dumps(self.routes, cls=plotly.utils.PlotlyJSONEncoder),
            mimetype="application/json",
        )

    def _collect_and_register_resources(self, resources):
        # now needs the app context.
        # template in the necessary component suite JS bundles
        # add the version number of the package as a query parameter
        # for cache busting
        def _relative_url_path(relative_package_path="", namespace=""):

            module_path = os.path.join(
                os.path.dirname(sys.modules[namespace].__file__),
                relative_package_path,
            )

            modified = int(os.stat(module_path).st_mtime)

            return "{}_dash-component-suites/{}/{}".format(
                self.config.requests_pathname_prefix,
                namespace,
                build_fingerprint(
                    relative_package_path,
                    importlib.import_module(namespace).__version__,
                    modified,
                ),
            )

        srcs = []
        for resource in resources:
            is_dynamic_resource = resource.get("dynamic", False)

            if "relative_package_path" in resource:
                paths = resource["relative_package_path"]
                paths = [paths] if isinstance(paths, str) else paths

                for rel_path in paths:
                    self.registered_paths[resource["namespace"]].add(rel_path)

                    if not is_dynamic_resource:
                        srcs.append(
                            _relative_url_path(
                                relative_package_path=rel_path,
                                namespace=resource["namespace"],
                            )
                        )
            elif "external_url" in resource:
                if not is_dynamic_resource:
                    if isinstance(resource["external_url"], str):
                        srcs.append(resource["external_url"])
                    else:
                        srcs += resource["external_url"]
            elif "absolute_path" in resource:
                raise Exception(
                    "Serving files from absolute_path isn't supported yet"
                )
            elif "asset_path" in resource:
                static_url = self.get_asset_url(resource["asset_path"])
                # Add a cache-busting query param
                static_url += "?m={}".format(resource["ts"])
                srcs.append(static_url)
        return srcs

    def _generate_css_dist_html(self):
        external_links = self.config.external_stylesheets
        links = self._collect_and_register_resources(self.css.get_all_css())

        return "\n".join(
            [
                _format_tag("link", link, opened=True)
                if isinstance(link, dict)
                else '<link rel="stylesheet" href="{}">'.format(link)
                for link in (external_links + links)
            ]
        )

    def _generate_scripts_html(self):
        # Dash renderer has dependencies like React which need to be rendered
        # before every other script. However, the dash renderer bundle
        # itself needs to be rendered after all of the component's
        # scripts have rendered.
        # The rest of the scripts can just be loaded after React but before
        # dash renderer.
        # pylint: disable=protected-access

        mode = "dev" if self._dev_tools["props_check"] is True else "prod"

        deps = []
        for js_dist_dependency in dash_renderer._js_dist_dependencies:
            dep = {}
            for key, value in js_dist_dependency.items():
                dep[key] = value[mode] if isinstance(value, dict) else value

            deps.append(dep)

        dev = self._dev_tools.serve_dev_bundles
        srcs = (
            self._collect_and_register_resources(
                self.scripts._resources._filter_resources(
                    deps, dev_bundles=dev
                )
            )
            + self.config.external_scripts
            + self._collect_and_register_resources(
                self.scripts.get_all_scripts(dev_bundles=dev)
                + self.scripts._resources._filter_resources(
                    dash_renderer._js_dist, dev_bundles=dev
                )
            )
        )

        return "\n".join(
            [
                _format_tag("script", src)
                if isinstance(src, dict)
                else '<script src="{}"></script>'.format(src)
                for src in srcs
            ] +
            [
                '<script>{}</script>'.format(src)
                for src in self._inline_scripts
            ]
        )

    def _generate_config_html(self):
        return (
            '<script id="_dash-config" type="application/json">'
            "{}"
            "</script>"
        ).format(json.dumps(self._config()))

    def _generate_renderer(self):
        return (
            '<script id="_dash-renderer" type="application/javascript">'
            "{}"
            "</script>"
        ).format(self.renderer)

    def _generate_meta_html(self):
        meta_tags = self.config.meta_tags
        has_ie_compat = any(
            x.get("http-equiv", "") == "X-UA-Compatible" for x in meta_tags
        )
        has_charset = any("charset" in x for x in meta_tags)

        tags = []
        if not has_ie_compat:
            tags.append(
                '<meta http-equiv="X-UA-Compatible" content="IE=edge">'
            )
        if not has_charset:
            tags.append('<meta charset="UTF-8">')

        tags += [_format_tag("meta", x, opened=True) for x in meta_tags]

        return "\n      ".join(tags)

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, path_in_package_dist):
        path_in_package_dist, has_fingerprint = check_fingerprint(
            path_in_package_dist
        )

        if package_name not in self.registered_paths:
            raise exceptions.DependencyException(
                "Error loading dependency.\n"
                '"{}" is not a registered library.\n'
                "Registered libraries are: {}".format(
                    package_name, list(self.registered_paths.keys())
                )
            )

        if path_in_package_dist not in self.registered_paths[package_name]:
            raise exceptions.DependencyException(
                '"{}" is registered but the path requested is not valid.\n'
                'The path requested: "{}"\n'
                "List of registered paths: {}".format(
                    package_name, path_in_package_dist, self.registered_paths
                )
            )

        mimetype = (
            {
                "js": "application/javascript",
                "css": "text/css",
                "map": "application/json",
            }
        )[path_in_package_dist.split(".")[-1]]

        package = sys.modules[package_name]
        self.logger.debug(
            "serving -- package: %s[%s] resource: %s => location: %s",
            package_name,
            package.__version__,
            path_in_package_dist,
            package.__path__,
        )

        response = flask.Response(
            pkgutil.get_data(package_name, path_in_package_dist),
            mimetype=mimetype,
        )

        if has_fingerprint:
            # Fingerprinted resources are good forever (1 year)
            # No need for ETag as the fingerprint changes with each build
            response.cache_control.max_age = 31536000  # 1 year
        else:
            # Non-fingerprinted resources are given an ETag that
            # will be used / check on future requests
            response.add_etag()
            tag = response.get_etag()[0]

            request_etag = flask.request.headers.get('If-None-Match')

            if '"{}"'.format(tag) == request_etag:
                response = flask.Response(None, status=304)

        return response

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta_html()
        renderer = self._generate_renderer()
        title = getattr(self, "title", "Dash")

        if self._favicon:
            favicon_mod_time = os.path.getmtime(
                os.path.join(self.config.assets_folder, self._favicon)
            )
            favicon_url = self.get_asset_url(self._favicon) + "?m={}".format(
                favicon_mod_time
            )
        else:
            favicon_url = "{}_favicon.ico?v={}".format(
                self.config.requests_pathname_prefix, __version__
            )

        favicon = _format_tag(
            "link",
            {"rel": "icon", "type": "image/x-icon", "href": favicon_url},
            opened=True,
        )

        index = self.interpolate_index(
            metas=metas,
            title=title,
            css=css,
            config=config,
            scripts=scripts,
            app_entry=_app_entry,
            favicon=favicon,
            renderer=renderer,
        )

        checks = (
            (_re_index_entry_id.search(index), "#react-entry-point"),
            (_re_index_config_id.search(index), "#_dash-configs"),
            (_re_index_scripts_id.search(index), "dash-renderer"),
            (_re_renderer_scripts_id.search(index), "new DashRenderer"),
        )
        missing = [missing for check, missing in checks if not check]

        if missing:
            plural = "s" if len(missing) > 1 else ""
            raise exceptions.InvalidIndexException(
                "Missing element{pl} {ids} in index.".format(
                    ids=", ".join(missing), pl=plural
                )
            )

        return index

    def interpolate_index(
        self,
        metas="",
        title="",
        css="",
        config="",
        scripts="",
        app_entry="",
        favicon="",
        renderer="",
    ):
        """Called to create the initial HTML string that is loaded on page.
        Override this method to provide you own custom HTML.

        :Example:

            class MyDash(dash.Dash):
                def interpolate_index(self, **kwargs):
                    return '''<!DOCTYPE html>
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
                    </html>'''.format(app_entry=kwargs.get('app_entry'),
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
        return _interpolate(
            self.index_string,
            metas=metas,
            title=title,
            css=css,
            config=config,
            scripts=scripts,
            favicon=favicon,
            renderer=renderer,
            app_entry=app_entry,
        )

    def dependencies(self):
        return flask.jsonify(
            [
                {
                    "output": k,
                    "inputs": v["inputs"],
                    "state": v["state"],
                    "clientside_function": v.get("clientside_function", None),
                }
                for k, v in self.callback_map.items()
            ]
        )

    def _validate_callback(self, output, inputs, state):
        # pylint: disable=too-many-branches
        layout = self._cached_layout or self._layout_value()
        is_multi = isinstance(output, (list, tuple))

        if layout is None and not self.config.suppress_callback_exceptions:
            # Without a layout, we can't do validation on the IDs and
            # properties of the elements in the callback.
            raise exceptions.LayoutIsNotDefined(
                dedent(
                    """
                Attempting to assign a callback to the application but
                the `layout` property has not been assigned.
                Assign the `layout` property before assigning callbacks.
                Alternatively, suppress this warning by setting
                `suppress_callback_exceptions=True`
            """
                )
            )

        outputs = output if is_multi else [output]
        for args, obj, name in [
            (outputs, Output, "Output"),
            (inputs, Input, "Input"),
            (state, State, "State"),
        ]:

            if not isinstance(args, (list, tuple)):
                raise exceptions.IncorrectTypeException(
                    "The {} argument `{}` must be "
                    "a list or tuple of `dash.dependencies.{}`s.".format(
                        name.lower(), str(args), name
                    )
                )

            for arg in args:
                if not isinstance(arg, obj):
                    raise exceptions.IncorrectTypeException(
                        "The {} argument `{}` must be "
                        "of type `dash.{}`.".format(
                            name.lower(), str(arg), name
                        )
                    )

                invalid_characters = ["."]
                if any(x in arg.component_id for x in invalid_characters):
                    raise exceptions.InvalidComponentIdError(
                        "The element `{}` contains {} in its ID. "
                        "Periods are not allowed in IDs.".format(
                            arg.component_id, invalid_characters
                        )
                    )

                if not self.config.suppress_callback_exceptions:
                    layout_id = getattr(layout, "id", None)
                    arg_id = arg.component_id
                    arg_prop = getattr(arg, "component_property", None)
                    if arg_id not in layout and arg_id != layout_id:
                        all_ids = [k for k in layout]
                        if layout_id:
                            all_ids.append(layout_id)
                        raise exceptions.NonExistentIdException(
                            dedent(
                                """
                            Attempting to assign a callback to the
                            component with the id "{0}" but no
                            components with id "{0}" exist in the
                            app\'s layout.\n\n
                            Here is a list of IDs in layout:\n{1}\n\n
                            If you are assigning callbacks to components
                            that are generated by other callbacks
                            (and therefore not in the initial layout), then
                            you can suppress this exception by setting
                            `suppress_callback_exceptions=True`.
                        """
                            ).format(arg_id, all_ids)
                        )

                    component = (
                        layout if layout_id == arg_id else layout[arg_id]
                    )

                    if (
                        arg_prop
                        and arg_prop not in component.available_properties
                        and not any(
                            arg_prop.startswith(w)
                            for w in component.available_wildcard_properties
                        )
                    ):
                        raise exceptions.NonExistentPropException(
                            dedent(
                                """
                            Attempting to assign a callback with
                            the property "{0}" but the component
                            "{1}" doesn't have "{0}" as a property.\n
                            Here are the available properties in "{1}":
                            {2}
                        """
                            ).format(
                                arg_prop,
                                arg_id,
                                component.available_properties,
                            )
                        )

                    if hasattr(arg, "component_event"):
                        raise exceptions.NonExistentEventException(
                            dedent(
                                """
                            Events have been removed.
                            Use the associated property instead.
                        """
                            )
                        )

        if state and not inputs:
            raise exceptions.MissingInputsException(
                dedent(
                    """
                This callback has {} `State` {}
                but no `Input` elements.\n
                Without `Input` elements, this callback
                will never get called.\n
                (Subscribing to input components will cause the
                callback to be called whenever their values change.)
            """
                ).format(
                    len(state), "elements" if len(state) > 1 else "element"
                )
            )

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
                    "Same output and input: {}".format(bad)
                )

        if is_multi:
            if len(set(output)) != len(output):
                raise exceptions.DuplicateCallbackOutput(
                    "Same output was used more than once in a "
                    "multi output callback!\n Duplicates:\n {}".format(
                        ",\n".join(
                            k
                            for k, v in (
                                (str(x), output.count(x)) for x in output
                            )
                            if v > 1
                        )
                    )
                )

        callback_id = _create_callback_id(output)

        callbacks = set(
            itertools.chain(
                *(
                    x[2:-2].split("...") if x.startswith("..") else [x]
                    for x in self.callback_map
                )
            )
        )
        ns = {"duplicates": set()}
        if is_multi:

            def duplicate_check():
                ns["duplicates"] = callbacks.intersection(
                    str(y) for y in output
                )
                return ns["duplicates"]

        else:

            def duplicate_check():
                return callback_id in callbacks

        if duplicate_check():
            if is_multi:
                msg = dedent(
                    """
                Multi output {} contains an `Output` object
                that was already assigned.
                Duplicates:
                {}
                """
                ).format(callback_id, pprint.pformat(ns["duplicates"]))
            else:
                msg = dedent(
                    """
                You have already assigned a callback to the output
                with ID "{}" and property "{}". An output can only have
                a single callback function. Try combining your inputs and
                callback functions together into one function.
                """
                ).format(output.component_id, output.component_property)
            raise exceptions.DuplicateCallbackOutput(msg)

    @staticmethod
    def _validate_callback_output(output_value, output):
        valid = [str, dict, int, float, type(None), Component]

        def _raise_invalid(
            bad_val, outer_val, path, index=None, toplevel=False
        ):
            bad_type = type(bad_val).__name__
            outer_id = (
                "(id={:s})".format(outer_val.id)
                if getattr(outer_val, "id", False)
                else ""
            )
            outer_type = type(outer_val).__name__
            raise exceptions.InvalidCallbackReturnValue(
                dedent(
                    """
            The callback for `{output:s}`
            returned a {object:s} having type `{type:s}`
            which is not JSON serializable.

            {location_header:s}{location:s}
            and has string representation
            `{bad_val}`

            In general, Dash properties can only be
            dash components, strings, dictionaries, numbers, None,
            or lists of those.
            """
                ).format(
                    output=repr(output),
                    object="tree with one value" if not toplevel else "value",
                    type=bad_type,
                    location_header=(
                        "The value in question is located at"
                        if not toplevel
                        else "The value in question is either the only value "
                        "returned,\nor is in the top level of the returned "
                        "list,"
                    ),
                    location=(
                        "\n"
                        + (
                            "[{:d}] {:s} {:s}".format(
                                index, outer_type, outer_id
                            )
                            if index is not None
                            else ("[*] " + outer_type + " " + outer_id)
                        )
                        + "\n"
                        + path
                        + "\n"
                    )
                    if not toplevel
                    else "",
                    bad_val=bad_val,
                )
            )

        def _value_is_valid(val):
            return (
                # pylint: disable=unused-variable
                any([isinstance(val, x) for x in valid])
                or type(val).__name__ == "unicode"
            )

        def _validate_value(val, index=None):
            # val is a Component
            if isinstance(val, Component):
                # pylint: disable=protected-access
                for p, j in val._traverse_with_paths():
                    # check each component value in the tree
                    if not _value_is_valid(j):
                        _raise_invalid(
                            bad_val=j, outer_val=val, path=p, index=index
                        )

                    # Children that are not of type Component or
                    # list/tuple not returned by traverse
                    child = getattr(j, "children", None)
                    if not isinstance(
                        child, (tuple, collections.MutableSequence)
                    ):
                        if child and not _value_is_valid(child):
                            _raise_invalid(
                                bad_val=child,
                                outer_val=val,
                                path=p + "\n" + "[*] " + type(child).__name__,
                                index=index,
                            )

                # Also check the child of val, as it will not be returned
                child = getattr(val, "children", None)
                if not isinstance(child, (tuple, collections.MutableSequence)):
                    if child and not _value_is_valid(child):
                        _raise_invalid(
                            bad_val=child,
                            outer_val=val,
                            path=type(child).__name__,
                            index=index,
                        )

            # val is not a Component, but is at the top level of tree
            else:
                if not _value_is_valid(val):
                    _raise_invalid(
                        bad_val=val,
                        outer_val=type(val).__name__,
                        path="",
                        index=index,
                        toplevel=True,
                    )

        if isinstance(output_value, list):
            for i, val in enumerate(output_value):
                _validate_value(val, index=i)
        else:
            _validate_value(output_value)

    # pylint: disable=dangerous-default-value
    def clientside_callback(
        self, clientside_function, output, inputs=[], state=[]
    ):
        """Create a callback that updates the output by calling a clientside
        (JavaScript) function instead of a Python function.

        Unlike `@app.calllback`, `clientside_callback` is not a decorator:
        it takes either a
        `dash.dependencies.ClientsideFunction(namespace, function_name)`
        argument that describes which JavaScript function to call
        (Dash will look for the JavaScript function at
        `window.dash_clientside[namespace][function_name]`), or it may take
        a string argument that contains the clientside function source.

        For example, when using a `dash.dependencies.ClientsideFunction`:
        ```
        app.clientside_callback(
            ClientsideFunction('my_clientside_library', 'my_function'),
            Output('my-div' 'children'),
            [Input('my-input', 'value'),
             Input('another-input', 'value')]
        )
        ```

        With this signature, Dash's front-end will call
        `window.dash_clientside.my_clientside_library.my_function` with the
        current values of the `value` properties of the components `my-input`
        and `another-input` whenever those values change.

        Include a JavaScript file by including it your `assets/` folder. The
        file can be named anything but you'll need to assign the function's
        namespace to the `window.dash_clientside` namespace. For example,
        this file might look:
        ```
        window.dash_clientside = window.dash_clientside || {};
        window.dash_clientside.my_clientside_library = {
            my_function: function(input_value_1, input_value_2) {
                return (
                    parseFloat(input_value_1, 10) +
                    parseFloat(input_value_2, 10)
                );
            }
        }
        ```

        Alternatively, you can pass the JavaScript source directly to
        `clientside_callback`. In this case, the same example would look like:
        ```
        app.clientside_callback(
            '''
            function(input_value_1, input_value_2) {
                return (
                    parseFloat(input_value_1, 10) +
                    parseFloat(input_value_2, 10)
                );
            }
            ''',
            Output('my-div' 'children'),
            [Input('my-input', 'value'),
             Input('another-input', 'value')]
        )
        ```
        """
        self._validate_callback(output, inputs, state)
        callback_id = _create_callback_id(output)

        # If JS source is explicitly given, create a namespace and function
        # name, then inject the code.
        if isinstance(clientside_function, str):

            out0 = output
            if isinstance(output, (list, tuple)):
                out0 = output[0]

            namespace = '_dashprivate_{}'.format(out0.component_id)
            function_name = '{}'.format(out0.component_property)

            self._inline_scripts.append(
                """
                var clientside = window.dash_clientside = window.dash_clientside || {{}};
                var ns = clientside["{0}"] = clientside["{0}"] || {{}};
                ns["{1}"] = {2};
                """.format(namespace.replace('"', '\\"'),
                           function_name.replace('"', '\\"'),
                           clientside_function)
            )

        # Callback is stored in an external asset.
        else:
            namespace = clientside_function.namespace
            function_name = clientside_function.function_name

        self.callback_map[callback_id] = {
            "inputs": [
                {"id": c.component_id, "property": c.component_property}
                for c in inputs
            ],
            "state": [
                {"id": c.component_id, "property": c.component_property}
                for c in state
            ],
            "clientside_function": {
                "namespace": namespace,
                "function_name": function_name,
            },
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
            "inputs": [
                {"id": c.component_id, "property": c.component_property}
                for c in inputs
            ],
            "state": [
                {"id": c.component_id, "property": c.component_property}
                for c in state
            ],
        }

        def wrap_func(func):
            @wraps(func)
            def add_context(*args, **kwargs):
                # don't touch the comment on the next line - used by debugger
                output_value = func(*args, **kwargs)  # %% callback invoked %%
                if multi:
                    if not isinstance(output_value, (list, tuple)):
                        raise exceptions.InvalidCallbackReturnValue(
                            "The callback {} is a multi-output.\n"
                            "Expected the output type to be a list"
                            " or tuple but got {}.".format(
                                callback_id, repr(output_value)
                            )
                        )

                    if not len(output_value) == len(output):
                        raise exceptions.InvalidCallbackReturnValue(
                            "Invalid number of output values for {}.\n"
                            " Expected {} got {}".format(
                                callback_id, len(output), len(output_value)
                            )
                        )

                    component_ids = collections.defaultdict(dict)
                    has_update = False
                    for i, o in enumerate(output):
                        val = output_value[i]
                        if not isinstance(val, _NoUpdate):
                            has_update = True
                            o_id, o_prop = o.component_id, o.component_property
                            component_ids[o_id][o_prop] = val

                    if not has_update:
                        raise exceptions.PreventUpdate

                    response = {"response": component_ids, "multi": True}
                else:
                    if isinstance(output_value, _NoUpdate):
                        raise exceptions.PreventUpdate

                    response = {
                        "response": {
                            "props": {output.component_property: output_value}
                        }
                    }

                try:
                    jsonResponse = json.dumps(
                        response, cls=plotly.utils.PlotlyJSONEncoder
                    )
                except TypeError:
                    self._validate_callback_output(output_value, output)
                    raise exceptions.InvalidCallbackReturnValue(
                        dedent(
                            """
                    The callback for property `{property:s}`
                    of component `{id:s}` returned a value
                    which is not JSON serializable.

                    In general, Dash properties can only be
                    dash components, strings, dictionaries, numbers, None,
                    or lists of those.
                    """
                        ).format(
                            property=output.component_property,
                            id=output.component_id,
                        )
                    )

                return jsonResponse

            self.callback_map[callback_id]["callback"] = add_context

            return add_context

        return wrap_func

    def dispatch(self):
        body = flask.request.get_json()
        inputs = body.get("inputs", [])
        state = body.get("state", [])
        output = body["output"]

        args = []

        flask.g.input_values = input_values = {
            "{}.{}".format(x["id"], x["property"]): x.get("value")
            for x in inputs
        }
        flask.g.state_values = {
            "{}.{}".format(x["id"], x["property"]): x.get("value")
            for x in state
        }
        changed_props = body.get("changedPropIds")
        flask.g.triggered_inputs = (
            [{"prop_id": x, "value": input_values[x]} for x in changed_props]
            if changed_props
            else []
        )

        response = flask.g.dash_response = flask.Response(
            mimetype="application/json"
        )

        for component_registration in self.callback_map[output]["inputs"]:
            args.append(
                [
                    c.get("value", None)
                    for c in inputs
                    if c["property"] == component_registration["property"]
                    and c["id"] == component_registration["id"]
                ][0]
            )

        for component_registration in self.callback_map[output]["state"]:
            args.append(
                [
                    c.get("value", None)
                    for c in state
                    if c["property"] == component_registration["property"]
                    and c["id"] == component_registration["id"]
                ][0]
            )

        response.set_data(self.callback_map[output]["callback"](*args))
        return response

    def _validate_layout(self):
        if self.layout is None:
            raise exceptions.NoLayoutException(
                "The layout was `None` "
                "at the time that `run_server` was called. "
                "Make sure to set the `layout` attribute of your application "
                "before running the server."
            )

        to_validate = self._layout_value()

        layout_id = getattr(self.layout, "id", None)

        component_ids = {layout_id} if layout_id else set()
        # pylint: disable=protected-access
        for component in to_validate._traverse():
            component_id = getattr(component, "id", None)
            if component_id and component_id in component_ids:
                raise exceptions.DuplicateIdError(
                    "Duplicate component id found"
                    " in the initial layout: `{}`".format(component_id)
                )
            component_ids.add(component_id)

    def _setup_server(self):
        # Apply _force_eager_loading overrides from modules
        eager_loading = self.config.eager_loading
        for module_name in ComponentRegistry.registry:
            module = sys.modules[module_name]
            eager = getattr(module, '_force_eager_loading', False)
            eager_loading = eager_loading or eager

        # Update eager_loading settings
        self.scripts.config.eager_loading = eager_loading

        if self.config.include_assets_files:
            self._walk_assets_directory()

        self._validate_layout()

        self._generate_scripts_html()
        self._generate_css_dist_html()

    def _add_assets_resource(self, url_path, file_path):
        res = {"asset_path": url_path, "filepath": file_path}
        if self.config.assets_external_path:
            res["external_url"] = "{}{}".format(
                self.config.assets_external_path, url_path
            )
        self._assets_files.append(file_path)
        return res

    def _walk_assets_directory(self):
        walk_dir = self.config.assets_folder
        slash_splitter = re.compile(r"[\\/]+")
        ignore_str = self.config.assets_ignore
        ignore_filter = re.compile(ignore_str) if ignore_str else None

        for current, _, files in os.walk(walk_dir):
            if current == walk_dir:
                base = ""
            else:
                s = current.replace(walk_dir, "").lstrip("\\").lstrip("/")
                splitted = slash_splitter.split(s)
                if len(splitted) > 1:
                    base = "/".join(slash_splitter.split(s))
                else:
                    base = splitted[0]

            if ignore_filter:
                files_gen = (x for x in files if not ignore_filter.search(x))
            else:
                files_gen = files

            for f in sorted(files_gen):
                path = "/".join([base, f]) if base else f

                full = os.path.join(current, f)

                if f.endswith("js"):
                    self.scripts.append_script(
                        self._add_assets_resource(path, full)
                    )
                elif f.endswith("css"):
                    self.css.append_css(self._add_assets_resource(path, full))
                elif f == "favicon.ico":
                    self._favicon = path

    @staticmethod
    def _invalid_resources_handler(err):
        return err.args[0], 404

    @staticmethod
    def _serve_default_favicon():
        return flask.Response(
            pkgutil.get_data("dash", "favicon.ico"),
            content_type="image/x-icon",
        )

    def get_asset_url(self, path):
        asset = _get_asset_path(
            self.config.requests_pathname_prefix,
            path,
            self.config.assets_url_path.lstrip("/"),
        )

        return asset

    def get_relative_path(self, path):
        """
        Return a path with `requests_pathname_prefix` prefixed before it.
        Use this function when specifying local URL paths that will work
        in environments regardless of what `requests_pathname_prefix` is.
        In some deployment environments, like Dash Enterprise,
        `requests_pathname_prefix` is set to the application name,
        e.g. `my-dash-app`.
        When working locally, `requests_pathname_prefix` might be unset and
        so a relative URL like `/page-2` can just be `/page-2`.
        However, when the app is deployed to a URL like `/my-dash-app`, then
        `app.get_relative_path('/page-2')` will return `/my-dash-app/page-2`.
        This can be used as an alternative to `get_asset_url` as well with
        `app.get_relative_path('/assets/logo.png')`

        Use this function with `app.strip_relative_path` in callbacks that
        deal with `dcc.Location` `pathname` routing.
        That is, your usage may look like:
        ```
        app.layout = html.Div([
            dcc.Location(id='url'),
            html.Div(id='content')
        ])
        @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
        def display_content(path):
            page_name = app.strip_relative_path(path)
            if not page_name:  # None or ''
                return html.Div([
                    dcc.Link(href=app.get_relative_path('/page-1')),
                    dcc.Link(href=app.get_relative_path('/page-2')),
                ])
            elif page_name == 'page-1':
                return chapters.page_1
            if page_name == "page-2":
                return chapters.page_2
        ```
        """
        asset = _get_relative_path(
            self.config.requests_pathname_prefix,
            path,
        )

        return asset

    def strip_relative_path(self, path):
        """
        Return a path with `requests_pathname_prefix` and leading and trailing
        slashes stripped from it. Also, if None is passed in, None is returned.
        Use this function with `get_relative_path` in callbacks that deal
        with `dcc.Location` `pathname` routing.
        That is, your usage may look like:
        ```
        app.layout = html.Div([
            dcc.Location(id='url'),
            html.Div(id='content')
        ])
        @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
        def display_content(path):
            page_name = app.strip_relative_path(path)
            if not page_name:  # None or ''
                return html.Div([
                    dcc.Link(href=app.get_relative_path('/page-1')),
                    dcc.Link(href=app.get_relative_path('/page-2')),
                ])
            elif page_name == 'page-1':
                return chapters.page_1
            if page_name == "page-2":
                return chapters.page_2
        ```
        Note that `chapters.page_1` will be served if the user visits `/page-1`
        _or_ `/page-1/` since `strip_relative_path` removes the trailing slash.

        Also note that `strip_relative_path` is compatible with
        `get_relative_path` in environments where `requests_pathname_prefix` set.
        In some deployment environments, like Dash Enterprise,
        `requests_pathname_prefix` is set to the application name, e.g. `my-dash-app`.
        When working locally, `requests_pathname_prefix` might be unset and
        so a relative URL like `/page-2` can just be `/page-2`.
        However, when the app is deployed to a URL like `/my-dash-app`, then
        `app.get_relative_path('/page-2')` will return `/my-dash-app/page-2`

        The `pathname` property of `dcc.Location` will return '`/my-dash-app/page-2`'
        to the callback.
        In this case, `app.strip_relative_path('/my-dash-app/page-2')`
        will return `'page-2'`

        For nested URLs, slashes are still included:
        `app.strip_relative_path('/page-1/sub-page-1/')` will return
        `page-1/sub-page-1`
        ```
        """
        return _strip_relative_path(
            self.config.requests_pathname_prefix,
            path,
        )

    def _setup_dev_tools(self, **kwargs):
        debug = kwargs.get("debug", False)
        dev_tools = self._dev_tools = _AttributeDict()

        for attr in (
            "ui",
            "props_check",
            "serve_dev_bundles",
            "hot_reload",
            "silence_routes_logging",
            "prune_errors",
        ):
            dev_tools[attr] = get_combined_config(
                attr, kwargs.get(attr, None), default=debug
            )

        for attr, _type, default in (
            ("hot_reload_interval", float, 3),
            ("hot_reload_watch_interval", float, 0.5),
            ("hot_reload_max_retry", int, 8),
        ):
            dev_tools[attr] = _type(
                get_combined_config(
                    attr, kwargs.get(attr, None), default=default
                )
            )

        return dev_tools

    def enable_dev_tools(
        self,
        debug=None,
        dev_tools_ui=None,
        dev_tools_props_check=None,
        dev_tools_serve_dev_bundles=None,
        dev_tools_hot_reload=None,
        dev_tools_hot_reload_interval=None,
        dev_tools_hot_reload_watch_interval=None,
        dev_tools_hot_reload_max_retry=None,
        dev_tools_silence_routes_logging=None,
        dev_tools_prune_errors=None,
    ):
        """Activate the dev tools, called by `run_server`. If your application
        is served by wsgi and you want to activate the dev tools, you can call
        this method out of `__main__`.

        All parameters can be set by environment variables as listed.
        Values provided here take precedence over environment variables.

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
            - DASH_PRUNE_ERRORS

        :param debug: Enable/disable all the dev tools unless overridden by the
            arguments or environment variables. Default is ``True`` when
            ``enable_dev_tools`` is called directly, and ``False`` when called
            via ``run_server``. env: ``DASH_DEBUG``
        :type debug: bool

        :param dev_tools_ui: Show the dev tools UI. env: ``DASH_UI``
        :type dev_tools_ui: bool

        :param dev_tools_props_check: Validate the types and values of Dash
            component props. env: ``DASH_PROPS_CHECK``
        :type dev_tools_props_check: bool

        :param dev_tools_serve_dev_bundles: Serve the dev bundles. Production
            bundles do not necessarily include all the dev tools code.
            env: ``DASH_SERVE_DEV_BUNDLES``
        :type dev_tools_serve_dev_bundles: bool

        :param dev_tools_hot_reload: Activate hot reloading when app, assets,
            and component files change. env: ``DASH_HOT_RELOAD``
        :type dev_tools_hot_reload: bool

        :param dev_tools_hot_reload_interval: Interval in seconds for the
            client to request the reload hash. Default 3.
            env: ``DASH_HOT_RELOAD_INTERVAL``
        :type dev_tools_hot_reload_interval: float

        :param dev_tools_hot_reload_watch_interval: Interval in seconds for the
            server to check asset and component folders for changes.
            Default 0.5. env: ``DASH_HOT_RELOAD_WATCH_INTERVAL``
        :type dev_tools_hot_reload_watch_interval: float

        :param dev_tools_hot_reload_max_retry: Maximum number of failed reload
            hash requests before failing and displaying a pop up. Default 8.
            env: ``DASH_HOT_RELOAD_MAX_RETRY``
        :type dev_tools_hot_reload_max_retry: int

        :param dev_tools_silence_routes_logging: Silence the `werkzeug` logger,
            will remove all routes logging. Enabled with debugging by default
            because hot reload hash checks generate a lot of requests.
            env: ``DASH_SILENCE_ROUTES_LOGGING``
        :type dev_tools_silence_routes_logging: bool

        :param dev_tools_prune_errors: Reduce tracebacks to just user code,
            stripping out Flask and Dash pieces. Only available with debugging.
            `True` by default, set to `False` to see the complete traceback.
            env: ``DASH_PRUNE_ERRORS``
        :type dev_tools_prune_errors: bool

        :return: debug
        """
        if debug is None:
            debug = get_combined_config("debug", None, True)

        dev_tools = self._setup_dev_tools(
            debug=debug,
            ui=dev_tools_ui,
            props_check=dev_tools_props_check,
            serve_dev_bundles=dev_tools_serve_dev_bundles,
            hot_reload=dev_tools_hot_reload,
            hot_reload_interval=dev_tools_hot_reload_interval,
            hot_reload_watch_interval=dev_tools_hot_reload_watch_interval,
            hot_reload_max_retry=dev_tools_hot_reload_max_retry,
            silence_routes_logging=dev_tools_silence_routes_logging,
            prune_errors=dev_tools_prune_errors,
        )

        if dev_tools.silence_routes_logging:
            logging.getLogger("werkzeug").setLevel(logging.ERROR)
            self.logger.setLevel(logging.INFO)

        if dev_tools.hot_reload:
            _reload = self._hot_reload
            _reload.hash = _generate_hash()

            component_packages_dist = [
                os.path.dirname(package.path)
                if hasattr(package, "path")
                else package.filename
                for package in (
                    pkgutil.find_loader(x)
                    for x in list(ComponentRegistry.registry)
                    + ["dash_renderer"]
                )
            ]

            _reload.watch_thread = threading.Thread(
                target=lambda: _watch.watch(
                    [self.config.assets_folder] + component_packages_dist,
                    self._on_assets_change,
                    sleep_time=dev_tools.hot_reload_watch_interval,
                )
            )
            _reload.watch_thread.daemon = True
            _reload.watch_thread.start()

        if debug and dev_tools.prune_errors:

            @self.server.errorhandler(Exception)
            def _wrap_errors(_):
                # find the callback invocation, if the error is from a callback
                # and skip the traceback up to that point
                # if the error didn't come from inside a callback, we won't
                # skip anything.
                tb = get_current_traceback()
                skip = 0
                for i, line in enumerate(tb.plaintext.splitlines()):
                    if "%% callback invoked %%" in line:
                        skip = int((i + 1) / 2)
                        break
                return get_current_traceback(skip=skip).render_full(), 500

        if (
            debug
            and dev_tools.serve_dev_bundles
            and not self.scripts.config.serve_locally
        ):
            # Dev bundles only works locally.
            self.scripts.config.serve_locally = True
            print(
                "WARNING: dev bundles requested with serve_locally=False.\n"
                "This is not supported, switching to serve_locally=True"
            )

        return debug

    # noinspection PyProtectedMember
    def _on_assets_change(self, filename, modified, deleted):
        _reload = self._hot_reload
        with _reload.lock:
            _reload.hard = True
            _reload.hash = _generate_hash()

            if self.config.assets_folder in filename:
                asset_path = (
                    os.path.relpath(
                        filename,
                        os.path.commonprefix(
                            [self.config.assets_folder, filename]
                        ),
                    )
                    .replace("\\", "/")
                    .lstrip("/")
                )

                _reload.changed_assets.append(
                    {
                        "url": self.get_asset_url(asset_path),
                        "modified": int(modified),
                        "is_css": filename.endswith("css"),
                    }
                )

                if filename not in self._assets_files and not deleted:
                    res = self._add_assets_resource(asset_path, filename)
                    if filename.endswith("js"):
                        self.scripts.append_script(res)
                    elif filename.endswith("css"):
                        self.css.append_css(res)

                if deleted:
                    if filename in self._assets_files:
                        self._assets_files.remove(filename)

                    def delete_resource(resources):
                        to_delete = None
                        for r in resources:
                            if r.get("asset_path") == asset_path:
                                to_delete = r
                                break
                        if to_delete:
                            resources.remove(to_delete)

                    if filename.endswith("js"):
                        # pylint: disable=protected-access
                        delete_resource(self.scripts._resources._resources)
                    elif filename.endswith("css"):
                        # pylint: disable=protected-access
                        delete_resource(self.css._resources._resources)

    def run_server(
        self,
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
        dev_tools_prune_errors=None,
        **flask_run_options
    ):
        """Start the flask server in local mode, you should not run this on a
        production server, use gunicorn/waitress instead.

        If a parameter can be set by an environment variable, that is listed
        too. Values provided here take precedence over environment variables.

        :param port: Port used to serve the application
        :type port: int

        :param debug: Set Flask debug mode and enable dev tools.
            env: ``DASH_DEBUG``
        :type debug: bool

        :param debug: Enable/disable all the dev tools unless overridden by the
            arguments or environment variables. Default is ``True`` when
            ``enable_dev_tools`` is called directly, and ``False`` when called
            via ``run_server``. env: ``DASH_DEBUG``
        :type debug: bool

        :param dev_tools_ui: Show the dev tools UI. env: ``DASH_UI``
        :type dev_tools_ui: bool

        :param dev_tools_props_check: Validate the types and values of Dash
            component props. env: ``DASH_PROPS_CHECK``
        :type dev_tools_props_check: bool

        :param dev_tools_serve_dev_bundles: Serve the dev bundles. Production
            bundles do not necessarily include all the dev tools code.
            env: ``DASH_SERVE_DEV_BUNDLES``
        :type dev_tools_serve_dev_bundles: bool

        :param dev_tools_hot_reload: Activate hot reloading when app, assets,
            and component files change. env: ``DASH_HOT_RELOAD``
        :type dev_tools_hot_reload: bool

        :param dev_tools_hot_reload_interval: Interval in seconds for the
            client to request the reload hash. Default 3.
            env: ``DASH_HOT_RELOAD_INTERVAL``
        :type dev_tools_hot_reload_interval: float

        :param dev_tools_hot_reload_watch_interval: Interval in seconds for the
            server to check asset and component folders for changes.
            Default 0.5. env: ``DASH_HOT_RELOAD_WATCH_INTERVAL``
        :type dev_tools_hot_reload_watch_interval: float

        :param dev_tools_hot_reload_max_retry: Maximum number of failed reload
            hash requests before failing and displaying a pop up. Default 8.
            env: ``DASH_HOT_RELOAD_MAX_RETRY``
        :type dev_tools_hot_reload_max_retry: int

        :param dev_tools_silence_routes_logging: Silence the `werkzeug` logger,
            will remove all routes logging. Enabled with debugging by default
            because hot reload hash checks generate a lot of requests.
            env: ``DASH_SILENCE_ROUTES_LOGGING``
        :type dev_tools_silence_routes_logging: bool

        :param dev_tools_prune_errors: Reduce tracebacks to just user code,
            stripping out Flask and Dash pieces. Only available with debugging.
            `True` by default, set to `False` to see the complete traceback.
            env: ``DASH_PRUNE_ERRORS``
        :type dev_tools_prune_errors: bool

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
            dev_tools_prune_errors,
        )

        if self._dev_tools.silence_routes_logging:
            # Since it's silenced, the address doesn't show anymore.
            host = flask_run_options.get("host", "127.0.0.1")
            ssl_context = flask_run_options.get("ssl_context")
            self.logger.info(
                "Running on %s://%s:%s%s",
                "https" if ssl_context else "http",
                host,
                port,
                self.config.requests_pathname_prefix,
            )

            # Generate a debugger pin and log it to the screen.
            debugger_pin = os.environ["WERKZEUG_DEBUG_PIN"] = "-".join(
                itertools.chain(
                    "".join([str(random.randint(0, 9)) for _ in range(3)])
                    for _ in range(3)
                )
            )

            self.logger.info("Debugger PIN: %s", debugger_pin)

        self.server.run(port=port, debug=debug, **flask_run_options)
