"""before_request hooks on the FastAPI backend gate every route, as on Flask
and Quart."""

import pytest

from dash import Dash, Input, Output, _get_app, hooks, html

pytest.importorskip("fastapi")


@pytest.fixture(autouse=True)
def _fresh_app_context():
    # Lifespan resolves the app through get_app(); a context left by an earlier
    # test would win over the app built here.
    _get_app.app_context.set(None)


ROUTES = [
    ("GET", ""),
    ("GET", "_dash-layout"),
    ("GET", "_dash-dependencies"),
    ("GET", "_reload-hash"),
    ("GET", "healthz"),
    ("GET", "secret-export"),
    ("GET", "assets/load.css"),
    ("POST", "api/echo"),
    ("GET", "some/page"),
]


@pytest.fixture
def secret_route():
    @hooks.route(name="secret-export")
    def secret_export():
        return "route secret"

    yield
    hooks._ns["routes"] = []


def _make_app(deny, assets):
    (assets / "load.css").write_text("body {}")
    app = Dash(
        __name__,
        backend="fastapi",
        health_endpoint="healthz",
        assets_folder=str(assets),
    )
    app.layout = html.Div([html.Div("layout", id="o"), html.Button(id="b")])

    @app.callback(
        Output("o", "children"), Input("b", "n_clicks"), api_endpoint="/api/echo"
    )
    def echo(n_clicks=None):
        return "api"

    app.setup_apis()

    def check_auth():
        if app.backend.request_adapter().headers.get("authorization") != "good":
            return deny()
        return None

    app.backend.before_request(check_auth)
    return app


def _deny_with_response():
    from starlette.responses import Response

    return Response("denied", status_code=401)


def _deny_with_tuple():
    return ("denied", 401)


def _deny_with_raise():
    from fastapi import HTTPException

    raise HTTPException(status_code=401, detail="denied")


@pytest.mark.parametrize(
    "deny", [_deny_with_response, _deny_with_tuple, _deny_with_raise]
)
def test_fabr001_hook_gates_every_route(secret_route, deny, tmp_path):
    from starlette.testclient import TestClient

    with TestClient(_make_app(deny, tmp_path).server) as client:
        for method, route in ROUTES:
            kwargs = {"json": {"n_clicks": 1}} if method == "POST" else {}
            denied = client.request(method, f"/{route}", **kwargs)
            assert denied.status_code == 401, f"{method} /{route} was not gated"
            allowed = client.request(
                method, f"/{route}", headers={"authorization": "good"}, **kwargs
            )
            assert allowed.status_code == 200, f"{method} /{route}"


def test_fabr002_hook_gates_mounted_app():
    from fastapi import FastAPI
    from starlette.testclient import TestClient

    app = Dash(
        __name__,
        backend="fastapi",
        requests_pathname_prefix="/dash/",
        routes_pathname_prefix="/",
    )
    app.layout = html.Div("layout")
    app.backend.before_request(
        lambda: (
            None
            if app.backend.request_adapter().headers.get("authorization") == "good"
            else ("denied", 401)
        )
    )
    parent = FastAPI()
    parent.mount("/dash", app.server)

    with TestClient(parent) as client:
        for route in ("_dash-layout", "_dash-dependencies", ""):
            assert client.get(f"/dash/{route}").status_code == 401
            ok = client.get(f"/dash/{route}", headers={"authorization": "good"})
            assert ok.status_code == 200


def test_fabr003_hook_gates_websocket_handshake():
    from starlette.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)
    app.layout = html.Div("layout")
    app.backend.before_request(
        lambda: (
            None
            if app.backend.request_adapter().headers.get("authorization") == "good"
            else ("denied", 401)
        )
    )
    origin = {"origin": "http://testserver"}

    with TestClient(app.server) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/_dash-ws-callback", headers=origin):
                pass
        with client.websocket_connect(
            "/_dash-ws-callback", headers={**origin, "authorization": "good"}
        ):
            pass


@pytest.mark.parametrize(
    "returned, status",
    [
        (("blocked", {"X-Blocked": "1"}), 200),
        (("blocked", [("X-Blocked", "1")]), 200),
        (("blocked", "403 FORBIDDEN", {"X-Blocked": "1"}), 403),
    ],
)
def test_fabr004_hook_returns_flask_style_tuples(returned, status):
    from starlette.testclient import TestClient

    app = Dash(__name__, backend="fastapi")
    app.layout = html.Div("layout")
    app.backend.before_request(lambda: returned)

    with TestClient(app.server) as client:
        r = client.get("/_dash-layout")
        assert r.status_code == status
        assert r.text == "blocked"
        assert r.headers["X-Blocked"] == "1"


def test_fabr005_failing_hook_logs_and_rejects_websocket(caplog):
    from starlette.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)
    app.layout = html.Div("layout")

    def broken():
        raise ValueError("hook bug")

    app.backend.before_request(broken)

    with TestClient(app.server) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/_dash-ws-callback", headers={"origin": "http://testserver"}
            ):
                pass
    assert "hook bug" in caplog.text
