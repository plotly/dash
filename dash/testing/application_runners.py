import sys
import os
import time
import uuid
import shlex
import threading
import shutil
import subprocess
import logging
import inspect
import ctypes

import runpy
import requests
import psutil

# pylint: disable=no-member
import multiprocess

from dash.testing.errors import (
    NoAppFoundError,
    TestingTimeoutError,
    ServerCloseError,
    DashAppLoadingError,
)
from dash.testing import wait

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
    except KeyError as app_name_missing:
        logger.exception("the app name cannot be found")
        raise NoAppFoundError(
            f"No dash `app` instance was found in {app_file}"
        ) from app_name_missing
    return app


class BaseDashRunner:
    """Base context manager class for running applications."""

    _next_port = 58050

    def __init__(self, keep_open, stop_timeout, scheme="http", host="localhost"):
        self.scheme = scheme
        self.host = host
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
            except TestingTimeoutError as cannot_stop_server:
                raise ServerCloseError(
                    f"Cannot stop server within {self.stop_timeout}s timeout"
                ) from cannot_stop_server
        logger.info("__exit__ complete")

    @property
    def url(self):
        """The default server url."""
        return f"{self.scheme}://{self.host}:{self.port}"

    @property
    def is_windows(self):
        return sys.platform == "win32"

    @property
    def tmp_app_path(self):
        return self._tmp_app_path


class KillerThread(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._old_threads = list(threading._active.keys())  # type: ignore[reportAttributeAccessIssue]; pylint: disable=W0212

    def kill(self):
        # Kill all the new threads.
        for thread_id in list(threading._active):  # type: ignore[reportAttributeAccessIssue]; pylint: disable=W0212
            if thread_id in self._old_threads:
                continue

            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(thread_id), ctypes.py_object(SystemExit)
            )
            if res == 0:
                raise ValueError(f"Invalid thread id: {thread_id}")
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id), None
                )
                raise SystemExit("Stopping thread failure")


class ThreadedRunner(BaseDashRunner):
    """Runs a dash application in a thread.

    This is the default flavor to use in dash integration tests.
    """

    def __init__(self, keep_open=False, stop_timeout=3):
        super().__init__(keep_open=keep_open, stop_timeout=stop_timeout)
        self.thread = None

    def running_and_accessible(self, url):
        if self.thread.is_alive():  # type: ignore[reportOptionalMemberAccess]
            return self.accessible(url)
        raise DashAppLoadingError("Thread is not alive.")

    # pylint: disable=arguments-differ
    def start(self, app, start_timeout=3, **kwargs):
        """Start the app server in threading flavor."""

        def run():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True

            options = kwargs.copy()
            options["dev_tools_disable_version_check"] = True

            if "port" not in kwargs:
                options["port"] = self.port = BaseDashRunner._next_port
                BaseDashRunner._next_port += 1
            else:
                self.port = options["port"]

            try:
                app.run(threaded=True, **options)
            except SystemExit:
                logger.info("Server stopped")
            except Exception as error:
                logger.exception(error)
                raise error

        retries = 0

        while not self.started and retries < 3:
            try:
                if self.thread:
                    if self.thread.is_alive():
                        self.stop()
                    else:
                        self.thread.kill()

                self.thread = KillerThread(target=run)
                self.thread.daemon = True
                self.thread.start()
                # wait until server is able to answer http request
                wait.until(
                    lambda: self.running_and_accessible(self.url), timeout=start_timeout
                )
                self.started = self.thread.is_alive()
            except Exception as err:  # pylint: disable=broad-except
                logger.exception(err)
                self.started = False
                retries += 1
                time.sleep(1)

        self.started = self.thread.is_alive()  # type: ignore[reportOptionalMemberAccess]
        if not self.started:
            raise DashAppLoadingError("threaded server failed to start")

    def stop(self):
        self.thread.kill()  # type: ignore[reportOptionalMemberAccess]
        self.thread.join()  # type: ignore[reportOptionalMemberAccess]
        wait.until_not(self.thread.is_alive, self.stop_timeout)  # type: ignore[reportOptionalMemberAccess]
        self.started = False


class MultiProcessRunner(BaseDashRunner):
    def __init__(self, keep_open=False, stop_timeout=3):
        super().__init__(keep_open, stop_timeout)
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app, start_timeout=3, **kwargs):
        self.port = kwargs.get("port", 8050)

        def target():
            app.scripts.config.serve_locally = True
            app.css.config.serve_locally = True

            options = kwargs.copy()

            try:
                app.run(threaded=True, **options)
            except SystemExit:
                logger.info("Server stopped")
                raise
            except Exception as error:
                logger.exception(error)
                raise error

        self.proc = multiprocess.Process(target=target)  # type: ignore[reportAttributeAccessIssue]; pylint: disable=not-callable
        self.proc.start()

        wait.until(lambda: self.accessible(self.url), timeout=start_timeout)
        self.started = True

    def stop(self):
        process = psutil.Process(self.proc.pid)  # type: ignore[reportOptionalMemberAccess]

        for proc in process.children(recursive=True):
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass

        try:
            process.wait(1)
        except (psutil.TimeoutExpired, psutil.NoSuchProcess):
            pass


class ProcessRunner(BaseDashRunner):
    """Runs a dash application in a waitress-serve subprocess.

    This flavor is closer to production environment but slower.
    """

    def __init__(self, keep_open=False, stop_timeout=3):
        super().__init__(keep_open=keep_open, stop_timeout=stop_timeout)
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
            else f"waitress-serve --listen=0.0.0.0:{port} {app_module}:{application_name}.server",
            posix=not self.is_windows,
        )

        logger.debug("start dash process with %s", args)

        try:
            self.proc = subprocess.Popen(  # pylint: disable=consider-using-with
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

                self.proc.communicate(
                    timeout=self.stop_timeout  # pylint: disable=unexpected-keyword-arg
                )
            except subprocess.TimeoutExpired:
                logger.exception(
                    "subprocess terminate not success, trying to kill "
                    "the subprocess in a safe manner"
                )
                self.proc.kill()
                self.proc.communicate()
        logger.info("process stop completes!")


class RRunner(ProcessRunner):
    def __init__(self, keep_open=False, stop_timeout=3):
        super().__init__(keep_open=keep_open, stop_timeout=stop_timeout)
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app, start_timeout=2, cwd=None):  # type: ignore[reportIncompatibleMethodOverride]
        """Start the server with subprocess and Rscript."""

        if os.path.isfile(app) and os.path.exists(app):
            # app is already a file in a dir - use that as cwd
            if not cwd:
                cwd = os.path.dirname(app)
                logger.info("RRunner inferred cwd from app path: %s", cwd)
        else:
            # app is a string chunk, we make a temporary folder to store app.R
            # and its relevant assets
            tmp_dir = "/tmp" if not self.is_windows else os.getenv("TEMP")
            tmp_dir = str(tmp_dir)  # to satisfy type checking
            hex_id = uuid.uuid4().hex
            self._tmp_app_path = os.path.join(tmp_dir, hex_id)
            try:
                os.mkdir(self.tmp_app_path)  # type: ignore[reportArgumentType]
            except OSError:
                logger.exception("cannot make temporary folder %s", self.tmp_app_path)
            path = os.path.join(self.tmp_app_path, "app.R")  # type: ignore[reportCallIssue]

            logger.info("RRunner start => app is R code chunk")
            logger.info("make a temporary R file for execution => %s", path)
            logger.debug("content of the dashR app")
            logger.debug("%s", app)

            with open(path, "w", encoding="utf-8") as fp:
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
                    target = os.path.join(self.tmp_app_path, os.path.basename(asset))  # type: ignore[reportCallIssue]
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
            f"Rscript -e 'source(\"{os.path.realpath(app)}\")'",
            posix=not self.is_windows,
        )
        logger.debug("start dash process with %s", args)

        try:
            self.proc = subprocess.Popen(  # pylint: disable=consider-using-with
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
        super().__init__(keep_open=keep_open, stop_timeout=stop_timeout)
        self.proc = None

    # pylint: disable=arguments-differ
    def start(self, app, start_timeout=30, cwd=None):  # type: ignore[reportIncompatibleMethodOverride]
        """Start the server with subprocess and julia."""

        if os.path.isfile(app) and os.path.exists(app):
            # app is already a file in a dir - use that as cwd
            if not cwd:
                cwd = os.path.dirname(app)
                logger.info("JuliaRunner inferred cwd from app path: %s", cwd)
        else:
            # app is a string chunk, we make a temporary folder to store app.jl
            # and its relevant assets
            tmp_dir = "/tmp" if not self.is_windows else os.getenv("TEMP")
            assert isinstance(tmp_dir, str)  # to satisfy typing
            hex_id = uuid.uuid4().hex
            self._tmp_app_path = os.path.join(tmp_dir, hex_id)
            assert isinstance(self.tmp_app_path, str)  # to satisfy typing
            try:
                os.mkdir(self.tmp_app_path)
            except OSError:
                logger.exception("cannot make temporary folder %s", self.tmp_app_path)
            path = os.path.join(self.tmp_app_path, "app.jl")

            logger.info("JuliaRunner start => app is Julia code chunk")
            logger.info("make a temporary Julia file for execution => %s", path)
            logger.debug("content of the Dash.jl app")
            logger.debug("%s", app)

            with open(path, "w", encoding="utf-8") as fp:
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
            f"julia --project {os.path.realpath(app)}", posix=not self.is_windows
        )
        logger.debug("start Dash.jl process with %s", args)

        try:
            self.proc = subprocess.Popen(  # pylint: disable=consider-using-with
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
