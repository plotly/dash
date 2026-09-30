import json
import os
import signal
import socket
import subprocess
import sys
import textwrap
import time

import pytest
import requests

from dash import Dash, html

FAKE_URL = "https://quick-test-tunnel.trycloudflare.com"


@pytest.fixture
def fake_cloudflared(tmp_path, monkeypatch):
    args_file = tmp_path / "args.json"
    script = tmp_path / "cloudflared"
    script.write_text(
        textwrap.dedent(
            f"""\
            #!{sys.executable}
            import json, os, sys, time
            with open({str(tmp_path / "pid")!r}, "w") as f:
                f.write(str(os.getpid()))
            with open({str(args_file)!r}, "w") as f:
                json.dump(sys.argv[1:], f)
            print("INF Requesting new quick Tunnel on trycloudflare.com...", file=sys.stderr)
            print("INF |  {FAKE_URL}  |", file=sys.stderr, flush=True)
            time.sleep(60)
            """
        )
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    return args_file


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for(condition, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        if condition():
            return
        time.sleep(0.1)
    raise AssertionError("timed out")


@pytest.mark.skipif(sys.platform == "win32", reason="fake cloudflared is a script")
def test_tunn001_run_with_tunnel(dash_thread_server, fake_cloudflared, caplog):
    app = Dash(__name__)
    app.layout = html.Div("tunneled", id="out")

    dash_thread_server(app, tunnel=True)
    tunnel = app._tunnel
    try:
        wait_for(lambda: FAKE_URL in caplog.text)
        assert tunnel.public_url == FAKE_URL
        assert f"Dash is publicly available at {FAKE_URL}/" in caplog.text

        wait_for(fake_cloudflared.exists)
        args = json.loads(fake_cloudflared.read_text())
        assert args[args.index("--url") + 1] == dash_thread_server.url.replace(
            "localhost", "127.0.0.1"
        )
        assert "--no-tls-verify" not in args

        layout = requests.get(f"{dash_thread_server.url}/_dash-layout").json()
        assert layout["props"]["children"] == "tunneled"
    finally:
        tunnel.stop()
    assert tunnel.process.poll() is not None


@pytest.mark.parametrize("env", [None, "0", "false"])
def test_tunn002_no_tunnel_when_off(dash_thread_server, monkeypatch, env):
    if env is not None:
        monkeypatch.setenv("DASH_TUNNEL", env)
    app = Dash(__name__)
    app.layout = html.Div("local")
    dash_thread_server(app)
    assert app._tunnel is None


def test_tunn003_tunnel_failure_keeps_app_running(
    dash_thread_server, monkeypatch, caplog
):
    def fail(*_):
        raise OSError("no network")

    monkeypatch.setattr("dash._tunnel.find_cloudflared", fail)
    monkeypatch.setenv("DASH_TUNNEL", "1")
    app = Dash(__name__)
    app.layout = html.Div("still local")
    dash_thread_server(app)

    assert app._tunnel is None
    assert "Could not start the tunnel: no network" in caplog.text
    layout = requests.get(f"{dash_thread_server.url}/_dash-layout").json()
    assert layout["props"]["children"] == "still local"


@pytest.mark.skipif(sys.platform == "win32", reason="no SIGTERM on Windows")
def test_tunn004_sigterm_stops_tunnel(fake_cloudflared, tmp_path):
    app_file = tmp_path / "app.py"
    app_file.write_text(
        textwrap.dedent(
            """\
            from dash import Dash, html
            app = Dash(__name__)
            app.layout = html.Div("bye")
            app.run(tunnel=True, port={port})
            """
        ).format(port=free_port())
    )
    pid_file = tmp_path / "pid"
    with subprocess.Popen([sys.executable, str(app_file)], cwd=tmp_path) as proc:
        try:
            wait_for(pid_file.exists)
            wait_for(lambda: pid_file.read_text().strip())
            tunnel_pid = int(pid_file.read_text())
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=10)
        finally:
            proc.kill()

    def tunnel_gone():
        try:
            os.kill(tunnel_pid, 0)
        except ProcessLookupError:
            return True
        return False

    wait_for(tunnel_gone)
