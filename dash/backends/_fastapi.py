from __future__ import annotations

from contextvars import copy_context, ContextVar
import asyncio
import concurrent.futures
import json
import queue
from typing import TYPE_CHECKING, Any, Callable, Dict
import sys
import mimetypes
import hashlib
import inspect
import pkgutil
import time
import os
import subprocess
import threading
import traceback
from urllib.parse import urlparse

try:
    from fastapi import FastAPI, Request, Response, Body
    from fastapi.responses import JSONResponse, RedirectResponse
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import Response as StarletteResponse
    from starlette.datastructures import MutableHeaders
    from starlette.types import ASGIApp, Scope, Receive, Send
    from starlette.websockets import WebSocket, WebSocketDisconnect
    import uvicorn
except ImportError as _err:
    raise ImportError(
        "All dependencies not installed. Please install it with `dash[fastapi]` to use the FastAPI backend."
    ) from _err

import janus

from dash.fingerprint import check_fingerprint
from dash import _validate, get_app
from dash.exceptions import PreventUpdate
from .base_server import (
    BaseDashServer,
    RequestAdapter,
    ResponseAdapter,
)
from .ws import (
    DashWebsocketCallback,
    run_ws_sender,
    run_callback_in_executor,
    make_callback_done_handler,
    SHUTDOWN_SIGNAL,
    DISCONNECTED,
)
from ._utils import format_traceback_html

if TYPE_CHECKING:  # pragma: no cover - typing only
    from dash import Dash


class FastAPIResponseAdapter(ResponseAdapter):
    """
    A custom Response class that wraps FastAPI's JSONResponse
    and provides a set_response() method for compatibility with Dash's callback system.
    """

    @property
    def callback_response(self):
        """Get the response object to be returned from a callback."""
        print(
            "Cannot access callback_response directly on FastAPIResponseAdapter. Use set_response() to create a response with data."
        )
        raise NotImplementedError()

    def set_response(self, **kwargs):
        """
        Set the response data. This method provides compatibility with Flask's Response.set_data().
        """
        data = kwargs.get("data")
        if isinstance(data, (str, bytes, bytearray)):
            resp = Response(content=data)
        else:
            resp = JSONResponse(content=data)
        if self._headers:
            for key, value in self._headers.items():
                if isinstance(value, list):
                    for v in value:
                        resp.headers.append(key, v)
                else:
                    resp.headers[key] = value
        if self._cookies:
            for key, (value, cookie_kwargs) in self._cookies.items():
                resp.set_cookie(key, value, **cookie_kwargs)
        return resp


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


_ENV_CONFIG = "_DASH_FASTAPI_CONFIG"


class DashMiddleware:  # pylint: disable=too-few-public-methods
    """Consolidated middleware for all Dash/FastAPI integration needs."""

    def __init__(
        self,
        app: ASGIApp,
        dash_app: Dash,
        dash_server: FastAPIDashServer,
        before_request_funcs: list,
        after_request_func: Callable | None = None,
        enable_timing: bool = False,
    ) -> None:
        self.app = app
        self.dash_app = dash_app
        self.dash_server = dash_server
        self.before_request_funcs = before_request_funcs
        self.after_request_func = after_request_func
        self.enable_timing = enable_timing
        self._dev_tools_initialized = False

    async def _initialize_dev_tools(self) -> None:
        """Initialize dev tools from environment config on first run."""
        if not self._dev_tools_initialized:
            config = json.loads(os.getenv(_ENV_CONFIG, "{}"))
            if config:
                self.dash_app.enable_dev_tools(**config, first_run=False)
            self._dev_tools_initialized = True

    async def _setup_timing(self, request: Request) -> None:
        """Set up timing information for the request."""
        try:
            request.state.json_body = (
                await request.json()
                if request.headers.get("content-type", "").startswith(
                    "application/json"
                )
                else None
            )
        except Exception:  # pylint: disable=broad-exception-caught
            request.state.json_body = None
        if self.enable_timing:
            request.state.timing_information = {
                "__dash_server": {"dur": time.time(), "desc": None}
            }

    async def _run_before_hooks(self) -> None:
        """Run all before-request hooks."""
        for func in self.before_request_funcs:
            if inspect.iscoroutinefunction(func):
                await func()
            else:
                func()

    async def _run_after_hooks(self) -> None:
        """Run after-request hook if configured."""
        if self.after_request_func is not None:
            if inspect.iscoroutinefunction(self.after_request_func):
                await self.after_request_func()
            else:
                self.after_request_func()

    def _finalize_timing(self, request: Request) -> dict | None:
        """Calculate final timing information and return headers to add."""
        if not self.enable_timing or not hasattr(request.state, "timing_information"):
            return None

        timing_information = request.state.timing_information
        dash_total = timing_information.get("__dash_server", None)
        if dash_total is not None:
            dash_total["dur"] = round((time.time() - dash_total["dur"]) * 1000)

        return timing_information

    async def _handle_error(
        self, error: Exception, scope: Scope, receive: Receive, send: Send
    ) -> None:
        """Handle exceptions during request processing."""
        if isinstance(error, PreventUpdate):
            response = Response(status_code=204)
        elif self.dash_server.error_handling_mode in ["raise", "prune"]:
            tb = self.dash_server._get_traceback(None, error)  # pylint: disable=W0212
            response = Response(content=tb, media_type="text/html", status_code=500)
        else:
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "InternalServerError",
                    "message": "An internal server error occurred.",
                },
            )
        await response(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Handle lifespan events (startup/shutdown)

        if scope["type"] == "lifespan":
            try:
                dash_app = get_app()
                dash_app.backend._setup_catchall()
            except Exception:  # pylint: disable=broad-exception-caught
                traceback.print_exc()
            await self._initialize_dev_tools()
            await self.app(scope, receive, send)
            return

        # Non-HTTP/WebSocket scopes pass through
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Non-Dash routes pass through to avoid consuming body stream
        path = scope["path"]
        prefix = self.dash_app.config.routes_pathname_prefix
        dash_prefix = prefix.rstrip("/") + "/_dash-"
        if (
            not path.startswith(dash_prefix)
            and path != prefix
            and path != prefix.rstrip("/")
        ):
            await self.app(scope, receive, send)
            return

        # HTTP request handling
        request = Request(scope, receive=receive)
        token = set_current_request(request)

        try:
            await self._setup_timing(request)
            await self._run_before_hooks()

            await self.app(scope, receive, send)

            await self._run_after_hooks()
            self._finalize_timing(request)

        except Exception as e:  # pylint: disable=W0718
            await self._handle_error(e, scope, receive, send)
        finally:
            reset_current_request(token)


class FastAPIDashServer(BaseDashServer[FastAPI]):
    websocket_capability: bool = True

    def __init__(self, server: FastAPI):
        super().__init__(server)
        self.server_type = "fastapi"
        self.error_handling_mode = "ignore"
        self.request_adapter = FastAPIRequestAdapter
        self.response_adapter = FastAPIResponseAdapter
        self._before_request_funcs = []
        self._after_request_func = None
        self._enable_timing = False

    def __call__(self, *args: Any, **kwargs: Any):
        # ASGI: pass through to FastAPI
        return self.server(*args, **kwargs)

    @staticmethod
    # pylint: disable=W0613
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
        """This is needed to ensure that all routes are handled by FastAPI
        and passed through the middleware, which is necessary for features like authentication
        and timing to work correctly on all routes. FastAPI will match this catch-all route
        for any path that isn't matched by a more specific route, allowing the middleware to
        process the request and then return the appropriate response (e.g., 404 if no Dash route matches)."""

    def _setup_catchall(self):
        try:
            dash_app = get_app()

            async def catchall(_request: Request):
                return Response(content=dash_app.index(), media_type="text/html")

            # pylint: disable=protected-access
            self.add_url_rule("{path:path}", catchall, methods=["GET"])
        except Exception:  # pylint: disable=broad-exception-caught
            traceback.print_exc()

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

    def after_request(self, func: Callable[[], Any] | None):
        self._after_request_func = func

    def has_request_context(self) -> bool:
        try:
            get_current_request()
            return True
        except RuntimeError:
            return False

    def run(self, dash_app: Dash, host, port, debug, **kwargs):  # pylint: disable=R0912
        frame = inspect.stack()[2]
        if debug and kwargs.get("reload") is None:
            kwargs["reload"] = True

        # Check if we're running in a thread (e.g., from testing framework)
        # If so, run uvicorn directly instead of spawning a subprocess
        is_threaded = threading.current_thread() != threading.main_thread()

        if is_threaded:
            # Running in a thread (testing context) - use uvicorn.Server
            # This allows graceful shutdown via should_exit flag
            kwargs.pop("reload", None)  # Reload not supported in threaded mode
            config = uvicorn.Config(self.server, host=host, port=port, **kwargs)
            server = uvicorn.Server(config)
            # Store server reference on the app for graceful shutdown
            dash_app._uvicorn_server = server  # pylint: disable=protected-access
            server.run()
        else:
            # Running in main thread (normal context) - use subprocess
            file_path = frame.filename
            rel_path = os.path.relpath(file_path, os.getcwd())

            # Check if the file is outside the current working directory
            if rel_path.startswith(".."):
                # File is outside cwd, try to find the module name from sys.modules
                module_name = None
                for mod_name, mod in sys.modules.items():
                    if hasattr(mod, "__file__") and mod.__file__:
                        if os.path.abspath(mod.__file__) == os.path.abspath(file_path):
                            module_name = mod_name
                            break

                # If we still can't find it, raise an error
                if not module_name:
                    raise RuntimeError(
                        f"Cannot determine module name for {file_path}. "
                        "The file is outside the current working directory and not found in sys.modules. "
                        "Please ensure the FastAPI app is being run from a file within the current working directory."
                    )
            else:
                # File is within cwd, use relative path
                module_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")

            # Find the Dash app variable name by inspecting the calling frame
            dash_var_name = None
            calling_frame = frame.frame
            for var_name, var_value in calling_frame.f_locals.items():
                if var_value is dash_app:
                    dash_var_name = var_name
                    break

            # If not found in locals, check globals
            if not dash_var_name:
                for var_name, var_value in calling_frame.f_globals.items():
                    if var_value is dash_app:
                        dash_var_name = var_name
                        break

            # Construct the app path - use .server to access the FastAPI instance
            if dash_var_name:
                app_path = f"{module_name}:{dash_var_name}.server"
            else:
                # Fallback to looking for 'server' variable (old behavior)
                app_path = f"{module_name}:server"

            uvicorn_args = [
                sys.executable,
                "-m",
                "uvicorn",
                app_path,
                "--host",
                str(host),
                "--port",
                str(port),
            ]
            if kwargs.get("reload"):
                uvicorn_args.append("--reload")

            dev_tools = dash_app._dev_tools  # pylint: disable=W0212
            config = dict(
                {"debug": debug} if debug else {"debug": False},
                **{f"dev_tools_{k}": v for k, v in dev_tools.items()},
            )
            env = os.environ.copy()
            env[_ENV_CONFIG] = json.dumps(config)

            # Add any other kwargs as CLI args if needed

            # pylint: disable=R1732
            proc = subprocess.Popen(uvicorn_args, env=env)
            proc.wait()

    def make_response(
        self,
        data: str | bytes | bytearray,
        mimetype: str | None = None,
        content_type: str | None = None,
        status: int | None = None,
    ):
        headers = {}
        if mimetype:
            headers["content-type"] = mimetype
        if content_type:
            headers["content-type"] = content_type
        return Response(content=data, headers=headers, status_code=status or 200)

    def jsonify(self, obj: Any):
        return JSONResponse(content=obj)

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

    def serve_callback(self, dash_app: Dash):
        async def _dispatch(request: Request):  # pylint: disable=unused-argument
            # pylint: disable=protected-access
            body = self.request_adapter().get_json()
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
            return cb_ctx.dash_response.set_response(data=response_data)

        return _dispatch

    def register_timing_hooks(self, first_run: bool):
        if first_run:
            self._enable_timing = True

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
        # pylint: disable=import-outside-toplevel,import-error
        from fastapi.middleware.gzip import (
            GZipMiddleware,
        )

        self.server.add_middleware(GZipMiddleware, minimum_size=500)

    def setup_backend(self, dash_app: Dash):
        # Add consolidated middleware for all Dash functionality
        self.server.add_middleware(
            DashMiddleware,
            dash_app=dash_app,
            dash_server=self,
            before_request_funcs=self._before_request_funcs,
            after_request_func=self._after_request_func,
            enable_timing=self._enable_timing,
        )

        # Add timing middleware separately if enabled (needs to modify response headers)
        if self._enable_timing:

            @self.server.middleware("http")
            async def timing_headers_middleware(request: Request, call_next):
                response = await call_next(request)
                timing_information = getattr(request.state, "timing_information", None)
                if timing_information is not None:
                    headers = MutableHeaders(response.headers)
                    for name, info in timing_information.items():
                        value = name
                        if info.get("desc") is not None:
                            value += f';desc="{info["desc"]}"'
                        if info.get("dur") is not None:
                            value += f";dur={info['dur']}"
                        headers.append("Server-Timing", value)
                return response

    async def _run_ws_hooks(
        self, hooks, websocket: "WebSocket", *args, default_reason: str = "Rejected"
    ) -> tuple | None:
        """Run WebSocket hooks and return rejection tuple or None if all pass.

        Args:
            hooks: List of hooks to run
            websocket: The WebSocket connection
            *args: Additional arguments to pass to hooks
            default_reason: Default reason if hook returns False

        Returns:
            None if all hooks pass, or (code, reason) tuple for rejection
        """
        for hook in hooks:
            try:
                result = hook(websocket, *args)
                if inspect.iscoroutine(result):
                    result = await result
                if result is False:
                    return (4001, default_reason)
                if isinstance(result, tuple) and len(result) == 2:
                    return result
            except Exception:  # pylint: disable=broad-exception-caught
                return (4001, "Authentication error")
        return None

    def serve_websocket_callback(self, dash_app: "Dash"):
        """Set up the WebSocket endpoint for callback handling.

        Uses thread pool executor for callback execution with janus queues
        for async/sync communication between main loop and worker threads.

        Args:
            dash_app: The Dash application instance
        """
        # pylint: disable=too-many-statements,too-many-locals
        ws_path = dash_app.config.requests_pathname_prefix + "_dash-ws-callback"

        # Get allowed origins from dash app config
        allowed_origins = getattr(
            dash_app, "_websocket_allowed_origins", []
        )  # pylint: disable=protected-access

        def validate_origin(origin: str | None, host: str | None) -> str | None:
            """Validate WebSocket origin. Returns error message or None if valid."""
            if not origin:
                return "Origin header required"
            if origin in allowed_origins:
                return None  # Explicitly allowed
            if not host:
                return "Origin not allowed"
            # Check same-origin
            origin_host = urlparse(origin).netloc
            if origin_host != host:
                return "Origin not allowed"
            return None

        async def websocket_handler(websocket: WebSocket):
            # Validate Origin header to prevent Cross-Site WebSocket Hijacking
            origin = websocket.headers.get("origin")
            host = websocket.headers.get("host")
            error = validate_origin(origin, host)
            if error:
                await websocket.close(code=4003, reason=error)
                return

            # Call websocket_connect hooks (before accept)
            # pylint: disable=protected-access
            rejection = await self._run_ws_hooks(
                dash_app._hooks.get_hooks("websocket_connect"),
                websocket,
                default_reason="Connection rejected",
            )
            if rejection:
                await websocket.close(code=rejection[0], reason=rejection[1])
                return

            await websocket.accept()

            # Capture request metadata from the WebSocket handshake once per
            # connection so that callbacks running over the WebSocket transport
            # can access cookies/headers (e.g. for authentication helpers such
            # as dash_enterprise_auth.get_user_data).
            request_context = {
                "cookies": dict(websocket.cookies),
                "headers": dict(websocket.headers),
                "args": dict(websocket.query_params),
                "path": websocket.url.path,
                "remote": websocket.client.host if websocket.client else "",
                "origin": websocket.headers.get("origin", ""),
            }

            # Create janus queue for outbound messages (main loop context)
            outbound_queue: janus.Queue[str] = janus.Queue()
            # Track pending get_props requests with standard queue.Queue for responses
            pending_get_props: Dict[str, queue.Queue] = {}
            # Shutdown event to signal connection closure to worker threads
            shutdown_event = threading.Event()
            # Get thread pool executor
            executor = self.get_callback_executor()
            # Track pending callback futures
            pending_callbacks: Dict[str, concurrent.futures.Future] = {}

            # Start sender task to drain outbound queue (sends pre-serialized text)
            # pylint: disable=protected-access
            batch_delay = getattr(dash_app, "_websocket_batch_delay", 0.005)
            sender_task = asyncio.create_task(
                run_ws_sender(websocket.send_text, outbound_queue, batch_delay)
            )

            try:
                while True:
                    message = await websocket.receive_json()

                    # Call websocket_message hooks
                    rejection = await self._run_ws_hooks(
                        dash_app._hooks.get_hooks("websocket_message"),
                        websocket,
                        message,
                        default_reason="Message rejected",
                    )
                    if rejection:
                        await websocket.close(code=rejection[0], reason=rejection[1])
                        return

                    msg_type = message.get("type")

                    if msg_type == "callback_request":
                        request_id = message.get("requestId")
                        renderer_id = message.get("rendererId", "")
                        payload = message.get("payload", {})

                        # Validate that the callback is allowed to use WebSocket transport
                        # pylint: disable=protected-access
                        _validate.validate_websocket_callback_request(
                            payload.get("output"),
                            dash_app.callback_map,
                            dash_app._websocket_callbacks,
                        )

                        # Create WebSocket callback instance
                        ws_cb = DashWebsocketCallback(
                            pending_get_props,
                            renderer_id,
                            outbound_queue,
                            shutdown_event,
                        )

                        # Submit callback to executor
                        future = run_callback_in_executor(
                            executor,
                            dash_app,
                            payload,
                            ws_cb,
                            FastAPIResponseAdapter(),
                            request_context,
                        )

                        # Set up done callback to send response
                        future.add_done_callback(
                            make_callback_done_handler(
                                outbound_queue,
                                pending_callbacks,
                                request_id,
                                renderer_id,
                                shutdown_event,
                            )
                        )
                        pending_callbacks[request_id] = future

                    elif msg_type == "get_props_response":
                        # Put response in waiting queue (non-blocking)
                        request_id = message.get("requestId")
                        response_queue = pending_get_props.get(request_id)
                        if response_queue is not None:
                            response_queue.put_nowait(message.get("payload"))

                    elif msg_type == "heartbeat":
                        outbound_queue.sync_q.put_nowait('{"type": "heartbeat_ack"}')

            except WebSocketDisconnect:
                pass  # Clean disconnect
            finally:
                # Signal shutdown to worker threads
                shutdown_event.set()
                # Unblock any threads waiting on get_prop responses
                for response_queue in pending_get_props.values():
                    response_queue.put_nowait(DISCONNECTED)
                # Signal sender to shutdown and cancel it
                outbound_queue.sync_q.put_nowait(SHUTDOWN_SIGNAL)
                sender_task.cancel()
                try:
                    await sender_task
                except asyncio.CancelledError:
                    pass
                # Close the janus queue
                outbound_queue.close()
                await outbound_queue.wait_closed()
                # Cancel any pending futures
                for f in pending_callbacks.values():
                    f.cancel()

        self.server.add_api_websocket_route(ws_path, websocket_handler)


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

    async def _get_json(self, request: Request = None):
        req = self._request
        if not hasattr(req.state, "json_body"):
            req.state.json_body = await request.json()
        return req.state.json_body

    def get_json(self):
        if not hasattr(self, "_request") or self._request is None:
            self._request = get_current_request()
        return self._request.state.json_body
