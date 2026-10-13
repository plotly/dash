"""Streaming over the multiplexed transport on gunicorn sync workers.

gunicorn's default sync worker serves one request at a time. The client must
open its long-lived downlink only once the uplink is acknowledged, otherwise
the downlink holds the only worker and the stream never starts.

With several workers, each must verify the stream token another one signed,
so they need a shared signing secret (``server.secret_key`` or
``DASH_SECRET_KEY``).
"""
import contextlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
import textwrap
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="gunicorn is POSIX only"
)
pytest.importorskip("gunicorn")

APP = textwrap.dedent(
    """
    import asyncio
    import os
    from dash import Dash, Input, Output, html

    app = Dash(__name__)
    server = app.server

    @server.after_request
    def tag_worker(response):
        response.headers["X-Worker-Pid"] = str(os.getpid())
        return response

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


@contextlib.contextmanager
def _gunicorn(tmp_path, workers, env=None):
    (tmp_path / "wsgi_app.py").write_text(APP)
    port = _free_port()
    proc_env = {k: v for k, v in os.environ.items() if k.lower() != "dash_secret_key"}
    proc_env.update(env or {})
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [
            sys.executable,
            "-m",
            "gunicorn",
            "wsgi_app:server",
            "--bind",
            f"127.0.0.1:{port}",
            "--workers",
            str(workers),
            "--timeout",
            "30",
        ],
        cwd=tmp_path,
        env=proc_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                if requests.get(url, timeout=1).ok:
                    break
            except requests.RequestException:
                time.sleep(0.2)
        else:
            raise AssertionError("gunicorn never came up")
        yield url
    finally:
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


def _downlink_polls(url, polls=40):
    """Poll the downlink with one page load's token from many connections at
    once, so the polls spread over the workers (one idle sync worker would take
    them all if sent one by one). Returns the pid of the worker that served the
    page and a ``(pid, status)`` per poll, from at least two workers."""
    page = requests.get(url, timeout=5)
    config = json.loads(
        re.search(
            r'<script id="_dash-config"[^>]*>(.*?)</script>', page.text, re.S
        ).group(1)
    )

    def poll(_):
        resp = requests.post(
            f"{url}/_dash-update-component",
            params={"endId": config["end_id"]},
            json={"streamDownlink": {"from": 0}},
            headers={"Connection": "close"},
            timeout=5,
        )
        return resp.headers["X-Worker-Pid"], resp.status_code

    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for _ in range(5):
            results += pool.map(poll, range(polls))
            if len({pid for pid, _ in results}) > 1:
                break
    assert len({pid for pid, _ in results}) > 1, "polls never left one worker"
    return page.headers["X-Worker-Pid"], results


def _stream_completes(dash_br, url):
    dash_br.server_url = url
    dash_br.find_element("#btn").click()
    started = time.monotonic()
    # Well under gunicorn's worker timeout: the stream must not need the
    # worker to be killed and respawned before it starts.
    dash_br.wait_for_contains_text("#out", "token 1", timeout=10)
    assert time.monotonic() - started < 10
    dash_br.wait_for_contains_text("#out", "token 19", timeout=15)
    assert dash_br.get_logs() == []


def test_stwg001_single_sync_worker_streams_promptly(dash_br, tmp_path):
    with _gunicorn(tmp_path, workers=1) as url:
        _stream_completes(dash_br, url)


def test_stwg002_workers_share_dash_secret_key(dash_br, tmp_path):
    with _gunicorn(tmp_path, workers=4, env={"DASH_SECRET_KEY": "shared"}) as url:
        _, polls = _downlink_polls(url)
        assert {status for _, status in polls} == {200}
        _stream_completes(dash_br, url)


def test_stwg003_workers_without_shared_secret_refuse_streams(tmp_path):
    # Keeps the multi-worker failure visible: each worker makes up its own
    # secret, so a token only verifies on the worker that signed it.
    with _gunicorn(tmp_path, workers=4) as url:
        page_pid, polls = _downlink_polls(url)
    for pid, status in polls:
        assert status == (200 if pid == page_pid else 403)
