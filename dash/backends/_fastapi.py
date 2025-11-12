from __future__ import annotations

import asyncio
from contextvars import copy_context, ContextVar
from typing import TYPE_CHECKING, Any, Callable, Dict
import sys
import mimetypes
import hashlib
import inspect
import pkgutil
import time
from importlib.util import spec_from_file_location
import json
import os

try:
    from fastapi import FastAPI, Request, Response, Body
    from fastapi.responses import JSONResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import Response as StarletteResponse
    from starlette.datastructures import MutableHeaders
    from starlette.types import ASGIApp, Scope, Receive, Send
    import uvicorn
except ImportError:
    FastAPI = None
    Request = None
    Response = None
    Body = None
    JSONResponse = None
    RedirectResponse = None
    StaticFiles = None
    StarletteResponse = None
    MutableHeaders = None
    ASGIApp = None
    Scope = None
    Receive = None
    Send = None
    uvicorn = None

from dash.fingerprint import check_fingerprint
from dash import _validate
from dash.exceptions import PreventUpdate
from .base_server import BaseDashServer, RequestAdapter
from ._utils import format_traceback_html

if TYPE_CHECKING:  # pragma: no cover - typing only
    from dash import Dash


_current_request_var = ContextVar("dash_current_request", default=None)


def set_current_request(req):
    return _current_request_var.set(req)


def reset_current_request(token):
    _current_request_var.reset(token)


def get_current_request() -> Request:
    req = _current_request_var.get()
    if req is None:
        raise RuntimeError("No active request in context")
    return req


class CurrentRequestMiddleware:  # pylint: disable=too-few-public-methods
    def __init__(self, app: ASGIApp) -> None:  # type: ignore[name-defined]
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # type: ignore[name-defined]
        # non-http/ws scopes pass through (lifespan etc.)
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        token = set_current_request(request)
        try:
            await self.app(scope, receive, send)
        finally:
            reset_current_request(token)


# Internal config helpers (local to this file)
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "dash_config.json")


def _save_config(config):
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f)


def _load_config():
    resp = {"debug": False}
    try:
        if os.path.exists(_CONFIG_PATH):
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                resp = json.load(f)
    except (json.JSONDecodeError, OSError):
        pass  # ignore errors
    return resp


def _remove_config():
    try:
        os.remove(_CONFIG_PATH)
    except FileNotFoundError:
        pass


class FastAPIDashServer(BaseDashServer):
    def __init__(self, server: FastAPI):
        self.server_type = "fastapi"
        self.server: FastAPI = server
        self.error_handling_mode = "ignore"
        self.request_adapter = FastAPIRequestAdapter
        self._before_request_funcs = []
        super().__init__()

    def __call__(self, *args: Any, **kwargs: Any):
        # ASGI: (scope, receive, send)
        if len(args) == 3 and isinstance(args[0], dict) and "type" in args[0]:
            return self.server(*args, **kwargs)
        raise TypeError("FastAPI app must be called with (scope, receive, send)")

    @staticmethod
    def create_app(name: str = "__main__", config: Dict[str, Any] | None = None):
        app = FastAPI()

        if config:
            for key, value in config.items():
                setattr(app.state, key, value)
        return app

    def register_assets_blueprint(
        self, blueprint_name: str, assets_url_path: str, assets_folder: str
    ):
        try:
            self.server.mount(
                assets_url_path,
                StaticFiles(directory=assets_folder),
                name=blueprint_name,
            )
        except RuntimeError:
            # directory doesnt exist
            pass

    def register_error_handlers(self):
        self.error_handling_mode = "ignore"

    def _get_traceback(self, _secret, error: Exception):
        return format_traceback_html(
            error, self.error_handling_mode, "FastAPI Debugger", "FastAPI"
        )

    def register_prune_error_handler(self, _secret, prune_errors):
        if prune_errors:
            self.error_handling_mode = "prune"
        else:
            self.error_handling_mode = "raise"

    def _html_response_wrapper(self, view_func: Callable[..., Any] | str):
        async def wrapped(*_args, **_kwargs):
            # If view_func is a function, call it; if it's a string, use it directly
            html = view_func() if callable(view_func) else view_func
            return Response(content=html, media_type="text/html")

        return wrapped

    def setup_index(self, dash_app: Dash):
        async def index(_request: Request):
            return Response(content=dash_app.index(), media_type="text/html")

        # pylint: disable=protected-access
        dash_app._add_url("", index, methods=["GET"])

    def setup_catchall(self, dash_app: Dash):
        @self.server.on_event("shutdown")
        def cleanup_config():
            _remove_config()

        @self.server.on_event("startup")
        def _setup_catchall():
            dash_app.enable_dev_tools(
                **_load_config(), first_run=False
            )  # do this to make sure dev tools are enabled

            async def catchall(_request: Request):
                return Response(content=dash_app.index(), media_type="text/html")

            # pylint: disable=protected-access
            dash_app._add_url("{path:path}", catchall, methods=["GET"])

    def add_url_rule(
        self,
        rule: str,
        view_func: Callable[..., Any] | str,
        endpoint: str | None = None,
        methods: list[str] | None = None,
        include_in_schema: bool = False,
    ):
        if rule == "":
            rule = "/"
        if isinstance(view_func, str):
            # Wrap string or sync function to async FastAPI handler
            view_func = self._html_response_wrapper(view_func)
        self.server.add_api_route(
            rule,
            view_func,
            methods=methods or ["GET"],
            name=endpoint,
            include_in_schema=include_in_schema,
        )

    def before_request(self, func: Callable[[], Any] | None):
        if func is not None:
            self._before_request_funcs.append(func)
        # Only add the middleware once
        if not hasattr(self, "_before_middleware_added"):
            self.server.add_middleware(CurrentRequestMiddleware)
            self.server.middleware("http")(self._make_before_middleware())
            self._before_middleware_added = True

    def after_request(self, func: Callable[[], Any] | None):
        # FastAPI does not have after_request, but we can use middleware
        self.server.middleware("http")(self._make_after_middleware(func))

    def has_request_context(self) -> bool:
        try:
            get_current_request()
            return True
        except RuntimeError:
            return False

    def run(self, dash_app: Dash, host, port, debug, **kwargs):
        frame = inspect.stack()[2]
        dev_tools = dash_app._dev_tools  # pylint: disable=protected-access
        config = dict(
            {"debug": debug} if debug else {"debug": False},
            **{f"dev_tools_{k}": v for k, v in dev_tools.items()},
        )
        _save_config(config)
        if debug:
            if kwargs.get("reload") is None:
                kwargs["reload"] = True
        if kwargs.get("reload"):
            # Dynamically determine the module name from the file path
            file_path = frame.filename
            spec = spec_from_file_location("app", file_path)
            module_name = spec.name if spec and getattr(spec, "name", None) else "app"
            uvicorn.run(
                f"{module_name}:app.server",
                host=host,
                port=port,
                **kwargs,
            )
        else:
            uvicorn.run(self.server, host=host, port=port, **kwargs)

    def make_response(
        self,
        data: str | bytes | bytearray,
        mimetype: str | None = None,
        content_type: str | None = None,
    ):
        headers = {}
        if mimetype:
            headers["content-type"] = mimetype
        if content_type:
            headers["content-type"] = content_type
        return Response(content=data, headers=headers)

    def jsonify(self, obj: Any):
        return JSONResponse(content=obj)

    def _make_before_middleware(self):
        async def middleware(request, call_next):
            for func in self._before_request_funcs:
                if inspect.iscoroutinefunction(func):
                    await func()
                else:
                    func()
            try:
                response = await call_next(request)
                return response
            except PreventUpdate:
                return Response(status_code=204)
            except Exception as e:
                if self.error_handling_mode in ["raise", "prune"]:
                    tb = self._get_traceback(None, e)
                    return Response(content=tb, media_type="text/html", status_code=500)
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "InternalServerError",
                        "message": "An internal server error occurred.",
                    },
                )

        return middleware

    def _make_after_middleware(self, func: Callable[[], Any] | None):
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
        self,
        dash_app: Dash,
        package_name: str,
        fingerprinted_path: str,
        request: Request,
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

    def setup_component_suites(self, dash_app: Dash):
        async def serve(request: Request, package_name: str, fingerprinted_path: str):
            return self.serve_component_suites(
                dash_app, package_name, fingerprinted_path, request
            )

        name = "_dash-component-suites/{package_name}/{fingerprinted_path:path}"
        dash_app._add_url(name, serve)  # pylint: disable=protected-access

    def _create_redirect_function(self, redirect_to):
        def _redirect():
            return RedirectResponse(url=redirect_to, status_code=301)

        return _redirect

    def add_redirect_rule(self, app, fullname, path):
        self.server.add_api_route(
            fullname,
            self._create_redirect_function(app.get_relative_path(path)),
            methods=["GET"],
            name=fullname,
            include_in_schema=False,
        )

    def dispatch(self, dash_app: Dash):
        async def _dispatch(request: Request):
            # pylint: disable=protected-access
            body = await request.json()
            cb_ctx = dash_app._initialize_context(
                body
            )  # pylint: disable=protected-access
            func = dash_app._prepare_callback(
                cb_ctx, body
            )  # pylint: disable=protected-access
            args = dash_app._inputs_to_vals(
                cb_ctx.inputs_list + cb_ctx.states_list
            )  # pylint: disable=protected-access
            ctx = copy_context()
            partial_func = dash_app._execute_callback(
                func, args, cb_ctx.outputs_list, cb_ctx
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

    def register_timing_hooks(self, first_run: bool):
        if not first_run:
            return

        @self.server.middleware("http")
        async def timing_middleware(request: Request, call_next):
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

    def register_callback_api_routes(
        self, callback_api_paths: Dict[str, Callable[..., Any]]
    ):
        """
        Register callback API endpoints on the FastAPI app.
        Each key in callback_api_paths is a route, each value is a handler (sync or async).
        Accepts a JSON body (dict) and filters keys based on the handler's signature.
        """
        for path, handler in callback_api_paths.items():
            endpoint = f"dash_callback_api_{path}"
            route = path if path.startswith("/") else f"/{path}"
            methods = ["POST"]
            sig = inspect.signature(handler)
            param_names = list(sig.parameters.keys())

            def make_view_func(handler, param_names):
                async def view_func(_request: Request, body: dict = Body(...)):
                    kwargs = {
                        k: v
                        for k, v in body.items()
                        if k in param_names and v is not None
                    }
                    if inspect.iscoroutinefunction(handler):
                        result = await handler(**kwargs)
                    else:
                        result = handler(**kwargs)
                    return JSONResponse(content=result)

                return view_func

            self.server.add_api_route(
                route,
                make_view_func(handler, param_names),
                methods=methods,
                name=endpoint,
                include_in_schema=True,
            )

    def enable_compression(self) -> None:
        from fastapi.middleware.gzip import GZipMiddleware

        self.server.add_middleware(GZipMiddleware, minimum_size=500)
        config = _load_config()
        if "COMPRESS_ALGORITHM" not in config:
            config["COMPRESS_ALGORITHM"] = ["gzip"]

        _save_config(config)


class FastAPIRequestAdapter(RequestAdapter):
    def __init__(self):
        self._request: Request = get_current_request()
        super().__init__()

    def __call__(self):
        self._request = get_current_request()
        return self

    @property
    def context(self):
        if self._request is None:
            raise RuntimeError("No active request in context")

        return self._request.state

    @property
    def root(self):
        return str(self._request.base_url)

    @property
    def args(self):
        return self._request.query_params

    @property
    def is_json(self):
        return self._request.headers.get("content-type", "").startswith(
            "application/json"
        )

    @property
    def cookies(self):
        return self._request.cookies

    @property
    def headers(self):
        return self._request.headers

    @property
    def full_path(self):
        return str(self._request.url)

    @property
    def url(self):
        return str(self._request.url)

    @property
    def remote_addr(self):
        client = getattr(self._request, "client", None)
        return getattr(client, "host", None)

    @property
    def origin(self):
        return self._request.headers.get("origin")

    @property
    def path(self):
        return self._request.url.path

    def get_json(self):
        return asyncio.run(self._request.json())
