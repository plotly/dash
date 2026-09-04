"""Ctrl+C must stop a real server while a streaming callback is running.

Drives the same process shape ``app.run()`` spawns for the FastAPI backend
(``python -m uvicorn``): the server's graceful shutdown waits for in-flight
responses, so if the streaming shutdown hook is not wired in, the process
ignores SIGINT until the generator ends.
"""
import os
import signal
import socket
import subprocess
import sys
import textwrap
import threading
import time

import pytest
import requests

from dash.testing.wait import until

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX signals and process groups"
)

APP = textwrap.dedent(
    """
    import asyncio
    from dash import Dash, Input, Output, html

    app = Dash(__name__, backend="{backend}")
    server = app.server
    app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"),
                  prevent_initial_call=True)
    async def stream(n):
        for i in range(10000):
            yield f"token {{i}}"
            await asyncio.sleep(0.2)
    """
)

CALLBACK_BODY = {
    "output": "out.children",
    "outputs": {"id": "out", "property": "children"},
    "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
    "changedPropIds": ["btn.n_clicks"],
    "state": [],
}


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_ready(url, proc, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise AssertionError(f"server exited early: {proc.stderr.read()}")
        try:
            if requests.get(url, timeout=1).status_code == 200:
                return
        except requests.RequestException:
            time.sleep(0.2)
    raise AssertionError("server never came up")


@pytest.mark.parametrize("backend", ["fastapi", "quart"])
def test_stsd001_sigint_stops_server_mid_stream(tmp_path, backend):
    pytest.importorskip(backend)
    (tmp_path / "shutdown_app.py").write_text(APP.format(backend=backend))
    port = _free_port()
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [sys.executable, "-m", "uvicorn", "shutdown_app:server", "--port", str(port)],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONUNBUFFERED="1"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    frames = []
    try:
        base = f"http://127.0.0.1:{port}"
        _wait_ready(base, proc)

        def read_stream():
            with requests.post(
                f"{base}/_dash-update-component",
                json=CALLBACK_BODY,
                stream=True,
                timeout=30,
            ) as resp:
                try:
                    for line in resp.iter_lines():
                        frames.append(line)
                except requests.RequestException:
                    pass

        reader = threading.Thread(target=read_stream, daemon=True)
        reader.start()
        deadline = time.monotonic() + 10
        while len(frames) < 2 and time.monotonic() < deadline:
            time.sleep(0.1)
        assert len(frames) >= 2, "stream never started"

        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            raise AssertionError(  # pylint: disable=raise-missing-from
                "server still running 10s after SIGINT with an active stream"
            )
        output = proc.stdout.read()
        assert "Application shutdown complete" in output, output
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


MUX_APP = textwrap.dedent(
    """
    import asyncio
    from dash import Dash, Input, Output, Patch, html

    app = Dash(__name__, backend="fastapi")
    server = app.server
    app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"),
                  running=[(Output("btn", "disabled"), True, False)],
                  prevent_initial_call=True)
    async def stream(n):
        for i in range(600):
            patch = Patch()
            patch.append(f"t{i} ")
            yield patch
            await asyncio.sleep(0.2)
    """
)

COUNT_DOWNLINKS = """
if (!window.__downlinks) {
    window.__downlinks = 0;
    const orig = window.fetch;
    window.fetch = function(url, init) {
        if (init && init.body && String(init.body).includes('streamDownlink')) {
            window.__downlinks += 1;
        }
        return orig.apply(this, arguments);
    };
}
return window.__downlinks;
"""


def _start_server(tmp_path, port):
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [sys.executable, "-m", "uvicorn", "restart_app:server", "--port", str(port)],
        cwd=tmp_path,
        env=dict(os.environ, PYTHONUNBUFFERED="1"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        _wait_ready(f"http://127.0.0.1:{port}", proc)
    except BaseException:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
        raise
    return proc


def _stop_server(proc):
    if proc.poll() is None:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


def test_stsd002_restart_settles_multiplexed_streams(dash_br, tmp_path):
    """A server restart mid-stream must not leave the page looping.

    The default shared storage puts streams on the multiplexed downlink. When
    the server restarts, its signing secret changes, so the old page's
    downlink is refused: the client must settle the callbacks it was running
    (clearing the running state) and stop reconnecting, and a refreshed page
    must stream again normally.
    """
    (tmp_path / "restart_app.py").write_text(MUX_APP)
    port = _free_port()
    proc = _start_server(tmp_path, port)
    try:
        dash_br.server_url = f"http://127.0.0.1:{port}"
        dash_br.driver.execute_script(COUNT_DOWNLINKS)
        dash_br.find_element("#btn").click()
        dash_br.wait_for_contains_text("#out", "t2")
        assert dash_br.find_element("#btn").get_attribute("disabled")

        _stop_server(proc)
        proc = _start_server(tmp_path, port)

        until(
            lambda: not dash_br.find_element("#btn").get_attribute("disabled"),
            timeout=15,
        )
        # Frames applied before the drop stay on the page.
        assert "t2" in dash_br.find_element("#out").text
        # No reconnect loop against the refused connection.
        count = dash_br.driver.execute_script(COUNT_DOWNLINKS)
        time.sleep(3)
        assert dash_br.driver.execute_script(COUNT_DOWNLINKS) == count

        # Drain the connection-refused entries logged while the server was down.
        dash_br.get_logs()
        dash_br.driver.refresh()
        dash_br.wait_for_element("#btn").click()
        dash_br.wait_for_contains_text("#out", "t2")
        assert dash_br.get_logs() == []
    finally:
        _stop_server(proc)
