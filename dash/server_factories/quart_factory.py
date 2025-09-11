from .base_factory import BaseServerFactory
from quart import Quart, request, Response as QuartResponse, jsonify, send_from_directory
from dash.exceptions import PreventUpdate, InvalidResourceError
from dash.server_factories import set_request_adapter
from dash.fingerprint import check_fingerprint
from dash import _validate
from contextvars import copy_context
import inspect
import os
import pkgutil
import mimetypes
import hashlib
import sys


class QuartAPIServerFactory(BaseServerFactory):
    """Quart implementation of the Dash server factory.

    All Quart/async specific imports are at the top-level (per user request) so
    Quart must be installed when this module is imported.
    """

    def __init__(self) -> None:
        self.config = {}
        super().__init__()

    def __call__(self, server, *args, **kwargs):
        # ASGI style (scope, receive, send) or standard call-through handled by BaseServerFactory
        return super().__call__(server, *args, **kwargs)

    def create_app(self, name="__main__", config=None):
        app = Quart(name)
        if config:
            for key, value in config.items():
                # Mirror Flask usage of config dict
                app.config[key] = value
        return app

    def register_assets_blueprint(
        self, app, blueprint_name, assets_url_path, assets_folder
    ):
        if os.path.isdir(assets_folder):
            route = f"{assets_url_path}/<path:filename>"

            @app.route(route)
            async def serve_asset(filename):  # pragma: no cover - simple passthrough
                return await send_from_directory(assets_folder, filename)

    def register_error_handlers(self, app):
        @app.errorhandler(PreventUpdate)
        async def _prevent_update(_):
            return "", 204

        @app.errorhandler(InvalidResourceError)
        async def _invalid_resource(err):
            return err.args[0], 404

    def _html_response_wrapper(self, view_func):
        async def wrapped(*args, **kwargs):
            html_val = view_func() if callable(view_func) else view_func
            if inspect.iscoroutine(html_val):  # handle async function returning html
                html_val = await html_val
            html = str(html_val)
            return QuartResponse(html, content_type="text/html")

        return wrapped

    def add_url_rule(self, app, rule, view_func, endpoint=None, methods=None):
        if rule == "":
            rule = "/"
        if isinstance(view_func, str) or not inspect.iscoroutinefunction(view_func):
            # Wrap plain strings or sync callables in async handler returning HTML
            if isinstance(view_func, str) or not inspect.iscoroutinefunction(view_func):
                view_func = self._html_response_wrapper(view_func)
        app.add_url_rule(rule, endpoint or rule, view_func, methods=methods or ["GET"])

    # ---- Index & Catchall ------------------------------------------------
    def setup_index(self, app, dash_app):
        async def index():
            adapter = QuartRequestAdapter()
            set_request_adapter(adapter)
            return QuartResponse(dash_app.render_index(), content_type="text/html")

        self.add_url_rule(app, "/", index, endpoint="index", methods=["GET"])

    def setup_catchall(self, app, dash_app):
        @app.before_serving
        async def _enable_dev_tools():  # pragma: no cover - environmental
            dash_app.enable_dev_tools(**self.config)

        async def catchall(path):
            adapter = QuartRequestAdapter()
            set_request_adapter(adapter)
            return QuartResponse(dash_app.render_index(), content_type="text/html")

        # Must be added after other routes
        self.add_url_rule(
            app, "/<path:path>", catchall, endpoint="catchall", methods=["GET"]
        )

    # ---- Middleware-esque hooks -----------------------------------------
    def before_request(self, app, func):
        app.before_request(func)

    def after_request(self, app, func):
        # Quart after_request expects (response) -> response
        @app.after_request
        async def _after(response):
            if func is not None:
                result = func()
                if inspect.iscoroutine(result):  # Allow async hooks
                    await result
            return response

    # ---- Running ---------------------------------------------------------
    def run(self, app, host, port, debug, **kwargs):
        self.config = dict({'debug': debug} if debug else {}, **kwargs)
        app.run(host=host, port=port, debug=debug, **kwargs)

    # ---- Responses / JSON ------------------------------------------------
    def make_response(self, data, mimetype=None, content_type=None):
        headers = {}
        if mimetype:
            headers["Content-Type"] = mimetype
        if content_type:
            headers["Content-Type"] = content_type
        return QuartResponse(data, headers=headers)

    def jsonify(self, obj):
        return jsonify(obj)

    def get_request_adapter(self):
        return QuartRequestAdapter

    # ---- Component Suites ------------------------------------------------
    def serve_component_suites(
        self, dash_app, package_name, fingerprinted_path, req
    ):
        path_in_pkg, has_fingerprint = check_fingerprint(fingerprinted_path)
        _validate.validate_js_path(dash_app.registered_paths, package_name, path_in_pkg)
        extension = "." + path_in_pkg.split(".")[-1]
        mimetype = mimetypes.types_map.get(extension, "application/octet-stream")
        package = sys.modules[package_name]
        dash_app.logger.debug(
            "serving -- package: %s[%s] resource: %s => location: %s",
            package_name,
            getattr(package, "__version__", "unknown"),
            path_in_pkg,
            package.__path__,
        )
        data = pkgutil.get_data(package_name, path_in_pkg)
        headers = {}
        if has_fingerprint:
            headers["Cache-Control"] = "public, max-age=31536000"
            return QuartResponse(data, content_type=mimetype, headers=headers)
        etag = hashlib.md5(data).hexdigest() if data else ""
        headers["ETag"] = etag
        if req.headers.get("If-None-Match") == etag:
            return QuartResponse(None, status=304)
        return QuartResponse(data, content_type=mimetype, headers=headers)

    def setup_component_suites(self, app, dash_app):
        async def serve(package_name, fingerprinted_path):
            return self.serve_component_suites(
                dash_app, package_name, fingerprinted_path, request
            )

        self.add_url_rule(
            app,
            "/_dash-component-suites/<string:package_name>/<path:fingerprinted_path>",
            serve,
            methods=["GET"],
        )

    # ---- Dispatch (Callbacks) -------------------------------------------
    def dispatch(self, app, dash_app, use_async=True):  # Quart always async
        async def _dispatch():
            adapter = QuartRequestAdapter()
            set_request_adapter(adapter)
            body = await request.get_json()
            g = dash_app._initialize_context(body, adapter)
            func = dash_app._prepare_callback(g, body)
            args = dash_app._inputs_to_vals(g.inputs_list + g.states_list)
            ctx = copy_context()
            partial_func = dash_app._execute_callback(func, args, g.outputs_list, g)
            response_data = ctx.run(partial_func)
            if inspect.iscoroutine(response_data):  # if user callback is async
                response_data = await response_data
            return QuartResponse(response_data, content_type="application/json")

        return _dispatch

    # ---- Favicon ---------------------------------------------------------
    def _serve_default_favicon(self):
        return QuartResponse(
            pkgutil.get_data("dash", "favicon.ico"), content_type="image/x-icon"
        )


class QuartRequestAdapter:
    """Adapter that normalizes Quart's request API to what Dash expects."""

    @staticmethod
    def get_args():
        return request.args

    @staticmethod
    async def get_json():
        return await request.get_json()

    @staticmethod
    def is_json():
        return request.is_json

    @staticmethod
    def get_cookies():
        return request.cookies

    @staticmethod
    def get_headers():
        return request.headers

    @staticmethod
    def get_full_path():
        return request.full_path

    @staticmethod
    def get_remote_addr():
        return request.remote_addr

    @staticmethod
    def get_origin():
        return request.headers.get("Origin")

    @staticmethod
    def get_path():
        return request.path

