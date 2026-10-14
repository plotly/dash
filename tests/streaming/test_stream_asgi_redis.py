"""Streaming on multi-worker uvicorn with Redis shared storage.

Every browser holds an open downlink. Those must cost a worker nothing but a
waiting task: if each one parks a blocking read in the loop's executor, a dozen
of them starve the worker, and every publish and store call behind them waits
out the read's block timeout. Frames then arrive seconds late, or not at all.
"""
import os
import re
import signal
import socket
import subprocess
import sys
import textwrap
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests

from dash.testing.wait import until

pytest.importorskip("uvicorn")
redis = pytest.importorskip("redis")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


def _redis_available():
    try:
        client = redis.Redis.from_url(REDIS_URL)
        client.ping()
        client.close()
        return True
    except Exception:  # pylint: disable=broad-except
        return False


pytestmark = [
    pytest.mark.skipif(
        sys.platform == "win32", reason="multi-worker uvicorn is POSIX only here"
    ),
    pytest.mark.skipif(
        not _redis_available(), reason="no Redis reachable at REDIS_URL"
    ),
]
# Per worker, comfortably more than the default executor's threads (at most 32).
IDLE_DOWNLINKS = 80

APP = textwrap.dedent(
    """
    import asyncio
    import os
    from dash import Dash, Input, Output, RedisSharedStorage, html

    app = Dash(
        __name__,
        backend=os.environ["TEST_BACKEND"],
        shared_storage=RedisSharedStorage(
            url=os.environ["REDIS_URL"], key_prefix=os.environ["TEST_PREFIX"]
        ),
    )
    # Every worker must verify the others' signed end_id.
    app.server.secret_key = "stream-test"
    app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream(n):
        if not n:
            return
        for i in range(20):
            yield f"token {i} "
            await asyncio.sleep(0.05)

    server = app.server
    """
)


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _end_id(base):
    page = requests.get(base, timeout=5).text
    return re.search(r'"end_id":\s*"([^"]+)"', page).group(1)


def _open_downlink(url):
    resp = requests.post(
        url, json={"streamDownlink": {"from": 0}}, stream=True, timeout=10
    )
    resp.raise_for_status()
    return resp


@pytest.mark.parametrize("backend", ["fastapi", "quart"])
def test_star001_stream_promptly_beside_many_open_downlinks(dash_br, tmp_path, backend):
    pytest.importorskip(backend)
    (tmp_path / "asgi_app.py").write_text(APP)
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    log = (tmp_path / "uvicorn.log").open("wb")
    proc = subprocess.Popen(  # pylint: disable=consider-using-with
        [
            sys.executable,
            "-m",
            "uvicorn",
            "asgi_app:server",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--workers",
            "2",
        ],
        cwd=tmp_path,
        env={
            **os.environ,
            "TEST_BACKEND": backend,
            "REDIS_URL": REDIS_URL,
            "TEST_PREFIX": f"dash:asgitest:{uuid.uuid4().hex[:12]}",
        },
        stdout=subprocess.DEVNULL,
        stderr=log,
        start_new_session=True,
    )
    downlinks = []
    try:

        def up():
            try:
                return requests.get(base, timeout=1).ok
            except requests.RequestException:
                return False

        until(up, timeout=30, poll=0.2, msg="uvicorn never came up")

        # Other browsers, quiet but connected, spread over both workers.
        url = f"{base}/_dash-update-component?endId={_end_id(base)}"
        with ThreadPoolExecutor(max_workers=16) as pool:
            downlinks = list(pool.map(_open_downlink, [url] * IDLE_DOWNLINKS))
        time.sleep(0.5)

        dash_br.server_url = base
        dash_br.find_element("#btn").click()
        started = time.monotonic()
        dash_br.wait_for_contains_text("#out", "token 19", timeout=15)
        # 20 frames 50 ms apart: about 1 s when each frame is delivered as it
        # is produced. A starved worker takes 5 s or more for each frame.
        assert time.monotonic() - started < 4
        assert dash_br.get_logs() == []
    except Exception:
        print((tmp_path / "uvicorn.log").read_text(errors="replace")[-4000:])
        raise
    finally:
        for resp in downlinks:
            resp.close()
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        log.close()
