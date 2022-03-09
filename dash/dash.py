import os
import sys
import collections
import importlib
from importlib.machinery import ModuleSpec
import pkgutil
import threading
import re
import logging
import time
import mimetypes
import hashlib
import base64
from urllib.parse import urlparse

import flask
from flask_compress import Compress
from werkzeug.debug.tbtools import get_current_traceback
from pkg_resources import get_distribution, parse_version
from dash import dcc
from dash import html
from dash import dash_table

from .fingerprint import build_fingerprint, check_fingerprint
from .resources import Scripts, Css
from .dependencies import (
    handle_grouped_callback_args,
    Output,
    State,
    Input,
)
from .development.base_component import ComponentRegistry
from .exceptions import (
    PreventUpdate,
    InvalidResourceError,
    ProxyError,
    DuplicateCallback,
)
from .version import __version__
from ._configs import get_combined_config, pathname_configs
from ._utils import (
    AttributeDict,
    format_tag,
    generate_hash,
    inputs_to_dict,
    inputs_to_vals,
    interpolate_str,
    patch_collections_abc,
    split_callback_id,
    to_json,
)
from . import _callback
from . import _get_paths
from . import _dash_renderer
from . import _validate
from . import _watch
from ._grouping import (
    flatten_grouping,
    map_grouping,
    grouping_len,
)


_flask_compress_version = parse_version(get_distribution("flask-compress").version)

# Add explicit mapping for map files
mimetypes.add_type("application/json", ".map", True)

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

_re_index_entry = "{%app_entry%}", "{%app_entry%}"
_re_index_config = "{%config%}", "{%config%}"
_re_index_scripts = "{%scripts%}", "{%scripts%}"

_re_index_entry_id = 'id="react-entry-point"', "#react-entry-point"
_re_index_config_id = 'id="_dash-config"', "#_dash-config"
_re_index_scripts_id = 'src="[^"]*dash[-_]renderer[^"]*"', "dash-renderer"
_re_renderer_scripts_id = 'id="_dash-renderer', "new DashRenderer"


class _NoUpdate:
    # pylint: disable=too-few-public-methods
    pass


# Singleton signal to not update an output, alternative to PreventUpdate
no_update = _callback.NoUpdate()  # pylint: disable=protected-access


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments, too-many-locals
class Dash:
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
        Use with ``serve_locally=False``. assets_external_path is joined
        with assets_url_path to determine the absolute url to the
        asset folder. Dash can still find js and css to automatically load
        if you also keep local copies in your assets folder that Dash can index,
        but external serving can improve performance and reduce load on
        the Dash server.
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
        Default ``False``
    :type compress: boolean

    :param meta_tags: html <meta> tags to be added to the index page.
        Each dict should have the attributes and values for one tag, eg:
        ``{'name': 'description', 'content': 'My App'}``
    :type meta_tags: list of dicts

    :param index_string: Override the standard Dash index page.
        Must contain the correct insertion markers to interpolate various
        content into it depending on the app config and components used.
        See https://dash.plotly.com/external-resources for details.
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

    :param prevent_initial_callbacks: Default ``False``: Sets the default value
        of ``prevent_initial_call`` for all callbacks added to the app.
        Normally all callbacks are fired when the associated outputs are first
        added to the page. You can disable this for individual callbacks by
        setting ``prevent_initial_call`` in their definitions, or set it
        ``True`` here in which case you must explicitly set it ``False`` for
        those callbacks you wish to have an initial call. This setting has no
        effect on triggering callbacks when their inputs change later on.

    :param show_undo_redo: Default ``False``, set to ``True`` to enable undo
        and redo buttons for stepping through the history of the app state.
    :type show_undo_redo: boolean

    :param extra_hot_reload_paths: A list of paths to watch for changes, in
        addition to assets and known Python and JS code, if hot reloading is
        enabled.
    :type extra_hot_reload_paths: list of strings

    :param plugins: Extend Dash functionality by passing a list of objects
        with a ``plug`` method, taking a single argument: this app, which will
        be called after the Flask server is attached.
    :type plugins: list of objects

    :param title: Default ``Dash``. Configures the document.title
    (the text that appears in a browser tab).

    :param update_title: Default ``Updating...``. Configures the document.title
    (the text that appears in a browser tab) text when a callback is being run.
    Set to None or '' if you don't want the document.title to change or if you
    want to control the document.title through a separate component or
    clientside callback.

    :param long_callback_manager: Long callback manager instance to support the
    ``@app.long_callback`` decorator. Currently an instance of one of
    ``DiskcacheLongCallbackManager`` or ``CeleryLongCallbackManager``
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
        prevent_initial_callbacks=False,
        show_undo_redo=False,
        extra_hot_reload_paths=None,
        plugins=None,
        title="Dash",
        update_title="Updating...",
        long_callback_manager=None,
        **obsolete,
    ):
        _validate.check_obsolete(obsolete)

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

        if (
            self.server is not None
            and not hasattr(self.server.config, "COMPRESS_ALGORITHM")
            and _flask_compress_version >= parse_version("1.6.0")
        ):
            # flask-compress==1.6.0 changed default to ['br', 'gzip']
            # and non-overridable default compression with Brotli is
            # causing performance issues
            self.server.config["COMPRESS_ALGORITHM"] = ["gzip"]

        base_prefix, routes_prefix, requests_prefix = pathname_configs(
            url_base_pathname, routes_pathname_prefix, requests_pathname_prefix
        )

        self.config = AttributeDict(
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
            compress=get_combined_config("compress", compress, False),
            meta_tags=meta_tags or [],
            external_scripts=external_scripts or [],
            external_stylesheets=external_stylesheets or [],
            suppress_callback_exceptions=get_combined_config(
                "suppress_callback_exceptions", suppress_callback_exceptions, False
            ),
            prevent_initial_callbacks=prevent_initial_callbacks,
            show_undo_redo=show_undo_redo,
            extra_hot_reload_paths=extra_hot_reload_paths or [],
            title=title,
            update_title=update_title,
        )
        self.config.set_read_only(
            [
                "name",
                "assets_folder",
                "assets_url_path",
                "eager_loading",
                "serve_locally",
                "compress",
            ],
            "Read-only: can only be set in the Dash constructor",
        )
        self.config.finalize(
            "Invalid config key. Some settings are only available "
            "via the Dash constructor"
        )

        _get_paths.CONFIG = self.config

        # keep title as a class property for backwards compatibility
        self.title = title

        # list of dependencies - this one is used by the back end for dispatching
        self.callback_map = {}
        # same deps as a list to catch duplicate outputs, and to send to the front end
        self._callback_list = []

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
        self._layout_is_function = False
        self.validation_layout = None
        self._extra_components = []

        self._setup_dev_tools()
        self._hot_reload = AttributeDict(
            hash=None,
            hard=False,
            lock=threading.RLock(),
            watch_thread=None,
            changed_assets=[],
        )

        self._assets_files = []
        self._long_callback_count = 0
        self._long_callback_manager = long_callback_manager

        self.logger = logging.getLogger(name)
        self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))

        if isinstance(plugins, patch_collections_abc("Iterable")):
            for plugin in plugins:
                plugin.plug(self)

        if self.server is not None:
            self.init_app()

        self.logger.setLevel(logging.INFO)

    def init_app(self, app=None, **kwargs):
        """Initialize the parts of Dash that require a flask app."""

        self.config.update(kwargs)
        self.config.set_read_only(
            [
                "url_base_pathname",
                "routes_pathname_prefix",
                "requests_pathname_prefix",
            ],
            "Read-only: can only be set in the Dash constructor or during init_app()",
        )

        config = self.config

        if app is not None:
            self.server = app

        assets_blueprint_name = "{}{}".format(
            config.routes_pathname_prefix.replace("/", "_").replace(".", "_"),
            "dash_assets",
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

        @self.server.errorhandler(PreventUpdate)
        def _handle_error(_):
            """Handle a halted callback and return an empty 204 response."""
            return "", 204

        self.server.before_first_request(self._setup_server)

        # add a handler for components suites errors to return 404
        self.server.errorhandler(InvalidResourceError)(self._invalid_resources_handler)

        self._add_url(
            "_dash-component-suites/<string:package_name>/<path:fingerprinted_path>",
            self.serve_component_suites,
        )
        self._add_url("_dash-layout", self.serve_layout)
        self._add_url("_dash-dependencies", self.dependencies)
        self._add_url("_dash-update-component", self.dispatch, ["POST"])
        self._add_url("_reload-hash", self.serve_reload_hash)
        self._add_url("_favicon.ico", self._serve_default_favicon)
        self._add_url("", self.index)

        # catch-all for front-end routes, used by dcc.Location
        self._add_url("<path:path>", self.index)

    def _add_url(self, name, view_func, methods=("GET",)):
        full_name = self.config.routes_pathname_prefix + name

        self.server.add_url_rule(
            full_name, view_func=view_func, endpoint=full_name, methods=list(methods)
        )

        # record the url in Dash.routes so that it can be accessed later
        # e.g. for adding authentication with flask_login
        self.routes.append(full_name)

    @property
    def layout(self):
        return self._layout

    def _layout_value(self):
        layout = self._layout() if self._layout_is_function else self._layout

        # Add any extra components
        if self._extra_components:
            layout = html.Div(children=[layout] + self._extra_components)

        return layout

    @layout.setter
    def layout(self, value):
        _validate.validate_layout_type(value)
        self._layout_is_function = isinstance(value, patch_collections_abc("Callable"))
        self._layout = value

        # for using flask.has_request_context() to deliver a full layout for
        # validation inside a layout function - track if a user might be doing this.
        if (
            self._layout_is_function
            and not self.validation_layout
            and not self.config.suppress_callback_exceptions
        ):

            def simple_clone(c, children=None):
                cls = type(c)
                # in Py3 we can use the __init__ signature to reduce to just
                # required args and id; in Py2 this doesn't work so we just
                # empty out children.
                sig = getattr(cls.__init__, "__signature__", None)
                props = {
                    p: getattr(c, p)
                    for p in c._prop_names  # pylint: disable=protected-access
                    if hasattr(c, p)
                    and (
                        p == "id" or not sig or sig.parameters[p].default == c.REQUIRED
                    )
                }
                if props.get("children", children):
                    props["children"] = children or []
                return cls(**props)

            layout_value = self._layout_value()
            _validate.validate_layout(value, layout_value)
            self.validation_layout = simple_clone(
                # pylint: disable=protected-access
                layout_value,
                [simple_clone(c) for c in layout_value._traverse_ids()],
            )

    @property
    def index_string(self):
        return self._index_string

    @index_string.setter
    def index_string(self, value):
        checks = (_re_index_entry, _re_index_config, _re_index_scripts)
        _validate.validate_index("index string", checks, value)
        self._index_string = value

    def serve_layout(self):
        layout = self._layout_value()

        # TODO - Set browser cache limit - pass hash into frontend
        return flask.Response(
            to_json(layout),
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
            "suppress_callback_exceptions": self.config.suppress_callback_exceptions,
            "update_title": self.config.update_title,
        }
        if self._dev_tools.hot_reload:
            config["hot_reload"] = {
                # convert from seconds to msec as used by js `setInterval`
                "interval": int(self._dev_tools.hot_reload_interval * 1000),
                "max_retry": self._dev_tools.hot_reload_max_retry,
            }
        if self.validation_layout and not self.config.suppress_callback_exceptions:
            validation_layout = self.validation_layout

            # Add extra components
            if self._extra_components:
                validation_layout = html.Div(
                    children=[validation_layout] + self._extra_components
                )

            config["validation_layout"] = validation_layout

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

    def _collect_and_register_resources(self, resources):
        # now needs the app context.
        # template in the necessary component suite JS bundles
        # add the version number of the package as a query parameter
        # for cache busting
        def _relative_url_path(relative_package_path="", namespace=""):
            if any(
                relative_package_path.startswith(x + "/")
                for x in ["dcc", "html", "dash_table"]
            ):
                relative_package_path = relative_package_path.replace("dash.", "")
                version = importlib.import_module(
                    "{}.{}".format(namespace, os.path.split(relative_package_path)[0])
                ).__version__
            else:
                version = importlib.import_module(namespace).__version__

            module_path = os.path.join(
                os.path.dirname(sys.modules[namespace].__file__), relative_package_path
            )

            modified = int(os.stat(module_path).st_mtime)

            return "{}_dash-component-suites/{}/{}".format(
                self.config.requests_pathname_prefix,
                namespace,
                build_fingerprint(relative_package_path, version, modified),
            )

        srcs = []
        for resource in resources:
            is_dynamic_resource = resource.get("dynamic", False)

            if "relative_package_path" in resource:
                paths = resource["relative_package_path"]
                paths = [paths] if isinstance(paths, str) else paths

                for rel_path in paths:
                    if any(x in rel_path for x in ["dcc", "html", "dash_table"]):
                        rel_path = rel_path.replace("dash.", "")

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
                raise Exception("Serving files from absolute_path isn't supported yet")
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
                format_tag("link", link, opened=True)
                if isinstance(link, dict)
                else f'<link rel="stylesheet" href="{link}">'
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
        for js_dist_dependency in _dash_renderer._js_dist_dependencies:
            dep = {}
            for key, value in js_dist_dependency.items():
                dep[key] = value[mode] if isinstance(value, dict) else value

            deps.append(dep)

        dev = self._dev_tools.serve_dev_bundles
        srcs = (
            self._collect_and_register_resources(
                self.scripts._resources._filter_resources(deps, dev_bundles=dev)
            )
            + self.config.external_scripts
            + self._collect_and_register_resources(
                self.scripts.get_all_scripts(dev_bundles=dev)
                + self.scripts._resources._filter_resources(
                    _dash_renderer._js_dist, dev_bundles=dev
                )
                + self.scripts._resources._filter_resources(
                    dcc._js_dist, dev_bundles=dev
                )
                + self.scripts._resources._filter_resources(
                    html._js_dist, dev_bundles=dev
                )
                + self.scripts._resources._filter_resources(
                    dash_table._js_dist, dev_bundles=dev
                )
            )
        )

        self._inline_scripts.extend(_callback.GLOBAL_INLINE_SCRIPTS)
        _callback.GLOBAL_INLINE_SCRIPTS.clear()

        return "\n".join(
            [
                format_tag("script", src)
                if isinstance(src, dict)
                else '<script src="{}"></script>'.format(src)
                for src in srcs
            ]
            + ["<script>{}</script>".format(src) for src in self._inline_scripts]
        )

    def _generate_config_html(self):
        return '<script id="_dash-config" type="application/json">{}</script>'.format(
            to_json(self._config())
        )

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
            tags.append('<meta http-equiv="X-UA-Compatible" content="IE=edge">')
        if not has_charset:
            tags.append('<meta charset="UTF-8">')

        tags += [format_tag("meta", x, opened=True) for x in meta_tags]

        return "\n      ".join(tags)

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, fingerprinted_path):
        path_in_pkg, has_fingerprint = check_fingerprint(fingerprinted_path)

        _validate.validate_js_path(self.registered_paths, package_name, path_in_pkg)

        extension = "." + path_in_pkg.split(".")[-1]
        mimetype = mimetypes.types_map.get(extension, "application/octet-stream")

        package = sys.modules[package_name]
        self.logger.debug(
            "serving -- package: %s[%s] resource: %s => location: %s",
            package_name,
            package.__version__,
            path_in_pkg,
            package.__path__,
        )

        response = flask.Response(
            pkgutil.get_data(package_name, path_in_pkg), mimetype=mimetype
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

            request_etag = flask.request.headers.get("If-None-Match")

            if '"{}"'.format(tag) == request_etag:
                response = flask.Response(None, status=304)

        return response

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta_html()
        renderer = self._generate_renderer()

        # use self.title instead of app.config.title for backwards compatibility
        title = self.title

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

        favicon = format_tag(
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
            _re_index_entry_id,
            _re_index_config_id,
            _re_index_scripts_id,
            _re_renderer_scripts_id,
        )
        _validate.validate_index("index", checks, index)
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
        return interpolate_str(
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
        return flask.jsonify(self._callback_list)

    def clientside_callback(self, clientside_function, *args, **kwargs):
        """Create a callback that updates the output by calling a clientside
        (JavaScript) function instead of a Python function.

        Unlike `@app.callback`, `clientside_callback` is not a decorator:
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

        The last, optional argument `prevent_initial_call` causes the callback
        not to fire when its outputs are first added to the page. Defaults to
        `False` unless `prevent_initial_callbacks=True` at the app level.
        """
        return _callback.register_clientside_callback(
            self._callback_list,
            self.callback_map,
            self.config.prevent_initial_callbacks,
            self._inline_scripts,
            clientside_function,
            *args,
            **kwargs,
        )

    def callback(self, *_args, **_kwargs):
        """
        Normally used as a decorator, `@app.callback` provides a server-side
        callback relating the values of one or more `Output` items to one or
        more `Input` items which will trigger the callback when they change,
        and optionally `State` items which provide additional information but
        do not trigger the callback directly.

        The last, optional argument `prevent_initial_call` causes the callback
        not to fire when its outputs are first added to the page. Defaults to
        `False` unless `prevent_initial_callbacks=True` at the app level.


        """
        return _callback.register_callback(
            self._callback_list,
            self.callback_map,
            self.config.prevent_initial_callbacks,
            *_args,
            **_kwargs,
        )

    def long_callback(self, *_args, **_kwargs):  # pylint: disable=too-many-statements
        """
        Normally used as a decorator, `@app.long_callback` is an alternative to
        `@app.callback` designed for callbacks that take a long time to run,
        without locking up the Dash app or timing out.

        `@long_callback` is designed to support multiple callback managers.
        Two long callback managers are currently implemented:

            - A diskcache manager (`DiskcacheLongCallbackManager`) that runs callback
              logic in a separate process and stores the results to disk using the
              diskcache library. This is the easiest backend to use for local
              development.
            - A Celery manager (`CeleryLongCallbackManager`) that runs callback logic
              in a celery worker and returns results to the Dash app through a Celery
              broker like RabbitMQ or Redis.

        The following arguments may include any valid arguments to `@app.callback`.
        In addition, `@app.long_callback` supports the following optional
        keyword arguments:

        :Keyword Arguments:
            :param manager:
                A long callback manager instance. Currently an instance of one of
                `DiskcacheLongCallbackManager` or `CeleryLongCallbackManager`.
                Defaults to the `long_callback_manager` instance provided to the
                `dash.Dash constructor`.
            :param running:
                A list of 3-element tuples. The first element of each tuple should be
                an `Output` dependency object referencing a property of a component in
                the app layout. The second element is the value that the property
                should be set to while the callback is running, and the third element
                is the value the property should be set to when the callback completes.
            :param cancel:
                A list of `Input` dependency objects that reference a property of a
                component in the app's layout.  When the value of this property changes
                while a callback is running, the callback is canceled.
                Note that the value of the property is not significant, any change in
                value will result in the cancellation of the running job (if any).
            :param progress:
                An `Output` dependency grouping that references properties of
                components in the app's layout. When provided, the decorated function
                will be called with an extra argument as the first argument to the
                function.  This argument, is a function handle that the decorated
                function should call in order to provide updates to the app on its
                current progress. This function accepts a single argument, which
                correspond to the grouping of properties specified in the provided
                `Output` dependency grouping
            :param progress_default:
                A grouping of values that should be assigned to the components
                specified by the `progress` argument when the callback is not in
                progress. If `progress_default` is not provided, all the dependency
                properties specified in `progress` will be set to `None` when the
                callback is not running.
            :param cache_args_to_ignore:
                Arguments to ignore when caching is enabled. If callback is configured
                with keyword arguments (Input/State provided in a dict),
                this should be a list of argument names as strings. Otherwise,
                this should be a list of argument indices as integers.
        """
        # pylint: disable-next=import-outside-toplevel
        from dash._callback_context import callback_context

        # pylint: disable-next=import-outside-toplevel
        from dash.exceptions import WildcardInLongCallback

        # Get long callback manager
        callback_manager = _kwargs.pop("manager", self._long_callback_manager)
        if callback_manager is None:
            raise ValueError(
                "The @app.long_callback decorator requires a long callback manager\n"
                "instance.  This may be provided to the app using the \n"
                "long_callback_manager argument to the dash.Dash constructor, or\n"
                "it may be provided to the @app.long_callback decorator as the \n"
                "manager argument"
            )

        # Extract special long_callback kwargs
        running = _kwargs.pop("running", ())
        cancel = _kwargs.pop("cancel", ())
        progress = _kwargs.pop("progress", ())
        progress_default = _kwargs.pop("progress_default", None)
        interval_time = _kwargs.pop("interval", 1000)
        cache_args_to_ignore = _kwargs.pop("cache_args_to_ignore", [])

        # Parse remaining args just like app.callback
        (
            output,
            flat_inputs,
            flat_state,
            inputs_state_indices,
            prevent_initial_call,
        ) = handle_grouped_callback_args(_args, _kwargs)
        inputs_and_state = flat_inputs + flat_state
        args_deps = map_grouping(lambda i: inputs_and_state[i], inputs_state_indices)

        # Disallow wildcard dependencies
        for deps in [output, flat_inputs, flat_state]:
            for dep in flatten_grouping(deps):
                if dep.has_wildcard():
                    raise WildcardInLongCallback(
                        f"""
                        @app.long_callback does not support dependencies with
                        pattern-matching ids
                            Received: {repr(dep)}\n"""
                    )

        # Get unique id for this long_callback definition.  This increment is not
        # thread safe, but it doesn't need to be because callback definitions
        # happen on the main thread before the app starts
        self._long_callback_count += 1
        long_callback_id = self._long_callback_count

        # Create Interval and Store for long callback and add them to the app's
        # _extra_components list
        interval_id = f"_long_callback_interval_{long_callback_id}"
        interval_component = dcc.Interval(
            id=interval_id, interval=interval_time, disabled=prevent_initial_call
        )
        store_id = f"_long_callback_store_{long_callback_id}"
        store_component = dcc.Store(id=store_id, data={})
        self._extra_components.extend([interval_component, store_component])

        # Compute full component plus property name for the cancel dependencies
        cancel_prop_ids = tuple(
            ".".join([dep.component_id, dep.component_property]) for dep in cancel
        )

        def wrapper(fn):
            background_fn = callback_manager.make_job_fn(fn, bool(progress), args_deps)

            def callback(_triggers, user_store_data, user_callback_args):
                # Build result cache key from inputs
                pending_key = callback_manager.build_cache_key(
                    fn, user_callback_args, cache_args_to_ignore
                )
                current_key = user_store_data.get("current_key", None)
                pending_job = user_store_data.get("pending_job", None)

                should_cancel = pending_key == current_key or any(
                    trigger["prop_id"] in cancel_prop_ids
                    for trigger in callback_context.triggered
                )

                # Compute grouping of values to set the progress component's to
                # when cleared
                if progress_default is None:
                    clear_progress = (
                        map_grouping(lambda x: None, progress) if progress else ()
                    )
                else:
                    clear_progress = progress_default

                if should_cancel:
                    user_store_data["current_key"] = None
                    user_store_data["pending_key"] = None
                    user_store_data["pending_job"] = None

                    callback_manager.terminate_job(pending_job)

                    return dict(
                        user_callback_output=map_grouping(lambda x: no_update, output),
                        interval_disabled=True,
                        in_progress=[val for (_, _, val) in running],
                        progress=clear_progress,
                        user_store_data=user_store_data,
                    )

                # Look up progress value if a job is in progress
                if pending_job:
                    progress_value = callback_manager.get_progress(pending_key)
                else:
                    progress_value = None

                if callback_manager.result_ready(pending_key):
                    result = callback_manager.get_result(pending_key, pending_job)
                    # Set current key (hash of data stored in client)
                    # to pending key (hash of data requested by client)
                    user_store_data["current_key"] = pending_key

                    # Disable interval if this value was pulled from cache.
                    # If this value was the result of a background calculation, don't
                    # disable yet. If no other calculations are in progress,
                    # interval will be disabled in should_cancel logic above
                    # the next time the interval fires.
                    interval_disabled = pending_job is None
                    return dict(
                        user_callback_output=result,
                        interval_disabled=interval_disabled,
                        in_progress=[val for (_, _, val) in running],
                        progress=clear_progress,
                        user_store_data=user_store_data,
                    )
                if progress_value:
                    return dict(
                        user_callback_output=map_grouping(lambda x: no_update, output),
                        interval_disabled=False,
                        in_progress=[val for (_, val, _) in running],
                        progress=progress_value or {},
                        user_store_data=user_store_data,
                    )

                # Check if there is a running calculation that can now
                # be canceled
                old_pending_key = user_store_data.get("pending_key", None)
                if (
                    old_pending_key
                    and old_pending_key != pending_key
                    and callback_manager.job_running(pending_job)
                ):
                    callback_manager.terminate_job(pending_job)

                user_store_data["pending_key"] = pending_key
                callback_manager.terminate_unhealthy_job(pending_job)
                if not callback_manager.job_running(pending_job):
                    user_store_data["pending_job"] = callback_manager.call_job_fn(
                        pending_key, background_fn, user_callback_args
                    )

                return dict(
                    user_callback_output=map_grouping(lambda x: no_update, output),
                    interval_disabled=False,
                    in_progress=[val for (_, val, _) in running],
                    progress=clear_progress,
                    user_store_data=user_store_data,
                )

            return self.callback(
                inputs=dict(
                    _triggers=dict(
                        n_intervals=Input(interval_id, "n_intervals"),
                        cancel=cancel,
                    ),
                    user_store_data=State(store_id, "data"),
                    user_callback_args=args_deps,
                ),
                output=dict(
                    user_callback_output=output,
                    interval_disabled=Output(interval_id, "disabled"),
                    in_progress=[dep for (dep, _, _) in running],
                    progress=progress,
                    user_store_data=Output(store_id, "data"),
                ),
                prevent_initial_call=prevent_initial_call,
            )(callback)

        return wrapper

    def dispatch(self):
        body = flask.request.get_json()
        flask.g.inputs_list = inputs = body.get(  # pylint: disable=assigning-non-slot
            "inputs", []
        )
        flask.g.states_list = state = body.get(  # pylint: disable=assigning-non-slot
            "state", []
        )
        output = body["output"]
        outputs_list = body.get("outputs") or split_callback_id(output)
        flask.g.outputs_list = outputs_list  # pylint: disable=assigning-non-slot

        flask.g.input_values = (  # pylint: disable=assigning-non-slot
            input_values
        ) = inputs_to_dict(inputs)
        flask.g.state_values = inputs_to_dict(  # pylint: disable=assigning-non-slot
            state
        )
        changed_props = body.get("changedPropIds", [])
        flask.g.triggered_inputs = [  # pylint: disable=assigning-non-slot
            {"prop_id": x, "value": input_values.get(x)} for x in changed_props
        ]

        response = (
            flask.g.dash_response  # pylint: disable=assigning-non-slot
        ) = flask.Response(mimetype="application/json")

        args = inputs_to_vals(inputs + state)

        try:
            cb = self.callback_map[output]
            func = cb["callback"]

            # Add args_grouping
            inputs_state_indices = cb["inputs_state_indices"]
            inputs_state = inputs + state
            args_grouping = map_grouping(
                lambda ind: inputs_state[ind], inputs_state_indices
            )
            flask.g.args_grouping = args_grouping  # pylint: disable=assigning-non-slot
            flask.g.using_args_grouping = (  # pylint: disable=assigning-non-slot
                not isinstance(inputs_state_indices, int)
                and (
                    inputs_state_indices
                    != list(range(grouping_len(inputs_state_indices)))
                )
            )

            # Add outputs_grouping
            outputs_indices = cb["outputs_indices"]
            if not isinstance(outputs_list, list):
                flat_outputs = [outputs_list]
            else:
                flat_outputs = outputs_list

            outputs_grouping = map_grouping(
                lambda ind: flat_outputs[ind], outputs_indices
            )
            flask.g.outputs_grouping = (  # pylint: disable=assigning-non-slot
                outputs_grouping
            )
            flask.g.using_outputs_grouping = (  # pylint: disable=assigning-non-slot
                not isinstance(outputs_indices, int)
                and outputs_indices != list(range(grouping_len(outputs_indices)))
            )

        except KeyError as missing_callback_function:
            msg = "Callback function not found for output '{}', perhaps you forgot to prepend the '@'?"
            raise KeyError(msg.format(output)) from missing_callback_function
        response.set_data(func(*args, outputs_list=outputs_list))
        return response

    def _setup_server(self):
        # Apply _force_eager_loading overrides from modules
        eager_loading = self.config.eager_loading
        for module_name in ComponentRegistry.registry:
            module = sys.modules[module_name]
            eager = getattr(module, "_force_eager_loading", False)
            eager_loading = eager_loading or eager

        # Update eager_loading settings
        self.scripts.config.eager_loading = eager_loading

        if self.config.include_assets_files:
            self._walk_assets_directory()

        _validate.validate_layout(self.layout, self._layout_value())

        self._generate_scripts_html()
        self._generate_css_dist_html()

        # Copy over global callback data structures assigned with `dash.callback`
        for k in list(_callback.GLOBAL_CALLBACK_MAP):

            if k in self.callback_map:
                raise DuplicateCallback(
                    "The callback `{}` provided with `dash.callback` was already ".format(
                        k
                    )
                    + "assigned with `app.callback`."
                )

            self.callback_map[k] = _callback.GLOBAL_CALLBACK_MAP.pop(k)

        self._callback_list.extend(_callback.GLOBAL_CALLBACK_LIST)
        _callback.GLOBAL_CALLBACK_LIST.clear()

    def _add_assets_resource(self, url_path, file_path):
        res = {"asset_path": url_path, "filepath": file_path}
        if self.config.assets_external_path:
            res["external_url"] = self.get_asset_url(url_path.lstrip("/"))
        self._assets_files.append(file_path)
        return res

    def _walk_assets_directory(self):
        walk_dir = self.config.assets_folder
        slash_splitter = re.compile(r"[\\/]+")
        ignore_str = self.config.assets_ignore
        ignore_filter = re.compile(ignore_str) if ignore_str else None

        for current, _, files in sorted(os.walk(walk_dir)):
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
                    self.scripts.append_script(self._add_assets_resource(path, full))
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
            pkgutil.get_data("dash", "favicon.ico"), content_type="image/x-icon"
        )

    def csp_hashes(self, hash_algorithm="sha256"):
        """Calculates CSP hashes (sha + base64) of all inline scripts, such that
        one of the biggest benefits of CSP (disallowing general inline scripts)
        can be utilized together with Dash clientside callbacks (inline scripts).

        Calculate these hashes after all inline callbacks are defined,
        and add them to your CSP headers before starting the server, for example
        with the flask-talisman package from PyPI:

        flask_talisman.Talisman(app.server, content_security_policy={
            "default-src": "'self'",
            "script-src": ["'self'"] + app.csp_hashes()
        })

        :param hash_algorithm: One of the recognized CSP hash algorithms ('sha256', 'sha384', 'sha512').
        :return: List of CSP hash strings of all inline scripts.
        """

        HASH_ALGORITHMS = ["sha256", "sha384", "sha512"]
        if hash_algorithm not in HASH_ALGORITHMS:
            raise ValueError(
                "Possible CSP hash algorithms: " + ", ".join(HASH_ALGORITHMS)
            )

        method = getattr(hashlib, hash_algorithm)

        self._inline_scripts.extend(_callback.GLOBAL_INLINE_SCRIPTS)
        _callback.GLOBAL_INLINE_SCRIPTS.clear()

        return [
            "'{hash_algorithm}-{base64_hash}'".format(
                hash_algorithm=hash_algorithm,
                base64_hash=base64.b64encode(
                    method(script.encode("utf-8")).digest()
                ).decode("utf-8"),
            )
            for script in (self._inline_scripts + [self.renderer])
        ]

    def get_asset_url(self, path):
        return _get_paths.app_get_asset_url(self.config, path)

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
        return _get_paths.app_get_relative_path(
            self.config.requests_pathname_prefix, path
        )

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
        return _get_paths.app_strip_relative_path(
            self.config.requests_pathname_prefix, path
        )

    def _setup_dev_tools(self, **kwargs):
        debug = kwargs.get("debug", False)
        dev_tools = self._dev_tools = AttributeDict()

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
                get_combined_config(attr, kwargs.get(attr, None), default=default)
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

        if dev_tools.hot_reload:
            _reload = self._hot_reload
            _reload.hash = generate_hash()

            # find_loader should return None on __main__ but doesn't
            # on some Python versions https://bugs.python.org/issue14710
            packages = [
                pkgutil.find_loader(x)
                for x in list(ComponentRegistry.registry)
                if x != "__main__"
            ]

            # # additional condition to account for AssertionRewritingHook object
            # # loader when running pytest

            if "_pytest" in sys.modules:
                from _pytest.assertion.rewrite import (  # pylint: disable=import-outside-toplevel
                    AssertionRewritingHook,
                )

                for index, package in enumerate(packages):
                    if isinstance(package, AssertionRewritingHook):
                        dash_spec = importlib.util.find_spec("dash")
                        dash_test_path = dash_spec.submodule_search_locations[0]
                        setattr(dash_spec, "path", dash_test_path)
                        packages[index] = dash_spec

            component_packages_dist = [
                dash_test_path
                if isinstance(package, ModuleSpec)
                else os.path.dirname(package.path)
                if hasattr(package, "path")
                else os.path.dirname(
                    package._path[0]  # pylint: disable=protected-access
                )
                if hasattr(package, "_path")
                else package.filename
                for package in packages
            ]

            for i, package in enumerate(packages):
                if hasattr(package, "path") and "dash/dash" in os.path.dirname(
                    package.path
                ):
                    component_packages_dist[i : i + 1] = [
                        os.path.join(os.path.dirname(package.path), x)
                        for x in ["dcc", "html", "dash_table"]
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

        if debug and dev_tools.ui:

            def _before_request():
                flask.g.timing_information = {  # pylint: disable=assigning-non-slot
                    "__dash_server": {"dur": time.time(), "desc": None}
                }

            def _after_request(response):
                timing_information = flask.g.get("timing_information", None)
                if timing_information is None:
                    return response

                dash_total = timing_information.get("__dash_server", None)
                if dash_total is not None:
                    dash_total["dur"] = round((time.time() - dash_total["dur"]) * 1000)

                for name, info in timing_information.items():

                    value = name
                    if info.get("desc") is not None:
                        value += ';desc="{}"'.format(info["desc"])

                    if info.get("dur") is not None:
                        value += ";dur={}".format(info["dur"])

                    response.headers.add("Server-Timing", value)

                return response

            self.server.before_request(_before_request)

            self.server.after_request(_after_request)

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
            _reload.hash = generate_hash()

            if self.config.assets_folder in filename:
                asset_path = (
                    os.path.relpath(
                        filename,
                        os.path.commonprefix([self.config.assets_folder, filename]),
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
        host=os.getenv("HOST", "127.0.0.1"),
        port=os.getenv("PORT", "8050"),
        proxy=os.getenv("DASH_PROXY", None),
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
        **flask_run_options,
    ):
        """Start the flask server in local mode, you should not run this on a
        production server, use gunicorn/waitress instead.

        If a parameter can be set by an environment variable, that is listed
        too. Values provided here take precedence over environment variables.

        :param host: Host IP used to serve the application
            env: ``HOST``
        :type host: string

        :param port: Port used to serve the application
            env: ``PORT``
        :type port: int

        :param proxy: If this application will be served to a different URL
            via a proxy configured outside of Python, you can list it here
            as a string of the form ``"{input}::{output}"``, for example:
            ``"http://0.0.0.0:8050::https://my.domain.com"``
            so that the startup message will display an accurate URL.
            env: ``DASH_PROXY``
        :type proxy: string

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

        # Verify port value
        try:
            port = int(port)
            assert port in range(1, 65536)
        except Exception as e:
            e.args = [
                "Expecting an integer from 1 to 65535, found port={}".format(repr(port))
            ]
            raise

        # so we only see the "Running on" message once with hot reloading
        # https://stackoverflow.com/a/57231282/9188800
        if os.getenv("WERKZEUG_RUN_MAIN") != "true":
            ssl_context = flask_run_options.get("ssl_context")
            protocol = "https" if ssl_context else "http"
            path = self.config.requests_pathname_prefix

            if proxy:
                served_url, proxied_url = map(urlparse, proxy.split("::"))

                def verify_url_part(served_part, url_part, part_name):
                    if served_part != url_part:
                        raise ProxyError(
                            """
                            {0}: {1} is incompatible with the proxy:
                                {3}
                            To see your app at {4},
                            you must use {0}: {2}
                        """.format(
                                part_name,
                                url_part,
                                served_part,
                                proxy,
                                proxied_url.geturl(),
                            )
                        )

                verify_url_part(served_url.scheme, protocol, "protocol")
                verify_url_part(served_url.hostname, host, "host")
                verify_url_part(served_url.port, port, "port")

                display_url = (
                    proxied_url.scheme,
                    proxied_url.hostname,
                    (":{}".format(proxied_url.port) if proxied_url.port else ""),
                    path,
                )
            else:
                display_url = (protocol, host, ":{}".format(port), path)

            self.logger.info("Dash is running on %s://%s%s%s\n", *display_url)

        if self.config.extra_hot_reload_paths:
            extra_files = flask_run_options["extra_files"] = []
            for path in self.config.extra_hot_reload_paths:
                if os.path.isdir(path):
                    for dirpath, _, filenames in os.walk(path):
                        for fn in filenames:
                            extra_files.append(os.path.join(dirpath, fn))
                elif os.path.isfile(path):
                    extra_files.append(path)

        self.server.run(host=host, port=port, debug=debug, **flask_run_options)
