from __future__ import print_function

import sys
import os
import uuid
import shlex
import threading
import subprocess
import logging

import runpy
import six
import flask
import requests

from dash.testing.errors import (
    NoAppFoundError,
    TestingTimeoutError,
    ServerCloseError,
)
import dash.testing.wait as wait


logger = logging.getLogger(__name__)


def import_app(app_file, application_name="app"):
    """
    Import a dash application from a module.
    The import path is in dot notation to the module.
    The variable named app will be returned.

    :Example:

        >>> app = import_app('my_app.app')

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
        raise NoAppFoundError(
            "No dash `app` instance was found in {}".format(app_file)
        )
    return app


class BaseDashRunner(object):
    """Base context manager class for running applications."""

    def __init__(self, keep_open, stop_timeout):
        self.port = 8050
        self.started = None
        self.keep_open = keep_open
        self.stop_timeout = stop_timeout

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
                    "Cannot stop server within {}s timeout".format(
                        self.stop_timeout
                    )
                )

    @property
    def url(self):
        """the default server url"""
        return "http://localhost:{}".format(self.port)

    @property
    def is_windows(self):
        return sys.platform == "win32"


class ThreadedRunner(BaseDashRunner):
    """Runs a dash application in a thread

    this is the default flavor to use in dash integration tests
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
        """Start the app server in threading flavor"""
        app.server.add_url_rule(
            self.stop_route, self.stop_route, self._stop_server
        )

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
    """Runs a dash application in a waitress-serve subprocess

    this flavor is closer to production environment but slower
    """

    def __init__(self, keep_open=False, stop_timeout=3):
        super(ProcessRunner, self).__init__(
            keep_open=keep_open, stop_timeout=stop_timeout
        )
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app_module, application_name="app", port=8050):
        """Start the server with waitress-serve in process flavor """
        entrypoint = "{}:{}.server".format(app_module, application_name)
        self.port = port

        args = shlex.split(
            "waitress-serve --listen=0.0.0.0:{} {}".format(port, entrypoint),
            posix=not self.is_windows,
        )
        logger.debug("start dash process with %s", args)

        try:
            self.proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # wait until server is able to answer http request
            wait.until(lambda: self.accessible(self.url), timeout=3)

        except (OSError, ValueError):
            logger.exception("process server has encountered an error")
            self.started = False
            return

        self.started = True

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
                if six.PY3:
                    # pylint:disable=no-member
                    _except = subprocess.TimeoutExpired
                    # pylint: disable=unexpected-keyword-arg
                    self.proc.communicate(timeout=self.stop_timeout)
                else:
                    _except = OSError
                    self.proc.communicate()
            except _except:
                logger.exception(
                    "subprocess terminate not success, trying to kill "
                    "the subprocess in a safe manner"
                )
                self.proc.kill()
                self.proc.communicate()


class RRunner(ProcessRunner):
    def __init__(self, keep_open=False, stop_timeout=3):
        super(RRunner, self).__init__(
            keep_open=keep_open, stop_timeout=stop_timeout
        )
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app):
        """Start the server with waitress-serve in process flavor """

        # app is a R string chunk
        if not (os.path.isfile(app) and os.path.exists(app)):
            path = (
                "/tmp/app_{}.R".format(uuid.uuid4().hex)
                if not self.is_windows
                else os.path.join(
                    (os.getenv("TEMP"), "app_{}.R".format(uuid.uuid4().hex))
                )
            )
            logger.info("RRuner start => app is R code chunk")
            logger.info("make a temporay R file for execution=> %s", path)
            logger.debug("the content of dashR app")
            logger.debug("%s", app)

            with open(path, "w") as fp:
                fp.write(app)

            app = path

        logger.info("Run dashR app with Rscript => %s", app)
        args = shlex.split(
            "Rscript {}".format(os.path.realpath(app)),
            posix=not self.is_windows,
        )
        logger.debug("start dash process with %s", args)

        try:
            self.proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            # wait until server is able to answer http request
            wait.until(lambda: self.accessible(self.url), timeout=2)

        except (OSError, ValueError):
            logger.exception("process server has encountered an error")
            self.started = False
            return

        self.started = True
