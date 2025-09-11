from contextvars import copy_context
import asyncio
import pkgutil
import sys
import mimetypes
import time
import flask
from dash.fingerprint import check_fingerprint
from dash import _validate
from dash.exceptions import PreventUpdate, InvalidResourceError
from dash.server_factories import set_request_adapter
from .base_factory import BaseServerFactory


class FlaskServerFactory(BaseServerFactory):
    def __call__(self, server, *args, **kwargs):
        # Always WSGI
        return server(*args, **kwargs)

    def create_app(self, name="__main__", config=None):
        app = flask.Flask(name)
        if config:
            app.config.update(config)
        return app

    def register_assets_blueprint(
        self, app, blueprint_name, assets_url_path, assets_folder
    ):
        bp = flask.Blueprint(
            blueprint_name,
            __name__,
            static_folder=assets_folder,
            static_url_path=assets_url_path,
        )
        app.register_blueprint(bp)

    def register_error_handlers(self, app):
        @app.errorhandler(PreventUpdate)
        def _handle_error(_):
            return "", 204

        @app.errorhandler(InvalidResourceError)
        def _invalid_resources_handler(err):
            return err.args[0], 404

    def register_prune_error_handler(self, app, secret, get_traceback_func):
        @app.errorhandler(Exception)
        def _wrap_errors(error):
            tb = get_traceback_func(secret, error)
            return tb, 500

    def add_url_rule(self, app, rule, view_func, endpoint=None, methods=None):
        app.add_url_rule(
            rule, view_func=view_func, endpoint=endpoint, methods=methods or ["GET"]
        )

    def before_request(self, app, func):
        app.before_request(func)

    def after_request(self, app, func):
        app.after_request(func)

    def run(self, app, host, port, debug, **kwargs):
        app.run(host=host, port=port, debug=debug, **kwargs)

    def make_response(self, data, mimetype=None, content_type=None):
        return flask.Response(data, mimetype=mimetype, content_type=content_type)

    def jsonify(self, obj):
        return flask.jsonify(obj)

    def get_request_adapter(self):
        return FlaskRequestAdapter

    def setup_catchall(self, app, dash_app):
        def catchall(_path, *args, **kwargs):
            adapter = FlaskRequestAdapter()
            set_request_adapter(adapter)
            return dash_app.render_index(*args, **kwargs)

        self.add_url_rule(
            app, "/<path:path>", catchall, endpoint="catchall", methods=["GET"]
        )

    def setup_index(self, app, dash_app):
        def index(*args, **kwargs):
            adapter = FlaskRequestAdapter()
            set_request_adapter(adapter)
            return dash_app.render_index(*args, **kwargs)

        self.add_url_rule(app, "/", index, endpoint="/", methods=["GET"])

    def serve_component_suites(self, dash_app, package_name, fingerprinted_path):
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
        response = flask.Response(data, mimetype=mimetype)
        if has_fingerprint:
            response.cache_control.max_age = 31536000  # 1 year
        else:
            response.add_etag()
            tag = response.get_etag()[0]
            request_etag = flask.request.headers.get("If-None-Match")
            if f'"{tag}"' == request_etag:
                response = flask.Response(None, status=304)
        return response

    def setup_component_suites(self, app, dash_app):
        def serve(package_name, fingerprinted_path):
            return self.serve_component_suites(
                dash_app, package_name, fingerprinted_path
            )

        self.add_url_rule(
            app,
            "/_dash-component-suites/<string:package_name>/<path:fingerprinted_path>",
            serve,
        )

    def dispatch(
        self, app, dash_app, use_async=False
    ):  # pylint: disable=unused-argument
        def _dispatch():
            adapter = FlaskRequestAdapter()
            set_request_adapter(adapter)
            body = flask.request.get_json()
            # pylint: disable=protected-access
            g = dash_app._initialize_context(body, adapter)
            func = dash_app._prepare_callback(g, body)
            args = dash_app._inputs_to_vals(g.inputs_list + g.states_list)
            ctx = copy_context()
            partial_func = dash_app._execute_callback(func, args, g.outputs_list, g)
            response_data = ctx.run(partial_func)
            if asyncio.iscoroutine(response_data):
                raise Exception(
                    "You are trying to use a coroutine without dash[async]. "
                    "Please install the dependencies via `pip install dash[async]` and ensure "
                    "that `use_async=False` is not being passed to the app."
                )
            g.dash_response.set_data(response_data)
            return g.dash_response

        async def _dispatch_async():
            adapter = FlaskRequestAdapter()
            set_request_adapter(adapter)
            body = flask.request.get_json()
            # pylint: disable=protected-access
            g = dash_app._initialize_context(body, adapter)
            func = dash_app._prepare_callback(g, body)
            args = dash_app._inputs_to_vals(g.inputs_list + g.states_list)
            ctx = copy_context()
            partial_func = dash_app._execute_callback(func, args, g.outputs_list, g)
            response_data = ctx.run(partial_func)
            if asyncio.iscoroutine(response_data):
                response_data = await response_data
            g.dash_response.set_data(response_data)
            return g.dash_response

        if use_async:
            return _dispatch_async
        return _dispatch

    def _serve_default_favicon(self):

        return flask.Response(
            pkgutil.get_data("dash", "favicon.ico"), content_type="image/x-icon"
        )

    def register_timing_hooks(self, app, _first_run):
        def _before_request():
            flask.g.timing_information = {
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
                    value += f';desc="{info["desc"]}"'
                if info.get("dur") is not None:
                    value += f";dur={info['dur']}"
                response.headers.add("Server-Timing", value)
            return response

        self.before_request(app, _before_request)
        self.after_request(app, _after_request)


class FlaskRequestAdapter:
    @staticmethod
    def get_args():
        return flask.request.args

    @staticmethod
    def get_json():
        return flask.request.get_json()

    @staticmethod
    def is_json():
        return flask.request.is_json

    @staticmethod
    def get_cookies():
        return flask.request.cookies

    @staticmethod
    def get_headers():
        return flask.request.headers

    @staticmethod
    def get_full_path():
        return flask.request.full_path

    @staticmethod
    def get_remote_addr():
        return flask.request.remote_addr

    @staticmethod
    def get_origin():
        return getattr(flask.request, "origin", None)

    @staticmethod
    def get_path():
        return flask.request.path
