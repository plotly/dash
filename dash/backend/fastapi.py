import sys
import mimetypes
import hashlib
import inspect
import pkgutil
from contextvars import copy_context
import importlib.util
import time
import traceback

try:
    import uvicorn
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import JSONResponse, PlainTextResponse
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import Response as StarletteResponse
    from starlette.datastructures import MutableHeaders
    from pydantic import create_model
    from typing import Any, Optional
except ImportError:
    uvicorn = None
    FastAPI = None
    Request = None
    Response = None
    JSONResponse = None
    PlainTextResponse = None
    StaticFiles = None
    StarletteResponse = None
    MutableHeaders = None
    create_model = None
    Any = None
    Optional = None

from dash.fingerprint import check_fingerprint
from dash import _validate
from dash.exceptions import PreventUpdate, InvalidResourceError, InvalidCallbackReturnValue, BackgroundCallbackError
from dash.backend import set_request_adapter
from .base_server import BaseDashServer

import json
import os

CONFIG_PATH = "dash_config.json"

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

class FastAPIDashServer(BaseDashServer):
    def __init__(self):
        self.error_handling_mode = "prune"
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
        self.error_handling_mode = "prune"
        # FastAPI uses exception handlers, but we will handle errors in middleware
        pass

    def _get_traceback(self, secret, error: Exception):
        tb = error.__traceback__
        errors = traceback.format_exception(type(error), error, tb)
        pass_errs = []
        callback_handled = False
        for err in errors:
            if self.error_handling_mode == "prune":
                if not callback_handled:
                    if 'callback invoked' in str(err) and '_callback.py' in str(err):
                        callback_handled = True
                    continue
            pass_errs.append(err)
        formatted_tb = "".join(pass_errs)
        error_type = type(error).__name__
        error_msg = str(error)

        # Parse traceback lines to group by file
        import re
        file_cards = []
        pattern = re.compile(r'  File "(.+)", line (\d+), in (\w+)')
        lines = formatted_tb.split('\n')
        current_file = None
        card_lines = []

        for i, line in enumerate(lines[:-1]):  # Skip the last line (error message)
            match = pattern.match(line)
            if match:
                if current_file and card_lines:
                    file_cards.append((current_file, card_lines))
                current_file = f'{match.group(1)} (line {match.group(2)}, in {match.group(3)})'
                card_lines = [line]
            elif current_file:
                card_lines.append(line)
        if current_file and card_lines:
            file_cards.append((current_file, card_lines))

        cards_html = ""
        for filename, card in file_cards:
            cards_html += f"""
            <div class="error-card">
                <div class="error-card-header">{filename}</div>
                <pre class="error-card-traceback">"""+ '\n'.join(card) + """</pre>
            </div>
            """

        html = f"""
        <!doctype html>
        <html lang="en">
          <head>
            <title>{error_type}: {error_msg} // FastAPI Debugger</title>
            <style>
              body {{ font-family: monospace; background: #fff; color: #333; }}
              .debugger {{ margin: 2em; max-width: 700px; }}
              .error-card {{
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-bottom: 1em;
                padding: 1em;
                background: #f9f9f9;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
                overflow: auto;
              }}
              .error-card-header {{
                font-weight: bold;
                margin-bottom: 0.5em;
                color: #0074d9;
              }}
              .error-card-traceback {{
                max-height: 150px;
                overflow: auto;
                margin: 0;
                white-space: pre-wrap;
              }}
              .plain textarea {{ width: 100%; height: 10em; resize: vertical; overflow: auto; }}
              h1 {{ color: #c00; }}
            </style>
          </head>
          <body style="padding-bottom:10px">
            <div class="debugger">
              <h1>{error_type}</h1>
              <div class="detail">
                <p class="errormsg">{error_type}: {error_msg}</p>
              </div>
              <h2 class="traceback">Traceback <em>(most recent call last)</em></h2>
              {cards_html}
              <blockquote>{error_type}: {error_msg}</blockquote>
              <div class="plain">
                <p>This is the Copy/Paste friendly version of the traceback.</p>
                <textarea readonly>{formatted_tb}</textarea>
              </div>
              <div class="explanation">
                The debugger caught an exception in your ASGI application. You can now
                look at the traceback which led to the error.
              </div>
              <div class="footer">
                Brought to you by <strong class="arthur">DON'T PANIC</strong>, your
                friendly FastAPI powered traceback interpreter.
              </div>
            </div>
          </body>
        </html>
        """
        return html

    def register_prune_error_handler(self, _app, _secret, prune_errors):
        if prune_errors:
            self.error_handling_mode = "prune"
        else:
            self.error_handling_mode = "raise"


    def _html_response_wrapper(self, view_func):
        async def wrapped(*_args, **_kwargs):
            # If view_func is a function, call it; if it's a string, use it directly
            html = view_func() if callable(view_func) else view_func
            return Response(content=html, media_type="text/html")

        return wrapped

    def setup_index(self, dash_app):
        async def index(request: Request):
            adapter = FastAPIRequestAdapter()
            set_request_adapter(adapter)
            adapter.set_request(request)
            return Response(content=dash_app.index(), media_type="text/html")

        # pylint: disable=protected-access
        dash_app._add_url("", index, methods=["GET"])

    def setup_catchall(self, dash_app):
        @dash_app.server.on_event("startup")
        def _setup_catchall():
            config = load_config()
            dash_app.enable_dev_tools(
                **config, first_run=False
            )

            async def catchall(request: Request):
                adapter = FastAPIRequestAdapter()
                set_request_adapter(adapter)
                adapter.set_request(request)
                return Response(content=dash_app.index(), media_type="text/html")

            # pylint: disable=protected-access
            dash_app._add_url("{path:path}", catchall, methods=["GET"])

    def add_url_rule(
        self, app, rule, view_func, endpoint=None, methods=None, include_in_schema=False
    ):
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
            include_in_schema=include_in_schema,
        )

    def before_request(self, app, func):
        # FastAPI does not have before_request, but we can use middleware
        app.middleware("http")(self._make_before_middleware(func))

    def after_request(self, app, func):
        # FastAPI does not have after_request, but we can use middleware
        app.middleware("http")(self._make_after_middleware(func))

    def run(self, dash_app, app, host, port, debug, **kwargs):
        frame = inspect.stack()[2]
        config = dict({"debug": debug} if debug else {}, **{
            f'dev_tools_{k}': v for k, v in dash_app._dev_tools.items()})
        save_config(config)
        if debug:
            if kwargs.get('reload') is None:
                kwargs['reload'] = True
        if kwargs.get('reload'):
            # Dynamically determine the module name from the file path
            file_path = frame.filename
            module_name = importlib.util.spec_from_file_location("app", file_path).name
            uvicorn.run(
                f"{module_name}:app.server",
                host=host,
                port=port,
                **kwargs,
            )
        else:
            uvicorn.run(app, host=host, port=port, **kwargs)

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
            try:
                response = await call_next(request)
                return response
            except PreventUpdate:
                # No content, nothing to update
                return Response(status_code=204)
            except Exception as e:
                if self.error_handling_mode in ["raise", "prune"]:
                    # Prune the traceback to remove internal Dash calls
                    tb = self._get_traceback(None, e)
                    return Response(content=tb, media_type='text/html', status_code=500)
                return JSONResponse(
                    status_code=500,
                    content={"error": "InternalServerError", "message": str(e.args[0])},
                )

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

    def setup_component_suites(self, dash_app):
        async def serve(request: Request, package_name: str, fingerprinted_path: str):
            return self.serve_component_suites(
                dash_app, package_name, fingerprinted_path, request
            )

        # pylint: disable=protected-access
        dash_app._add_url(
            "_dash-component-suites/{package_name}/{fingerprinted_path:path}",
            serve,
        )

    # pylint: disable=unused-argument
    def dispatch(self, app, dash_app, use_async=False):
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

    def register_callback_api_routes(self, app, callback_api_paths):
        """
        Register callback API endpoints on the FastAPI app.
        Each key in callback_api_paths is a route, each value is a handler (sync or async).
        Dynamically creates a Pydantic model for the handler's parameters and uses it as the body parameter.
        """
        for path, handler in callback_api_paths.items():
            endpoint = f"dash_callback_api_{path}"
            route = path if path.startswith("/") else f"/{path}"
            methods = ["POST"]
            sig = inspect.signature(handler)
            param_names = list(sig.parameters.keys())
            fields = {name: (Optional[Any], None) for name in param_names}
            Model = create_model(
                f"Payload_{endpoint}", **fields
            )  # pylint: disable=cell-var-from-loop

            # pylint: disable=cell-var-from-loop
            async def view_func(request: Request, body: Model):
                kwargs = body.dict(exclude_unset=True)
                if inspect.iscoroutinefunction(handler):
                    result = await handler(**kwargs)
                else:
                    result = handler(**kwargs)
                return JSONResponse(content=result)

            app.add_api_route(
                route,
                view_func,
                methods=methods,
                name=endpoint,
                include_in_schema=True,
            )


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
