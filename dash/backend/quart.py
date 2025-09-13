import inspect
import pkgutil
import mimetypes
import sys
import time
from contextvars import copy_context

try:
    import quart
    from quart import Quart, Response, jsonify, request, Blueprint
except ImportError:
    quart = None
    Quart = None
    Response = None
    jsonify = None
    request = None
    Blueprint = None
from dash.exceptions import PreventUpdate, InvalidResourceError
from dash.backend import set_request_adapter
from dash.fingerprint import check_fingerprint
from dash import _validate
from .base_server import BaseDashServer


class QuartDashServer(BaseDashServer):
    """Quart implementation of the Dash server factory.

    All Quart/async specific imports are at the top-level (per user request) so
    Quart must be installed when this module is imported.
    """

    def __init__(self) -> None:
        self.config = {}
        super().__init__()

    def __call__(self, server, *args, **kwargs):
        return server(*args, **kwargs)

    def create_app(self, name="__main__", config=None):
        app = Quart(name)
        if config:
            for key, value in config.items():
                app.config[key] = value
        return app

    def register_assets_blueprint(
        self, app, blueprint_name, assets_url_path, assets_folder
    ):
        bp = Blueprint(
            blueprint_name,
            __name__,
            static_folder=assets_folder,
            static_url_path=assets_url_path,
        )
        app.register_blueprint(bp)

    def register_prune_error_handler(self, app, secret, get_traceback_func):
        @app.errorhandler(Exception)
        async def _wrap_errors(_error_request, error):
            tb = get_traceback_func(secret, error)
            return tb, 500

    def register_timing_hooks(self, app, _first_run):  # parity with Flask factory
        @app.before_request
        async def _before_request():  # pragma: no cover - timing infra
            quart.g.timing_information = {
                "__dash_server": {"dur": time.time(), "desc": None}
            }

        @app.after_request
        async def _after_request(response):  # pragma: no cover - timing infra
            timing_information = getattr(quart.g, "timing_information", None)
            if timing_information is None:
                return response
            dash_total = timing_information.get("__dash_server", None)
            if dash_total is not None:
                dash_total["dur"] = round((time.time() - dash_total["dur"]) * 1000)
            for name, info in timing_information.items():
                value = name
                if info.get("desc") is not None:
                    value += f';desc="{info["desc"]}"'
                if info.get("dur") is not None:
                    value += f";dur={info['dur']}"
                # Quart/Werkzeug headers expose 'add' (not 'append')
                if hasattr(response.headers, "add"):
                    response.headers.add("Server-Timing", value)
                else:  # fallback just in case
                    response.headers["Server-Timing"] = value
            return response

    def register_error_handlers(self, app):
        @app.errorhandler(PreventUpdate)
        async def _prevent_update(_):
            return "", 204

        @app.errorhandler(InvalidResourceError)
        async def _invalid_resource(err):
            return err.args[0], 404

    def _html_response_wrapper(self, view_func):
        async def wrapped(*_args, **_kwargs):
            html_val = view_func() if callable(view_func) else view_func
            if inspect.iscoroutine(html_val):  # handle async function returning html
                html_val = await html_val
            html = str(html_val)
            return Response(html, content_type="text/html")

        return wrapped

    def add_url_rule(self, app, rule, view_func, endpoint=None, methods=None):
        app.add_url_rule(
            rule, view_func=view_func, endpoint=endpoint, methods=methods or ["GET"]
        )

    def setup_index(self, dash_app):
        async def index(*args, **kwargs):
            adapter = QuartRequestAdapter()
            set_request_adapter(adapter)
            adapter.set_request()
            return Response(dash_app.index(*args, **kwargs), content_type="text/html")

        # pylint: disable=protected-access
        dash_app._add_url("", index, methods=["GET"])

    def setup_catchall(self, dash_app):
        async def catchall(
            path, *args, **kwargs
        ):  # noqa: ARG001 - path is unused but kept for route signature, pylint: disable=unused-argument
            adapter = QuartRequestAdapter()
            set_request_adapter(adapter)
            adapter.set_request()
            return Response(dash_app.index(*args, **kwargs), content_type="text/html")

        # pylint: disable=protected-access
        dash_app._add_url("<path:path>", catchall, methods=["GET"])

    def before_request(self, app, func):
        app.before_request(func)

    def after_request(self, app, func):
        @app.after_request
        async def _after(response):
            if func is not None:
                result = func()
                if inspect.iscoroutine(result):  # Allow async hooks
                    await result
            return response

    def run(self, app, host, port, debug, **kwargs):
        self.config = {"debug": debug, **kwargs} if debug else kwargs
        app.run(host=host, port=port, debug=debug, **kwargs)

    def make_response(self, data, mimetype=None, content_type=None):
        return Response(data, mimetype=mimetype, content_type=content_type)

    def jsonify(self, obj):
        return jsonify(obj)

    def get_request_adapter(self):
        return QuartRequestAdapter

    def serve_component_suites(
        self, dash_app, package_name, fingerprinted_path
    ):  # noqa: ARG002 unused req preserved for interface parity
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

        return Response(data, content_type=mimetype, headers=headers)

    def setup_component_suites(self, dash_app):
        async def serve(package_name, fingerprinted_path):
            return self.serve_component_suites(
                dash_app, package_name, fingerprinted_path
            )

        # pylint: disable=protected-access
        dash_app._add_url(
            "_dash-component-suites/<string:package_name>/<path:fingerprinted_path>",
            serve,
        )

    # pylint: disable=unused-argument
    def dispatch(self, app, dash_app, use_async=True):  # Quart always async
        async def _dispatch():
            adapter = QuartRequestAdapter()
            set_request_adapter(adapter)
            adapter.set_request()
            body = await request.get_json()
            # pylint: disable=protected-access
            g = dash_app._initialize_context(body, adapter)
            # pylint: disable=protected-access
            func = dash_app._prepare_callback(g, body)
            # pylint: disable=protected-access
            args = dash_app._inputs_to_vals(g.inputs_list + g.states_list)
            ctx = copy_context()
            # pylint: disable=protected-access
            partial_func = dash_app._execute_callback(func, args, g.outputs_list, g)
            response_data = ctx.run(partial_func)
            if inspect.iscoroutine(response_data):  # if user callback is async
                response_data = await response_data
            return Response(response_data, content_type="application/json")

        return _dispatch

    def register_callback_api_routes(self, app, callback_api_paths):
        """
        Register callback API endpoints on the Quart app.
        Each key in callback_api_paths is a route, each value is a handler (sync or async).
        The view function parses the JSON body and passes it to the handler.
        """
        for path, handler in callback_api_paths.items():
            endpoint = f"dash_callback_api_{path}"
            route = path if path.startswith("/") else f"/{path}"
            methods = ["POST"]

            def _make_view_func(handler):
                if inspect.iscoroutinefunction(handler):

                    async def async_view_func(*args, **kwargs):
                        data = await request.get_json()
                        result = await handler(**data) if data else await handler()
                        return jsonify(result)

                    return async_view_func

                async def sync_view_func(*args, **kwargs):
                    data = await request.get_json()
                    result = handler(**data) if data else handler()
                    return jsonify(result)

                return sync_view_func

            view_func = _make_view_func(handler)
            app.add_url_rule(
                route, endpoint=endpoint, view_func=view_func, methods=methods
            )

    def _serve_default_favicon(self):
        return Response(
            pkgutil.get_data("dash", "favicon.ico"), content_type="image/x-icon"
        )


class QuartRequestAdapter:
    def __init__(self) -> None:
        self._request = None

    def set_request(self) -> None:
        self._request = request

    # Accessors (instance-based)
    def get_root(self):
        return self._request.root_url

    def get_args(self):
        return self._request.args

    async def get_json(self):
        return await self._request.get_json()

    def is_json(self):
        return self._request.is_json

    def get_cookies(self):
        return self._request.cookies

    def get_headers(self):
        return self._request.headers

    def get_full_path(self):
        return self._request.full_path

    def get_url(self):
        return str(self._request.url)

    def get_remote_addr(self):
        return self._request.remote_addr

    def get_origin(self):
        return self._request.headers.get("origin")

    def get_path(self):
        return self._request.path
