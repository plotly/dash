import asyncio
import io
import inspect
import logging
import os
import queue
import uuid
import re
import sys
import threading
import time
import traceback

from typing_extensions import Literal

from werkzeug.serving import make_server


try:
    from IPython import get_ipython
    from IPython.display import IFrame, display, Javascript
    from IPython.core.display import HTML
    from IPython.core.ultratb import FormattedTB
    from retrying import retry
    from ansi2html import Ansi2HTMLConverter
    from ipykernel.comm import Comm
    import nest_asyncio

    import requests

    _dash_comm = Comm(target_name="dash")
    _dep_installed = True
except ImportError:
    _dep_installed = False
    _dash_comm = None
    get_ipython = lambda: None

JupyterDisplayMode = Literal["inline", "external", "jupyterlab", "tab", "_none"]


def _get_skip(error: Exception):
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    skip = 0
    for i, line in enumerate(tb):
        if "%% callback invoked %%" in line:
            skip = i + 1
            break
    return skip


def _custom_formatargvalues(
    args,
    varargs,
    varkw,
    locals,  # pylint: disable=W0622
    formatarg=str,
    formatvarargs=lambda name: "*" + name,
    formatvarkw=lambda name: "**" + name,
    formatvalue=lambda value: "=" + repr(value),
):

    """Copied from inspect.formatargvalues, modified to place function
    arguments on separate lines"""

    # pylint: disable=W0622
    def convert(name, locals=locals, formatarg=formatarg, formatvalue=formatvalue):
        return formatarg(name) + formatvalue(locals[name])

    specs = []

    # pylint: disable=C0200
    for i in range(len(args)):
        specs.append(convert(args[i]))
    if varargs:
        specs.append(formatvarargs(varargs) + formatvalue(locals[varargs]))
    if varkw:
        specs.append(formatvarkw(varkw) + formatvalue(locals[varkw]))

    result = "(" + ", ".join(specs) + ")"

    if len(result) < 40:
        return result
    # Put each arg on a separate line
    return "(\n    " + ",\n    ".join(specs) + "\n)"


_jupyter_config = {}

_caller = {}


def _send_jupyter_config_comm_request():
    # If running in an ipython kernel,
    # request that the front end extension send us the notebook server base URL
    if get_ipython() is not None:
        if _dash_comm.kernel is not None:
            _caller["parent"] = _dash_comm.kernel.get_parent()
            _dash_comm.send({"type": "base_url_request"})


def _jupyter_comm_response_received():
    return bool(_jupyter_config)


def _request_jupyter_config(timeout=2):
    # Heavily inspired by implementation of CaptureExecution in the
    if _dash_comm.kernel is None:
        # Not in jupyter setting
        return

    _send_jupyter_config_comm_request()

    # Get shell and kernel
    shell = get_ipython()
    kernel = shell.kernel

    # Start capturing shell events to replay later
    captured_events = []

    def capture_event(stream, ident, parent):
        captured_events.append((stream, ident, parent))

    kernel.shell_handlers["execute_request"] = capture_event

    # increment execution count to avoid collision error
    shell.execution_count += 1

    # Allow kernel to execute comms until we receive the jupyter configuration comm
    # response
    t0 = time.time()
    while True:
        if (time.time() - t0) > timeout:
            # give up
            raise EnvironmentError(
                "Unable to communicate with the jupyter_dash notebook or JupyterLab \n"
                "extension required to infer Jupyter configuration."
            )
        if _jupyter_comm_response_received():
            break

        if asyncio.iscoroutinefunction(kernel.do_one_iteration):
            loop = asyncio.get_event_loop()
            nest_asyncio.apply(loop)
            loop.run_until_complete(kernel.do_one_iteration())
        else:
            kernel.do_one_iteration()

    # Stop capturing events, revert the kernel shell handler to the default
    # execute_request behavior
    kernel.shell_handlers["execute_request"] = kernel.execute_request

    # Replay captured events
    # need to flush before replaying so messages show up in current cell not
    # replay cells
    sys.stdout.flush()
    sys.stderr.flush()

    for stream, ident, parent in captured_events:
        # Using kernel.set_parent is the key to getting the output of the replayed
        # events to show up in the cells that were captured instead of the current cell
        kernel.set_parent(ident, parent)
        kernel.execute_request(stream, ident, parent)


class JupyterDash:
    """
    Interact with dash apps inside jupyter notebooks.
    """

    default_mode: JupyterDisplayMode = "inline"
    alive_token = str(uuid.uuid4())
    inline_exceptions: bool = True

    _servers = {}

    def infer_jupyter_proxy_config(self):
        """
        Infer the current Jupyter server configuration. This will detect
        the proper request_pathname_prefix and server_url values to use when
        displaying Dash apps.Dash requests will be routed through the proxy.

        Requirements:

        In the classic notebook, this method requires the `dash` nbextension
        which should be installed automatically with the installation of the
        jupyter-dash Python package. You can see what notebook extensions are installed
        by running the following command:
            $ jupyter nbextension list

        In JupyterLab, this method requires the `@plotly/dash-jupyterlab` labextension. This
        extension should be installed automatically with the installation of the
        jupyter-dash Python package, but JupyterLab must be allowed to rebuild before
        the extension is activated (JupyterLab should automatically detect the
        extension and produce a popup dialog asking for permission to rebuild). You can
        see what JupyterLab extensions are installed by running the following command:
            $ jupyter labextension list
        """
        if not self.in_ipython or self.in_colab:
            # No op when not running in a Jupyter context or when in Colab
            return
        # Assume classic notebook or JupyterLab
        _request_jupyter_config()

    def __init__(self):
        self.in_ipython = get_ipython() is not None
        self.in_colab = "google.colab" in sys.modules

        if _dep_installed and self.in_ipython and _dash_comm:

            @_dash_comm.on_msg
            def _receive_message(msg):
                prev_parent = _caller.get("parent")
                if prev_parent and prev_parent != _dash_comm.kernel.get_parent():
                    _dash_comm.kernel.set_parent(
                        [prev_parent["header"]["session"]], prev_parent
                    )
                    del _caller["parent"]

                msg_data = msg.get("content").get("data")
                msg_type = msg_data.get("type", None)
                if msg_type == "base_url_response":
                    _jupyter_config.update(msg_data)

    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    def run_app(
        self,
        app,
        mode: JupyterDisplayMode = None,
        width="100%",
        height=650,
        host="127.0.0.1",
        port=8050,
        server_url=None,
    ):
        """
        :type app: dash.Dash
        :param mode: How to display the app on the notebook. One Of:
            ``"external"``: The URL of the app will be displayed in the notebook
                output cell. Clicking this URL will open the app in the default
                web browser.
            ``"inline"``: The app will be displayed inline in the notebook output cell
                in an iframe.
            ``"jupyterlab"``: The app will be displayed in a dedicate tab in the
                JupyterLab interface. Requires JupyterLab and the `jupyterlab-dash`
                extension.
        :param width: Width of app when displayed using mode="inline"
        :param height: Height of app when displayed using mode="inline"
        :param host: Host of the server
        :param port: Port used by the server
        :param server_url: Use if a custom url is required to display the app.
        """
        # Validate / infer display mode
        if self.in_colab:
            valid_display_values = ["inline", "external"]
        else:
            valid_display_values = ["jupyterlab", "inline", "external", "tab", "_none"]

        if mode is None:
            mode = self.default_mode
        elif not isinstance(mode, str):
            raise ValueError(
                f"The mode argument must be a string\n"
                f"    Received value of type {type(mode)}: {repr(mode)}"
            )
        else:
            mode = mode.lower()
            if mode not in valid_display_values:
                raise ValueError(
                    f"Invalid display argument {mode}\n"
                    f"    Valid arguments: {valid_display_values}"
                )

        # Terminate any existing server using this port
        old_server = self._servers.get((host, port))
        if old_server:
            old_server.shutdown()
            del self._servers[(host, port)]

        # Configure pathname prefix
        if "base_subpath" in _jupyter_config:
            requests_pathname_prefix = (
                _jupyter_config["base_subpath"].rstrip("/") + "/proxy/{port}/"
            )
        else:
            requests_pathname_prefix = app.config.get("requests_pathname_prefix", None)

        if requests_pathname_prefix is not None:
            requests_pathname_prefix = requests_pathname_prefix.format(port=port)
        else:
            requests_pathname_prefix = "/"

        # FIXME Move config initialization to main dash __init__
        # low-level setter to circumvent Dash's config locking
        # normally it's unsafe to alter requests_pathname_prefix this late, but
        # Jupyter needs some unusual behavior.
        dict.__setitem__(
            app.config, "requests_pathname_prefix", requests_pathname_prefix
        )

        # # Compute server_url url
        if server_url is None:
            if "server_url" in _jupyter_config:
                server_url = _jupyter_config["server_url"].rstrip("/")
            else:
                domain_base = os.environ.get("DASH_DOMAIN_BASE", None)
                if domain_base:
                    # Dash Enterprise sets DASH_DOMAIN_BASE environment variable
                    server_url = "https://" + domain_base
                else:
                    server_url = f"http://{host}:{port}"
        else:
            server_url = server_url.rstrip("/")

        # server_url = "http://{host}:{port}".format(host=host, port=port)

        dashboard_url = f"{server_url}{requests_pathname_prefix}"

        # prevent partial import of orjson when it's installed and mode=jupyterlab
        # TODO: why do we need this? Why only in this mode? Importing here in
        # all modes anyway, in case there's a way it can pop up in another mode
        try:
            # pylint: disable=C0415,W0611
            import orjson  # noqa: F401
        except ImportError:
            pass

        err_q = queue.Queue()

        server = make_server(host, port, app.server, threaded=True, processes=0)
        logging.getLogger("werkzeug").setLevel(logging.ERROR)

        @retry(
            stop_max_attempt_number=15,
            wait_exponential_multiplier=100,
            wait_exponential_max=1000,
        )
        def run():
            try:
                server.serve_forever()
            except SystemExit:
                pass
            except Exception as error:
                err_q.put(error)
                raise error

        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

        self._servers[(host, port)] = server

        # Wait for server to start up
        alive_url = f"http://{host}:{port}/_alive_{JupyterDash.alive_token}"

        def _get_error():
            try:
                err = err_q.get_nowait()
                if err:
                    raise err
            except queue.Empty:
                pass

        # Wait for app to respond to _alive endpoint
        @retry(
            stop_max_attempt_number=15,
            wait_exponential_multiplier=10,
            wait_exponential_max=1000,
        )
        def wait_for_app():
            _get_error()
            try:
                req = requests.get(alive_url)
                res = req.content.decode()
                if req.status_code != 200:
                    raise Exception(res)

                if res != "Alive":
                    url = f"http://{host}:{port}"
                    raise OSError(
                        f"Address '{url}' already in use.\n"
                        "    Try passing a different port to run_server."
                    )
            except requests.ConnectionError as err:
                _get_error()
                raise err

        try:
            wait_for_app()

            if self.in_colab:
                JupyterDash._display_in_colab(dashboard_url, port, mode, width, height)
            else:
                JupyterDash._display_in_jupyter(
                    dashboard_url, port, mode, width, height
                )
        except Exception as final_error:  # pylint: disable=broad-except
            msg = str(final_error)
            if msg.startswith("<!"):
                display(HTML(msg))
            else:
                raise final_error

    @staticmethod
    def _display_in_colab(dashboard_url, port, mode, width, height):
        # noinspection PyUnresolvedReferences
        from google.colab import output  # pylint: disable=E0401,E0611,C0415

        if mode == "inline":
            output.serve_kernel_port_as_iframe(port, width=width, height=height)
        elif mode == "external":
            # FIXME there is a 403 on this, maybe it's updated?
            # Display a hyperlink that can be clicked to open Dashboard
            print("Dash app running on:")
            output.serve_kernel_port_as_window(port, anchor_text=dashboard_url)

    @staticmethod
    def _display_in_jupyter(dashboard_url, port, mode, width, height):
        if mode == "inline":
            display(IFrame(dashboard_url, width, height))
        elif mode in ("external", "tab"):
            # Display a hyperlink that can be clicked to open Dashboard
            print(f"Dash app running on {dashboard_url}")
            if mode == "tab":
                display(Javascript(f"window.open('{dashboard_url}')"))
        elif mode == "jupyterlab":
            # Update front-end extension
            # FIXME valid only in jupyterlab but accepted in regular notebooks show nothing.
            _dash_comm.send(
                {
                    "type": "show",
                    "port": port,
                    "url": dashboard_url,
                }
            )

    @staticmethod
    def serve_alive():
        return "Alive"

    def configure_callback_exception_handling(self, app, dev_tools_prune_errors):
        """Install traceback handling for callbacks"""

        @app.server.errorhandler(Exception)
        def _wrap_errors(error):
            # Compute number of stack frames to skip to get down to callback
            skip = _get_skip(error) if dev_tools_prune_errors else 0

            # Customized formatargvalues function we can place function parameters
            # on separate lines
            original_formatargvalues = inspect.formatargvalues
            inspect.formatargvalues = _custom_formatargvalues
            try:
                # Use IPython traceback formatting to build colored ANSI traceback
                # string
                ostream = io.StringIO()
                ipytb = FormattedTB(
                    tb_offset=skip,
                    mode="Verbose",
                    color_scheme="Linux",
                    include_vars=True,
                    ostream=ostream,
                )
                ipytb()
            finally:
                # Restore formatargvalues
                inspect.formatargvalues = original_formatargvalues

            # Print colored ANSI representation if requested
            ansi_stacktrace = ostream.getvalue()

            if self.inline_exceptions:
                print(ansi_stacktrace)

            # Use ansi2html to convert the colored ANSI string to HTML
            conv = Ansi2HTMLConverter(scheme="ansi2html", dark_bg=False)
            html_str = conv.convert(ansi_stacktrace)

            # Set width to fit 75-character wide stack trace and font to a size the
            # won't require a horizontal scroll bar
            html_str = html_str.replace(
                "<html>", '<html style="width: 75ch; font-size: 0.86em">'
            )

            # Remove explicit background color so Dash dev-tools can set background
            # color
            html_str = re.sub("background-color:[^;]+;", "", html_str)

            return html_str, 500

    @property
    def active(self):
        _inside_dbx = "DATABRICKS_RUNTIME_VERSION" in os.environ
        return _dep_installed and not _inside_dbx and (self.in_ipython or self.in_colab)


jupyter_dash = JupyterDash()
