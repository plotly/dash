"""after_request hook behavior across backends."""

import asyncio

import pytest

from dash import Dash, html


@pytest.fixture(params=["flask", "quart", "fastapi"])
def backend(request):
    if request.param != "flask":
        pytest.importorskip(request.param)
    return request.param


def get(app, path):
    """GET with the test client of the app's backend, returning
    ``(status, headers, body)``."""
    server_type = app.backend.server_type
    if server_type == "fastapi":
        from starlette.testclient import TestClient

        with TestClient(app.server) as client:
            response = client.get(path)
            return response.status_code, response.headers, response.content

    if server_type == "quart":

        async def run():
            response = await app.server.test_client().get(path)
            return response.status_code, response.headers, await response.get_data()

        return asyncio.run(run())

    response = app.server.test_client().get(path)
    return response.status_code, response.headers, response.data


def make_app(backend):
    app = Dash(__name__, backend=backend)
    app.layout = html.Div()
    return app


def test_after_request_hooks_get_response_lifo(backend):
    app = make_app(backend)
    calls = []

    @app.backend.after_request
    def first(response):
        calls.append(("first", response.headers.get("X-Hook")))
        response.headers["X-Hook"] = "first"
        return response

    @app.backend.after_request
    def second(response):
        calls.append(("second", response.headers.get("X-Hook")))
        response.headers["X-Hook"] = "second"
        response.headers["X-Second"] = "1"
        return response

    status, headers, _ = get(app, "/_dash-layout")
    assert status == 200
    assert calls == [("second", None), ("first", "second")]
    assert headers["X-Hook"] == "first"
    assert headers["X-Second"] == "1"


@pytest.mark.parametrize("server", ["quart", "fastapi"])
def test_after_request_async_and_zero_arg_hooks(server):
    pytest.importorskip(server)
    app = make_app(server)
    calls = []

    @app.backend.after_request
    def no_args():
        calls.append("no_args")
        return True

    @app.backend.after_request
    async def async_hook(response):
        calls.append("async_hook")
        response.headers["X-Async"] = "1"

    status, headers, _ = get(app, "/_dash-layout")
    assert status == 200
    assert calls == ["async_hook", "no_args"]
    assert headers["X-Async"] == "1"


def test_after_request_hook_replaces_response(backend):
    app = make_app(backend)

    @app.backend.after_request
    def replace(_response):
        return app.backend.make_response("replaced", mimetype="text/plain", status=202)

    status, _, body = get(app, "/_dash-layout")
    assert status == 202
    assert body == b"replaced"


def test_after_request_runs_on_user_routes(backend):
    app = make_app(backend)

    @app.backend.after_request
    def hook(response):
        response.headers["X-Test"] = "1"
        return response

    def custom():
        return app.backend.make_response("custom", mimetype="text/plain")

    app.backend.add_url_rule("/custom", view_func=custom, endpoint="custom")

    status, headers, body = get(app, "/custom")
    assert status == 200
    assert body == b"custom"
    assert headers["X-Test"] == "1"
