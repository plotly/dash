import os
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
    ("env", "run_kwargs", "expected_host", "expected_port"),
    [
        # DASH_HOST/DASH_PORT win over the generic HOST/PORT.
        (
            {
                "DASH_HOST": "0.0.0.0",
                "DASH_PORT": "8060",
                "HOST": "192.0.2.1",
                "PORT": "8070",
            },
            {},
            "0.0.0.0",
            8060,
        ),
        # Generic HOST/PORT still work when the DASH_ ones are absent.
        ({"HOST": "192.0.2.1", "PORT": "8070"}, {}, "192.0.2.1", 8070),
        # Each DASH_ variable falls back independently.
        ({"DASH_HOST": "0.0.0.0", "PORT": "8070"}, {}, "0.0.0.0", 8070),
        ({"HOST": "192.0.2.1", "DASH_PORT": "8060"}, {}, "192.0.2.1", 8060),
        # Defaults when no relevant variable is set.
        ({}, {}, "127.0.0.1", 8050),
        # Explicit arguments win over environment variables.
        (
            {"DASH_HOST": "0.0.0.0", "DASH_PORT": "8060"},
            {"host": "192.0.2.1", "port": 8070},
            "192.0.2.1",
            8070,
        ),
        # DASH_HOST is honored even under conda, where the generic HOST
        # is ignored because some conda systems set it to an invalid
        # hostname (see #3069).
        (
            {"CONDA_PREFIX": "/opt/conda", "DASH_HOST": "0.0.0.0"},
            {},
            "0.0.0.0",
            8050,
        ),
        # ... and without DASH_HOST the conda workaround still applies.
        (
            {"CONDA_PREFIX": "/opt/conda", "HOST": "192.0.2.1"},
            {},
            "127.0.0.1",
            8050,
        ),
    ],
)
def test_run_host_port_env_vars(
    monkeypatch, env, run_kwargs, expected_host, expected_port
):
    for var in ("DASH_HOST", "DASH_PORT", "HOST", "PORT", "CONDA_PREFIX"):
        monkeypatch.delenv(var, raising=False)
    for var, value in env.items():
        monkeypatch.setenv(var, value)

    app = dash.Dash(__name__)
    run = Mock()
    monkeypatch.setattr(app.backend, "run", run)

    app.run(debug=False, **run_kwargs)

    run.assert_called_once()
    assert run.call_args.kwargs["host"] == expected_host
    assert run.call_args.kwargs["port"] == expected_port


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
