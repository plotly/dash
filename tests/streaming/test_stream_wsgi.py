"""Streaming over the multiplexed transport on a single-threaded WSGI worker.

gunicorn's default sync worker serves one request at a time. The client must
open its long-lived downlink only once the uplink is acknowledged, otherwise
the downlink holds the only worker and the stream never starts.
"""
import os
import signal
import socket
import subprocess
import sys
import textwrap
import time

import pytest
import requests

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="gunicorn is POSIX only"
)
pytest.importorskip("gunicorn")

APP = textwrap.dedent(
    """
    import asyncio
    from dash import Dash, Input, Output, html

    app = Dash(__name__)
    server = app.server
    app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream(n):
        if not n:
            return
        for i in range(20):
            yield f"token {i} "
            await asyncio.sleep(0.2)
    """
)


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_stwg001_single_sync_worker_streams_promptly(dash_br, tmp_path):
    (tmp_path / "wsgi_app.py").write_text(APP)
    port = _free_port()
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [
            sys.executable,
            "-m",
            "gunicorn",
            "wsgi_app:server",
            "--bind",
            f"127.0.0.1:{port}",
            "--workers",
            "1",
            "--timeout",
            "30",
        ],
        cwd=tmp_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                if requests.get(f"http://127.0.0.1:{port}", timeout=1).ok:
                    break
            except requests.RequestException:
                time.sleep(0.2)
        else:
            raise AssertionError("gunicorn never came up")

        dash_br.server_url = f"http://127.0.0.1:{port}"
        dash_br.find_element("#btn").click()
        started = time.monotonic()
        # Well under gunicorn's worker timeout: the stream must not need the
        # worker to be killed and respawned before it starts.
        dash_br.wait_for_contains_text("#out", "token 1", timeout=10)
        assert time.monotonic() - started < 10
        dash_br.wait_for_contains_text("#out", "token 19", timeout=15)
        assert dash_br.get_logs() == []
    finally:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
