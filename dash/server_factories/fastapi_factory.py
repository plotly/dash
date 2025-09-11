import sys
import mimetypes
import hashlib
import inspect
import pkgutil
from contextvars import copy_context
import importlib.util
import time

try:
    import uvicorn
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import JSONResponse, PlainTextResponse
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import Response as StarletteResponse
    from starlette.datastructures import MutableHeaders
except ImportError:
    uvicorn = None
    FastAPI = Request = Response = None
    JSONResponse = PlainTextResponse = None
    StaticFiles = None
    StarletteResponse = None
    MutableHeaders = None

from dash.fingerprint import check_fingerprint
from dash import _validate
from dash.exceptions import PreventUpdate, InvalidResourceError
from dash.server_factories import set_request_adapter
from .base_factory import BaseServerFactory


class FastAPIServerFactory(BaseServerFactory):
    def __init__(self):
        self.config = {}
        super().__init__()

    def __call__(self, server, *args, **kwargs):
        # ASGI: (scope, receive, send)
        if len(args) == 3 and isinstance(args[0], dict) and "type" in args[0]:
            return server(*args, **kwargs)
        raise TypeError("FastAPI app must be called with (scope, receive, send)")

    def create_app(self, name="__main__", config=None):
        app = FastAPI()
        if config:
            for key, value in config.items():
                setattr(app.state, key, value)
        return app

    def register_assets_blueprint(
        self, app, blueprint_name, assets_url_path, assets_folder
    ):
        try:
            app.mount(
                assets_url_path,
                StaticFiles(directory=assets_folder),
                name=blueprint_name,
            )
        except RuntimeError:
            # directory doesnt exist
            pass

    def register_error_handlers(self, app):
        @app.exception_handler(PreventUpdate)
        async def _handle_error(_request, _exc):
            return Response(status_code=204)

        @app.exception_handler(InvalidResourceError)
        async def _invalid_resources_handler(_request, exc):
            return Response(content=exc.args[0], status_code=404)

    def register_prune_error_handler(self, app, secret, get_traceback_func):
        @app.exception_handler(Exception)
        async def _wrap_errors(_error_request, error):
            tb = get_traceback_func(secret, error)
            return PlainTextResponse(tb, status_code=500)

    def _html_response_wrapper(self, view_func):
        async def wrapped(*_args, **_kwargs):
            # If view_func is a function, call it; if it's a string, use it directly
            html = view_func() if callable(view_func) else view_func
            return Response(content=html, media_type="text/html")

        return wrapped

    def setup_index(self, app, dash_app):
        async def index(request: Request):
            adapter = FastAPIRequestAdapter()
            set_request_adapter(adapter)
            adapter.set_request(request)
            return Response(content=dash_app.render_index(), media_type="text/html")

        self.add_url_rule(app, "/", index, endpoint="index", methods=["GET"])

    def setup_catchall(self, app, dash_app):
        @dash_app.server.on_event("startup")
        def _setup_catchall():
            dash_app.enable_dev_tools(
                **self.config, first_run=False
            )  # do this to make sure dev tools are enabled

            async def catchall(request: Request):
                adapter = FastAPIRequestAdapter()
                set_request_adapter(adapter)
                adapter.set_request(request)
                return Response(content=dash_app.render_index(), media_type="text/html")

            self.add_url_rule(
                app, "/{path:path}", catchall, endpoint="catchall", methods=["GET"]
            )

    def add_url_rule(self, app, rule, view_func, endpoint=None, methods=None):
        if rule == "":
            rule = "/"
        if isinstance(view_func, str):
            # Wrap string or sync function to async FastAPI handler
            view_func = self._html_response_wrapper(view_func)
        app.add_api_route(
            rule,
            view_func,
            methods=methods or ["GET"],
            name=endpoint,
            include_in_schema=False,
        )

    def before_request(self, app, func):
        # FastAPI does not have before_request, but we can use middleware
        app.middleware("http")(self._make_before_middleware(func))

    def after_request(self, app, func):
        # FastAPI does not have after_request, but we can use middleware
        app.middleware("http")(self._make_after_middleware(func))

    def run(self, app, host, port, debug, **kwargs):
        frame = inspect.stack()[2]
        self.config = dict({"debug": debug} if debug else {}, **kwargs)
        reload = debug
        if reload:
            # Dynamically determine the module name from the file path
            file_path = frame.filename
            module_name = importlib.util.spec_from_file_location("app", file_path).name
            uvicorn.run(
                f"{module_name}:app.server",
                host=host,
                port=port,
                reload=reload,
                **kwargs,
            )
        else:
            uvicorn.run(app, host=host, port=port, reload=reload, **kwargs)

    def make_response(self, data, mimetype=None, content_type=None):
        headers = {}
        if mimetype:
            headers["content-type"] = mimetype
        if content_type:
            headers["content-type"] = content_type
        return Response(content=data, headers=headers)

    def jsonify(self, obj):
        return JSONResponse(content=obj)

    def get_request_adapter(self):
        return FastAPIRequestAdapter

    def _make_before_middleware(self, func):
        async def middleware(request, call_next):
            if func is not None:
                if inspect.iscoroutinefunction(func):
                    await func()
                else:
                    func()
            response = await call_next(request)
            return response

        return middleware

    def _make_after_middleware(self, func):
        async def middleware(request, call_next):
            response = await call_next(request)
            if func is not None:
                if inspect.iscoroutinefunction(func):
                    await func()
                else:
                    func()
            return response

        return middleware

    def serve_component_suites(
        self, dash_app, package_name, fingerprinted_path, request
    ):
        path_in_pkg, has_fingerprint = check_fingerprint(fingerprinted_path)
        _validate.validate_js_path(dash_app.registered_paths, package_name, path_in_pkg)
        extension = "." + path_in_pkg.split(".")[-1]
        mimetype = mimetypes.types_map.get(extension, "application/octet-stream")
        package = sys.modules[package_name]
        dash_app.logger.debug(
            "serving -- package: %s[%s] resource: %s => location: %s",
            package_name,
            package.__version__,
            path_in_pkg,
            package.__path__,
        )
        data = pkgutil.get_data(package_name, path_in_pkg)
        headers = {}
        if has_fingerprint:
            headers["Cache-Control"] = "public, max-age=31536000"
            return StarletteResponse(content=data, media_type=mimetype, headers=headers)
        etag = hashlib.md5(data).hexdigest() if data else ""
        headers["ETag"] = etag
        if request.headers.get("if-none-match") == etag:
            return StarletteResponse(status_code=304)
        return StarletteResponse(content=data, media_type=mimetype, headers=headers)

    def setup_component_suites(self, app, dash_app):
        async def serve(request: Request, package_name: str, fingerprinted_path: str):
            return self.serve_component_suites(
                dash_app, package_name, fingerprinted_path, request
            )

        dash_app._add_url(
            "/_dash-component-suites/<string:package_name>/<path:fingerprinted_path>",
            serve,
        )

    def dispatch(
        self, app, dash_app, use_async=False
    ):  # pylint: disable=unused-argument
        async def _dispatch(request: Request):
            adapter = FastAPIRequestAdapter()
            set_request_adapter(adapter)
            adapter.set_request(request)
            # pylint: disable=protected-access
            body = await request.json()
            g = dash_app._initialize_context(
                body, adapter
            )  # pylint: disable=protected-access
            func = dash_app._prepare_callback(
                g, body
            )  # pylint: disable=protected-access
            args = dash_app._inputs_to_vals(
                g.inputs_list + g.states_list
            )  # pylint: disable=protected-access
            ctx = copy_context()
            partial_func = dash_app._execute_callback(
                func, args, g.outputs_list, g
            )  # pylint: disable=protected-access
            response_data = ctx.run(partial_func)
            if inspect.iscoroutine(response_data):
                response_data = await response_data
            # Instead of set_data, return a new Response
            return Response(content=response_data, media_type="application/json")

        return _dispatch

    def _serve_default_favicon(self):
        return Response(
            content=pkgutil.get_data("dash", "favicon.ico"), media_type="image/x-icon"
        )

    def register_timing_hooks(self, app, first_run):
        if not first_run:
            return

        @app.middleware("http")
        async def timing_middleware(request, call_next):
            # Before request
            request.state.timing_information = {
                "__dash_server": {"dur": time.time(), "desc": None}
            }
            response = await call_next(request)
            # After request
            timing_information = getattr(request.state, "timing_information", None)
            if timing_information is not None:
                dash_total = timing_information.get("__dash_server", None)
                if dash_total is not None:
                    dash_total["dur"] = round((time.time() - dash_total["dur"]) * 1000)
                headers = MutableHeaders(response.headers)
                for name, info in timing_information.items():
                    value = name
                    if info.get("desc") is not None:
                        value += f';desc="{info["desc"]}"'
                    if info.get("dur") is not None:
                        value += f";dur={info['dur']}"
                    headers.append("Server-Timing", value)
            return response


class FastAPIRequestAdapter:
    def __init__(self):
        self._request = None

    def set_request(self, request: Request):
        self._request = request

    def get_root(self):
        return str(self._request.base_url)

    def get_args(self):
        return self._request.query_params

    async def get_json(self):
        return await self._request.json()

    def is_json(self):
        return self._request.headers.get("content-type", "").startswith(
            "application/json"
        )

    def get_cookies(self, _request=None):
        return self._request.cookies

    def get_headers(self):
        return self._request.headers

    def get_full_path(self):
        return str(self._request.url)

    def get_url(self):
        return str(self._request.url)

    def get_remote_addr(self):
        return self._request.client.host if self._request.client else None

    def get_origin(self):
        return self._request.headers.get("origin")

    def get_path(self):
        return self._request.url.path
