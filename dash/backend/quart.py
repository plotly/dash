import inspect
import pkgutil
import mimetypes
import sys
import time
from contextvars import copy_context
import traceback
import re

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
        self.error_handling_mode = "prune"
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

    def register_prune_error_handler(self, app, secret, prune_errors):
        if prune_errors:
            self.error_handling_mode = "prune"
        else:
            self.error_handling_mode = "raise"

        @app.errorhandler(Exception)
        async def _wrap_errors(error):
            tb = self._get_traceback(secret, error)
            return Response(tb, status=500, content_type="text/html")

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

    def run(self, _dash_app, app, host, port, debug, **kwargs):
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
