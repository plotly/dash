"""after_request hook behavior across backends."""

import asyncio

import pytest

from dash import Dash, html


@pytest.fixture(params=["flask", "quart", "fastapi"])
def backend(request):
    if request.param != "flask":
        pytest.importorskip(request.param)
    return request.param


def get_status(app, path):
    """GET with the test client of the app's backend."""
    server_type = app.backend.server_type
    if server_type == "fastapi":
        from starlette.testclient import TestClient

        with TestClient(app.server) as client:
            response = client.get(path)
            return response.status_code

    if server_type == "quart":

        async def run():
            response = await app.server.test_client().get(path)
            return response.status_code

        return asyncio.run(run())

    response = app.server.test_client().get(path)
    return response.status_code


def make_app(backend):
    app = Dash(__name__, backend=backend)
    app.layout = html.Div()
    return app


def test_after_request_hooks_run_lifo_order(backend):
    app = make_app(backend)
    calls = []

    @app.backend.after_request
    def first(*args):
        calls.append("first")
        if args:
            return args[0]
        return None

    @app.backend.after_request
    def second(*args):
        calls.append("second")
        if args:
            return args[0]
        return None

    assert get_status(app, "/_dash-layout") == 200
    assert calls == ["second", "first"]
