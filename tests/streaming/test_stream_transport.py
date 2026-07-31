"""Multiplexed streaming transport over shared storage (server side).

The uplink: a streaming callback POST that carries a streamConnection returns a
fast ack and pumps its frames onto the connection's shared-storage topic (from
which the client's single downlink relays them). Exercised over the real HTTP
dispatch on all three backends (Flask WSGI, Quart + FastAPI ASGI).
"""
import asyncio
import json
import threading
import time
import uuid

import pytest

from dash import Dash, Input, Output, html
from dash._shared_storage import LocalSharedStorage
from dash._stream_hub import subscribe_envelopes


def _uplink_body(connection_id, request_id):
    return {
        "output": "out.children",
        "outputs": {"id": "out", "property": "children"},
        "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
        "changedPropIds": ["btn.n_clicks"],
        "streamConnection": {
            "connectionId": connection_id,
            "requestId": request_id,
        },
    }


def _start_drain(storage, connection_id, out):
    """Subscribe to a connection's topic on a daemon thread until 'done'."""

    def drain():
        gen = subscribe_envelopes(storage, connection_id)
        for env in gen:
            out.append(env)
            if env["frame"].get("done"):
                break
        gen.close()

    th = threading.Thread(target=drain, daemon=True)
    th.start()
    time.sleep(0.3)  # subscription established before the pump publishes
    return th


def _streaming_app(server=None):
    storage = LocalSharedStorage(namespace=f"tx-{uuid.uuid4().hex[:8]}")
    kwargs = {"shared_storage": storage}
    if server is not None:
        kwargs["server"] = server  # default (Flask) server otherwise
    app = Dash(__name__, **kwargs)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def cb(n):
        yield "a"
        yield "b"

    return app, storage


def _assert_delivered(out):
    assert [e["rid"] for e in out] == ["r1", "r1", "r1"]
    frames = [e["frame"] for e in out]
    assert frames[0]["response"] == {"out": {"children": "a"}}
    assert frames[1]["response"] == {"out": {"children": "b"}}
    assert frames[2] == {"done": True}


def test_flask_uplink_pumps_callback_frames_to_storage():
    app, storage = _streaming_app()
    out = []
    th = _start_drain(storage, "c1", out)

    resp = app.server.test_client().post(
        "/_dash-update-component", json=_uplink_body("c1", "r1")
    )
    assert resp.status_code == 200
    assert json.loads(resp.get_data(as_text=True)) == {"multi": True, "stream": True}

    th.join(timeout=5)
    _assert_delivered(out)
    storage.close()


def test_fastapi_uplink_pumps_callback_frames_to_storage():
    pytest.importorskip("httpx", reason="fastapi.testclient requires httpx")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    server = FastAPI()
    app, storage = _streaming_app(server=server)
    app._setup_server()  # pylint: disable=protected-access
    out = []
    th = _start_drain(storage, "c1", out)

    with TestClient(server) as client:
        resp = client.post("/_dash-update-component", json=_uplink_body("c1", "r1"))
        assert resp.status_code == 200
        assert resp.json() == {"multi": True, "stream": True}
        th.join(timeout=8)

    _assert_delivered(out)
    storage.close()


def test_quart_uplink_pumps_callback_frames_to_storage():
    quart = pytest.importorskip("quart")

    server = quart.Quart(__name__)
    app, storage = _streaming_app(server=server)
    app._setup_server()  # pylint: disable=protected-access
    out = []
    th = _start_drain(storage, "c1", out)

    async def run():
        client = server.test_client()
        resp = await client.post(
            "/_dash-update-component", json=_uplink_body("c1", "r1")
        )
        assert resp.status_code == 200
        assert await resp.get_json() == {"multi": True, "stream": True}
        # Keep the loop alive so the fire-and-forget pump task delivers.
        for _ in range(100):
            if len(out) >= 3:
                break
            await asyncio.sleep(0.05)

    asyncio.run(run())
    th.join(timeout=5)
    _assert_delivered(out)
    storage.close()
