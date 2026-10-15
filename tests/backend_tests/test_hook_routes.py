"""Hook routes on every backend: sync and async views reading the request
through the backend's request adapter, and FastAPI handlers reading the body
themselves after the Dash middleware parsed it."""
import asyncio
import inspect

import pytest

from dash import Dash, get_app, hooks, html


@pytest.fixture(autouse=True)
def routes_cleanup():
    yield
    hooks._ns["routes"] = []
    hooks._ns["setup"] = []


@pytest.fixture(params=["flask", "quart", "fastapi"])
def backend(request):
    if request.param != "flask":
        pytest.importorskip(request.param)
    return request.param


def post(app, path, body):
    """POST JSON with the test client of the app's backend."""
    server_type = app.backend.server_type
    if server_type == "fastapi":
        from starlette.testclient import TestClient

        with TestClient(app.server) as client:
            response = client.post(path, json=body)
            return response.status_code, response.json()

    if server_type == "quart":

        async def run():
            response = await app.server.test_client().post(path, json=body)
            return response.status_code, await response.get_json()

        return asyncio.run(run())

    response = app.server.test_client().post(path, json=body)
    return response.status_code, response.get_json()


def make_app(backend):
    app = Dash(__name__, backend=backend)
    app.layout = html.Div()
    return app


def test_hook_route_sync(backend):
    if backend == "quart":
        pytest.skip("Quart's request adapter get_json is async")

    @hooks.route("sync_echo", methods=("POST",))
    def sync_echo():
        adapter = get_app().backend.request_adapter()
        return get_app().backend.jsonify({"echo": adapter.get_json()})

    assert post(make_app(backend), "/sync_echo", {"a": 1}) == (200, {"echo": {"a": 1}})


def test_hook_route_async(backend):
    if backend == "flask":
        pytest.importorskip("asgiref")

    @hooks.route("async_echo", methods=("POST",))
    async def async_echo():
        app = get_app()
        data = app.backend.request_adapter().get_json()
        if inspect.isawaitable(data):
            data = await data
        return app.backend.jsonify({"echo": data, "title": app.title})

    app = make_app(backend)
    app.title = "hook app"
    # get_app() must return the app serving the request, not the last created.
    make_app(backend).title = "other app"
    assert post(app, "/async_echo", {"a": 1}) == (
        200,
        {"echo": {"a": 1}, "title": "hook app"},
    )


def test_fastapi_route_reads_own_body():
    pytest.importorskip("fastapi")
    from starlette.requests import Request

    @hooks.setup()
    def add_route(app):
        async def own_body(request: Request):
            return app.backend.jsonify({"own": await request.json()})

        app._add_url("own_body", own_body, ["POST"])

    assert post(make_app("fastapi"), "/own_body", {"a": 1}) == (200, {"own": {"a": 1}})
