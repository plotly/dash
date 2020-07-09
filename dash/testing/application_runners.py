from __future__ import print_function

import sys
import os
import uuid
import shlex
import threading
import shutil
import subprocess
import logging
import inspect

import runpy
import future.utils as utils
import flask
import requests

from dash.testing.errors import NoAppFoundError, TestingTimeoutError, ServerCloseError
import dash.testing.wait as wait


logger = logging.getLogger(__name__)


def import_app(app_file, application_name="app"):
    """Import a dash application from a module. The import path is in dot
    notation to the module. The variable named app will be returned.

    :Example:

        >>> app = import_app("my_app.app")

    Will import the application in module `app` of the package `my_app`.

    :param app_file: Path to the app (dot-separated).
    :type app_file: str
    :param application_name: The name of the dash application instance.
    :raise: dash_tests.errors.NoAppFoundError
    :return: App from module.
    :rtype: dash.Dash
    """
    try:
        app_module = runpy.run_module(app_file)
        app = app_module[application_name]
    except KeyError:
        logger.exception("the app name cannot be found")
        raise NoAppFoundError("No dash `app` instance was found in {}".format(app_file))
    return app


class BaseDashRunner(object):
    """Base context manager class for running applications."""

    def __init__(self, keep_open, stop_timeout):
        self.port = 8050
        self.started = None
        self.keep_open = keep_open
        self.stop_timeout = stop_timeout
        self._tmp_app_path = None

    def start(self, *args, **kwargs):
        raise NotImplementedError  # pragma: no cover

    def stop(self):
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def accessible(url):
        try:
            requests.get(url)
        except requests.exceptions.RequestException:
            return False
        return True

    def __call__(self, *args, **kwargs):
        return self.start(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if self.started and not self.keep_open:
            try:
                logger.info("killing the app runner")
                self.stop()
            except TestingTimeoutError:
                raise ServerCloseError(
                    "Cannot stop server within {}s timeout".format(self.stop_timeout)
                )
        logger.info("__exit__ complete")

    @property
    def url(self):
        """The default server url."""
        return "http://localhost:{}".format(self.port)

    @property
    def is_windows(self):
        return sys.platform == "win32"

    @property
    def tmp_app_path(self):
        return self._tmp_app_path


class ThreadedRunner(BaseDashRunner):
    """Runs a dash application in a thread.

    This is the default flavor to use in dash integration tests.
    """

    def __init__(self, keep_open=False, stop_timeout=3):
        super(ThreadedRunner, self).__init__(
            keep_open=keep_open, stop_timeout=stop_timeout
        )
        self.stop_route = "/_stop-{}".format(uuid.uuid4().hex)
        self.thread = None

    @staticmethod
    def _stop_server():
        # https://werkzeug.palletsprojects.com/en/0.15.x/serving/#shutting-down-the-server
        stopper = flask.request.environ.get("werkzeug.server.shutdown")
        if stopper is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        stopper()
        return "Flask server is shutting down"

    # pylint: disable=arguments-differ,C0330
    def start(self, app, **kwargs):
        """Start the app server in threading flavor."""
        app.server.add_url_rule(self.stop_route, self.stop_route, self._stop_server)

        def _handle_error():
            self._stop_server()

        app.server.errorhandler(500)(_handle_error)

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True
            if "port" not in kwargs:
                kwargs["port"] = self.port
            else:
                self.port = kwargs["port"]
            app.run_server(threaded=True, **kwargs)

        self.thread = threading.Thread(target=run)
        self.thread.daemon = True
        try:
            self.thread.start()
        except RuntimeError:  # multiple call on same thread
            logger.exception("threaded server failed to start")
            self.started = False

        self.started = self.thread.is_alive()

        # wait until server is able to answer http request
        wait.until(lambda: self.accessible(self.url), timeout=1)

    def stop(self):
        requests.get("{}{}".format(self.url, self.stop_route))
        wait.until_not(self.thread.is_alive, self.stop_timeout)


class ProcessRunner(BaseDashRunner):
    """Runs a dash application in a waitress-serve subprocess.

    This flavor is closer to production environment but slower.
    """

    def __init__(self, keep_open=False, stop_timeout=3):
        super(ProcessRunner, self).__init__(
            keep_open=keep_open, stop_timeout=stop_timeout
        )
        self.proc = None

    # pylint: disable=arguments-differ
    def start(
        self,
        app_module=None,
        application_name="app",
        raw_command=None,
        port=8050,
        start_timeout=3,
    ):
        """Start the server with waitress-serve in process flavor."""
        if not (app_module or raw_command):  # need to set a least one
            logging.error(
                "the process runner needs to start with at least one valid command"
            )
            return
        self.port = port
        args = shlex.split(
            raw_command
            if raw_command
            else "waitress-serve --listen=0.0.0.0:{} {}:{}.server".format(
                port, app_module, application_name
            ),
            posix=not self.is_windows,
        )

        logger.debug("start dash process with %s", args)

        try:
            self.proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # wait until server is able to answer http request
            wait.until(lambda: self.accessible(self.url), timeout=start_timeout)

        except (OSError, ValueError):
            logger.exception("process server has encountered an error")
            self.started = False
            self.stop()
            return

        self.started = True

    def stop(self):
        if self.proc:
            try:
                logger.info("proc.terminate with pid %s", self.proc.pid)
                self.proc.terminate()
                if self.tmp_app_path and os.path.exists(self.tmp_app_path):
                    logger.debug("removing temporary app path %s", self.tmp_app_path)
                    shutil.rmtree(self.tmp_app_path)
                if utils.PY3:
                    # pylint:disable=no-member
                    _except = subprocess.TimeoutExpired
                    # pylint: disable=unexpected-keyword-arg
                    self.proc.communicate(timeout=self.stop_timeout)
                else:
                    _except = Exception
                    logger.info("ruthless kill the process to avoid zombie")
                    self.proc.kill()
            except _except:
                logger.exception(
                    "subprocess terminate not success, trying to kill "
                    "the subprocess in a safe manner"
                )
                self.proc.kill()
                self.proc.communicate()
        logger.info("process stop completes!")


class RRunner(ProcessRunner):
    def __init__(self, keep_open=False, stop_timeout=3):
        super(RRunner, self).__init__(keep_open=keep_open, stop_timeout=stop_timeout)
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app, start_timeout=2, cwd=None):
        """Start the server with subprocess and Rscript."""

        if os.path.isfile(app) and os.path.exists(app):
            # app is already a file in a dir - use that as cwd
            if not cwd:
                cwd = os.path.dirname(app)
                logger.info("RRunner inferred cwd from app path: %s", cwd)
        else:
            # app is a string chunk, we make a temporary folder to store app.R
            # and its relevant assets
            self._tmp_app_path = os.path.join(
                "/tmp" if not self.is_windows else os.getenv("TEMP"), uuid.uuid4().hex
            )
            try:
                os.mkdir(self.tmp_app_path)
            except OSError:
                logger.exception("cannot make temporary folder %s", self.tmp_app_path)
            path = os.path.join(self.tmp_app_path, "app.R")

            logger.info("RRunner start => app is R code chunk")
            logger.info("make a temporary R file for execution => %s", path)
            logger.debug("content of the dashR app")
            logger.debug("%s", app)

            with open(path, "w") as fp:
                fp.write(app)

            app = path

            # try to find the path to the calling script to use as cwd
            if not cwd:
                for entry in inspect.stack():
                    if "/dash/testing/" not in entry[1].replace("\\", "/"):
                        cwd = os.path.dirname(os.path.realpath(entry[1]))
                        logger.warning("get cwd from inspect => %s", cwd)
                        break
            if cwd:
                logger.info("RRunner inferred cwd from the Python call stack: %s", cwd)

                # try copying all valid sub folders (i.e. assets) in cwd to tmp
                # note that the R assets folder name can be any valid folder name
                assets = [
                    os.path.join(cwd, _)
                    for _ in os.listdir(cwd)
                    if not _.startswith("__") and os.path.isdir(os.path.join(cwd, _))
                ]

                for asset in assets:
                    target = os.path.join(self.tmp_app_path, os.path.basename(asset))
                    if os.path.exists(target):
                        logger.debug("delete existing target %s", target)
                        shutil.rmtree(target)
                    logger.debug("copying %s => %s", asset, self.tmp_app_path)
                    shutil.copytree(asset, target)
                    logger.debug("copied with %s", os.listdir(target))

            else:
                logger.warning(
                    "RRunner found no cwd in the Python call stack. "
                    "You may wish to specify an explicit working directory "
                    "using something like: "
                    "dashr.run_server(app, cwd=os.path.dirname(__file__))"
                )

        logger.info("Run dashR app with Rscript => %s", app)

        args = shlex.split(
            "Rscript -e 'source(\"{}\")'".format(os.path.realpath(app)),
            posix=not self.is_windows,
        )
        logger.debug("start dash process with %s", args)

        try:
            self.proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.tmp_app_path if self.tmp_app_path else cwd,
            )
            # wait until server is able to answer http request
            wait.until(lambda: self.accessible(self.url), timeout=start_timeout)

        except (OSError, ValueError):
            logger.exception("process server has encountered an error")
            self.started = False
            return

        self.started = True


class JuliaRunner(ProcessRunner):
    def __init__(self, keep_open=False, stop_timeout=3):
        super(JuliaRunner, self).__init__(
            keep_open=keep_open, stop_timeout=stop_timeout
        )
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app, start_timeout=30, cwd=None):
        """Start the server with subprocess and julia."""

        if os.path.isfile(app) and os.path.exists(app):
            # app is already a file in a dir - use that as cwd
            if not cwd:
                cwd = os.path.dirname(app)
                logger.info("JuliaRunner inferred cwd from app path: %s", cwd)
        else:
            # app is a string chunk, we make a temporary folder to store app.jl
            # and its relevant assets
            self._tmp_app_path = os.path.join(
                "/tmp" if not self.is_windows else os.getenv("TEMP"), uuid.uuid4().hex
            )
            try:
                os.mkdir(self.tmp_app_path)
            except OSError:
                logger.exception("cannot make temporary folder %s", self.tmp_app_path)
            path = os.path.join(self.tmp_app_path, "app.jl")

            logger.info("JuliaRunner start => app is Julia code chunk")
            logger.info("make a temporary Julia file for execution => %s", path)
            logger.debug("content of the Dash.jl app")
            logger.debug("%s", app)

            with open(path, "w") as fp:
                fp.write(app)

            app = path

            # try to find the path to the calling script to use as cwd
            if not cwd:
                for entry in inspect.stack():
                    if "/dash/testing/" not in entry[1].replace("\\", "/"):
                        cwd = os.path.dirname(os.path.realpath(entry[1]))
                        logger.warning("get cwd from inspect => %s", cwd)
                        break
            if cwd:
                logger.info(
                    "JuliaRunner inferred cwd from the Python call stack: %s", cwd
                )

                # try copying all valid sub folders (i.e. assets) in cwd to tmp
                # note that the R assets folder name can be any valid folder name
                assets = [
                    os.path.join(cwd, _)
                    for _ in os.listdir(cwd)
                    if not _.startswith("__") and os.path.isdir(os.path.join(cwd, _))
                ]

                for asset in assets:
                    target = os.path.join(self.tmp_app_path, os.path.basename(asset))
                    if os.path.exists(target):
                        logger.debug("delete existing target %s", target)
                        shutil.rmtree(target)
                    logger.debug("copying %s => %s", asset, self.tmp_app_path)
                    shutil.copytree(asset, target)
                    logger.debug("copied with %s", os.listdir(target))

            else:
                logger.warning(
                    "JuliaRunner found no cwd in the Python call stack. "
                    "You may wish to specify an explicit working directory "
                    "using something like: "
                    "dashjl.run_server(app, cwd=os.path.dirname(__file__))"
                )

        logger.info("Run Dash.jl app with julia => %s", app)

        args = shlex.split(
            "julia {}".format(os.path.realpath(app)), posix=not self.is_windows,
        )
        logger.debug("start Dash.jl process with %s", args)

        try:
            self.proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.tmp_app_path if self.tmp_app_path else cwd,
            )
            # wait until server is able to answer http request
            wait.until(lambda: self.accessible(self.url), timeout=start_timeout)

        except (OSError, ValueError):
            logger.exception("process server has encountered an error")
            self.started = False
            return

        self.started = True
