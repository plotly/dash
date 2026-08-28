import os
import sys
import time
from types import SimpleNamespace
from unittest.mock import Mock

import requests
import pytest

import dash
from dash import html
from dash.testing.application_runners import ThreadedRunner, _run_app


def test_threaded_server_smoke(dash_thread_server):
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("click me", id="clicker"),
            html.Div(id="output", children="hello thread"),
        ]
    )
    dash_thread_server(app, debug=True, use_reloader=False, use_debugger=True)
    r = requests.get(dash_thread_server.url)
    assert r.status_code == 200, "the threaded server is reachable"
    assert 'id="react-entry-point"' in r.text, "the entrypoint is present"


def test_threaded_server_wrapped_fastapi(monkeypatch):
    wrapped_server = type(
        "WrappedFastAPI", (), {"__module__": "instrumentation.wrapper"}
    )()
    uvicorn_server = SimpleNamespace(should_exit=False)
    run_options = {}

    def run(**options):
        run_options.update(options)
        while not uvicorn_server.should_exit:
            time.sleep(0.01)

    app = SimpleNamespace(
        server=wrapped_server,
        backend=SimpleNamespace(server_type="fastapi"),
        scripts=SimpleNamespace(config=SimpleNamespace(serve_locally=False)),
        css=SimpleNamespace(config=SimpleNamespace(serve_locally=False)),
        run=run,
        _uvicorn_server=uvicorn_server,
    )
    runner = ThreadedRunner()
    monkeypatch.setattr(runner, "accessible", lambda _url: True)

    try:
        runner.start(app)
        assert "threaded" not in run_options
    finally:
        if runner.started:
            runner.stop()


@pytest.mark.skipif(
    sys.version_info < (3,), reason="requires python3 for process testing"
)
def test_process_server_smoke(dash_process_server):
    cwd = os.getcwd()
    this_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(os.path.join(this_dir, "..", "assets"))
    try:
        os.chdir(assets_dir)
        dash_process_server("simple_app")
        r = requests.get(dash_process_server.url)
        assert r.status_code == 200, "the server is reachable"
        assert 'id="react-entry-point"' in r.text, "the entrypoint is present"
    finally:
        os.chdir(cwd)


@pytest.mark.parametrize(
    ("server_type", "expected_options"),
    [
        ("fastapi", {"port": 8050}),
        ("quart", {"port": 8050}),
        ("flask", {"port": 8050, "threaded": True}),
    ],
)
def test_run_app_uses_backend_type(server_type, expected_options):
    wrapped_server = type(
        "WrappedServer", (), {"__module__": "instrumentation.wrapper"}
    )()
    app = SimpleNamespace(
        server=wrapped_server,
        backend=SimpleNamespace(server_type=server_type),
        run=Mock(),
    )

    _run_app(app, {"port": 8050})

    app.run.assert_called_once_with(**expected_options)
