"""Component suite requests on every backend: a registered resource is served,
an unregistered package or path is a 404, and a real server error stays a 500.

See https://github.com/plotly/dash/issues/4211
"""
import asyncio

import pytest

from dash import Dash, html

REGISTERED = "/_dash-component-suites/dash/dcc/async-dropdown.js"


@pytest.fixture(params=["flask", "quart", "fastapi"])
def backend(request):
    if request.param != "flask":
        pytest.importorskip(request.param)
    return request.param


def get(app, path):
    """GET with the test client of the app's backend."""
    server_type = app.backend.server_type
    if server_type == "fastapi":
        from starlette.testclient import TestClient

        with TestClient(app.server) as client:
            response = client.get(path)
            return response.status_code, response.text

    if server_type == "quart":

        async def run():
            response = await app.server.test_client().get(path)
            return response.status_code, await response.get_data(as_text=True)

        return asyncio.run(run())

    response = app.server.test_client().get(path)
    return response.status_code, response.get_data(as_text=True)


def make_app(backend):
    app = Dash(__name__, backend=backend)
    app.layout = html.Div()
    return app


def test_registered_resource_is_served(backend):
    status, body = get(make_app(backend), REGISTERED)
    assert status == 200
    assert body


@pytest.mark.parametrize("debug", [False, True], ids=["production", "debug"])
@pytest.mark.parametrize(
    "path",
    [
        "/_dash-component-suites/not_registered/af.js",
        "/_dash-component-suites/dash/dcc/not_registered.js",
        "/_dash-component-suites/dash/dcc/not_registered.v1_0_0m1.js",
    ],
    ids=["unknown-package", "unknown-path", "unknown-fingerprinted-path"],
)
def test_unregistered_resource_is_404(backend, path, debug):
    app = make_app(backend)
    if debug:
        app.enable_dev_tools(debug=True, dev_tools_hot_reload=False)
    status, body = get(app, path)
    assert status == 404
    # The request must not be echoed: Flask and Quart would serve it as HTML.
    assert "not_registered" not in body


def test_server_error_is_still_500(backend, monkeypatch):
    calls = []

    def broken_get_data(*args, **_kwargs):
        calls.append(args)
        raise OSError("disk on fire")

    monkeypatch.setattr("pkgutil.get_data", broken_get_data)
    status, _ = get(make_app(backend), REGISTERED)
    assert status == 500
    assert ("dash", "dcc/async-dropdown.js") in calls
