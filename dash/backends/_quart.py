from __future__ import annotations
from contextvars import copy_context
import typing as _t
import traceback
import mimetypes
import inspect
import pkgutil
import time
import sys
import re

# Attempt top-level Quart imports; allow absence if user not using quart backend
from quart import (
    Quart,
    Response,
    jsonify,
    request,
    Blueprint,
    g,
)

if _t.TYPE_CHECKING:
    from dash import Dash

from dash.exceptions import PreventUpdate, InvalidResourceError
from dash.fingerprint import check_fingerprint
from dash import _validate
from .base_server import BaseDashServer


class QuartDashServer(BaseDashServer):

    def __init__(self, server: Quart) -> None:
        self.server_type = "quart"
        self.server: Quart = server
        self.config = {}
        self.error_handling_mode = "prune"
        super().__init__()

    def __call__(self, *args: Any, **kwargs: Any):  # type: ignore[name-defined]
        return self.server(*args, **kwargs)

    @staticmethod
    def create_app(name: str = "__main__", config: _t.Optional[_t.Dict[str, _t.Any]] = None):
        if Quart is None:
            raise RuntimeError(
                "Quart is not installed. Install with 'pip install quart' to use the quart backend."
            )
        app = Quart(name)  # type: ignore
        if config:
            for key, value in config.items():
                app.config[key] = value
        return app

    def register_assets_blueprint(
        self, blueprint_name: str, assets_url_path: str, assets_folder: str  # type: ignore[name-defined]
    ):

        bp = Blueprint(
            blueprint_name,
            __name__,
            static_folder=assets_folder,
            static_url_path=assets_url_path,
        )
        self.server.register_blueprint(bp)

    def _get_traceback(self, _secret, error: Exception):
        tb = error.__traceback__
        errors = traceback.format_exception(type(error), error, tb)
        pass_errs = []
        callback_handled = False
        for err in errors:
            if self.error_handling_mode == "prune":
                if not callback_handled:
                    if "callback invoked" in str(err) and "_callback.py" in str(err):
                        callback_handled = True
                    continue
            pass_errs.append(err)
        formatted_tb = "".join(pass_errs)
        error_type = type(error).__name__
        error_msg = str(error)

        # Parse traceback lines to group by file
        file_cards = []
        pattern = re.compile(r'  File "(.+)", line (\d+), in (\w+)')
        lines = formatted_tb.split("\n")
        current_file = None
        card_lines = []

        for line in lines[:-1]:  # Skip the last line (error message)
            match = pattern.match(line)
            if match:
                if current_file and card_lines:
                    file_cards.append((current_file, card_lines))
                current_file = (
                    f"{match.group(1)} (line {match.group(2)}, in {match.group(3)})"
                )
                card_lines = [line]
            elif current_file:
                card_lines.append(line)
        if current_file and card_lines:
            file_cards.append((current_file, card_lines))

        cards_html = ""
        for filename, card in file_cards:
            cards_html += (
                f"""
            <div class="error-card">
                <div class="error-card-header">{filename}</div>
                <pre class="error-card-traceback">"""
                + "\n".join(card)
                + """</pre>
            </div>
            """
            )

        html = f"""
        <!doctype html>
        <html lang="en">
          <head>
            <title>{error_type}: {error_msg} // Quart Debugger</title>
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

    def register_prune_error_handler(self, secret, prune_errors):
        if prune_errors:
            self.error_handling_mode = "prune"
        else:
            self.error_handling_mode = "raise"

        @self.server.errorhandler(Exception)
        async def _wrap_errors(error):
            tb = self._get_traceback(secret, error)
            return Response(tb, status=500, content_type="text/html")

    def register_timing_hooks(self, _first_run: bool):  # type: ignore[name-defined] parity with Flask factory
        @self.server.before_request
        async def _before_request():  # pragma: no cover - timing infra
            if g is not None:
                g.timing_information = {  # type: ignore[attr-defined]
                    "__dash_server": {"dur": time.time(), "desc": None}
                }

        @self.server.after_request
        async def _after_request(response):  # pragma: no cover - timing infra
            timing_information = (
                getattr(g, "timing_information", None) if g is not None else None
            )
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

    def register_error_handlers(self):  # type: ignore[name-defined]
        @self.server.errorhandler(PreventUpdate)
        async def _prevent_update(_):
            return "", 204

        @self.server.errorhandler(InvalidResourceError)
        async def _invalid_resource(err):
            return err.args[0], 404

    def _html_response_wrapper(self, view_func: _t.Callable[..., _t.Any] | str):

        async def wrapped(*_args, **_kwargs):
            html_val = view_func() if callable(view_func) else view_func
            if inspect.iscoroutine(html_val):  # handle async function returning html
                html_val = await html_val
            html = str(html_val)
            return Response(html, content_type="text/html")

        return wrapped

    def add_url_rule(
        self,
        rule: str,
        view_func: _t.Callable[..., _t.Any],
        endpoint: str | None = None,
        methods: list[str] | None = None,
    ):
        self.server.add_url_rule(
            rule, view_func=view_func, endpoint=endpoint, methods=methods or ["GET"]
        )

    def setup_index(self, dash_app: Dash):  # type: ignore[name-defined]

        async def index(*args, **kwargs):
            return Response(dash_app.index(*args, **kwargs), content_type="text/html")  # type: ignore[arg-type]

        # pylint: disable=protected-access
        dash_app._add_url("", index, methods=["GET"])

    def setup_catchall(self, dash_app: Dash):

        async def catchall(
            path: str, *args, **kwargs
        ):  # noqa: ARG001 - path is unused but kept for route signature, pylint: disable=unused-argument
            return Response(dash_app.index(*args, **kwargs), content_type="text/html")  # type: ignore[arg-type]

        # pylint: disable=protected-access
        dash_app._add_url("<path:path>", catchall, methods=["GET"])

    def before_request(self, func: _t.Callable[[], _t.Any]):
        self.server.before_request(func)

    def after_request(self, func: _t.Callable[[], _t.Any]):
        @self.server.after_request
        async def _after(response):
            if func is not None:
                result = func()
                if inspect.iscoroutine(result):  # Allow async hooks
                    await result
            return response

    def run(self, dash_app: Dash, host: str, port: int, debug: bool, **kwargs: _t.Any):
        self.config = {"debug": debug, **kwargs} if debug else kwargs
        self.server.run(host=host, port=port, debug=debug, **kwargs)

    def make_response(
        self,
        data: str | bytes | bytearray,
        mimetype: str | None = None,
        content_type: str | None = None,
    ):
        if Response is None:
            raise RuntimeError("Quart not installed; cannot generate Response")
        return Response(data, mimetype=mimetype, content_type=content_type)

    def jsonify(self, obj):
        return jsonify(obj)

    def serve_component_suites(
        self, dash_app: Dash, package_name: str, fingerprinted_path: str
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

        if Response is None:
            raise RuntimeError("Quart not installed; cannot generate Response")
        return Response(data, content_type=mimetype, headers=headers)

    def setup_component_suites(self, dash_app: Dash):
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
    def dispatch(self, dash_app: Dash):  # type: ignore[name-defined] Quart always async

        async def _dispatch():
            adapter = QuartRequestAdapter()
            body = await adapter.get_json()
            # pylint: disable=protected-access
            g = dash_app._initialize_context(body)
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
            return Response(response_data, content_type="application/json")  # type: ignore[arg-type]

        return _dispatch

    def register_callback_api_routes(self, callback_api_paths: _t.Dict[str, _t.Callable[..., _t.Any]]):
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
                        if request is None:
                            raise RuntimeError(
                                "Quart not installed; request unavailable"
                            )
                        data = await request.get_json()
                        result = await handler(**data) if data else await handler()
                        return jsonify(result)  # type: ignore[arg-type]

                    return async_view_func

                async def sync_view_func(*args, **kwargs):
                    if request is None:
                        raise RuntimeError("Quart not installed; request unavailable")
                    data = await request.get_json()
                    result = handler(**data) if data else handler()
                    return jsonify(result)  # type: ignore[arg-type]

                return sync_view_func

            view_func = _make_view_func(handler)
            self.server.add_url_rule(
                route, endpoint=endpoint, view_func=view_func, methods=methods
            )

    def _serve_default_favicon(self):
        if Response is None:
            raise RuntimeError("Quart not installed; cannot generate Response")
        return Response(
            pkgutil.get_data("dash", "favicon.ico"), content_type="image/x-icon"
        )


class QuartRequestAdapter:
    def __init__(self) -> None:
        self._request = request  # type: ignore[assignment]
        if self._request is None:
            raise RuntimeError("Quart not installed; cannot access request context")

    @property
    def request(self) -> _t.Any:
        return self._request

    @property
    def root(self):
        return self.request.root_url

    @property
    def args(self):
        return self.request.args

    @property
    def is_json(self):
        return self.request.is_json

    @property
    def cookies(self):
        return self.request.cookies

    @property
    def headers(self):
        return self.request.headers

    @property
    def full_path(self):
        return self.request.full_path

    @property
    def url(self):
        return str(self.request.url)

    @property
    def remote_addr(self):
        return self.request.remote_addr

    @property
    def origin(self):
        return self.request.headers.get("origin")

    @property
    def path(self):
        return self.request.path

    async def get_json(self):
        return await self.request.get_json()
