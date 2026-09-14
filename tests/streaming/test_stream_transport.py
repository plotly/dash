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


# --- downlink lifecycle: tab close stops the relay and cancels the pumps ------


def _storage(tag):
    storage = LocalSharedStorage(namespace=f"tx-{tag}-{uuid.uuid4().hex[:8]}")
    storage.start()
    return storage


def _wait_for(pred, timeout=5.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if pred():
            return True
        time.sleep(0.02)
    return pred()


def _stream_threads():
    return [
        t.name
        for t in threading.enumerate()
        if t.name in ("dash-stream-pump", "dash-stream-bridge")
    ]


def test_downlink_gone_semantics(monkeypatch):
    from dash import _stream_hub as hub

    storage = _storage("gone")
    cid = "c1"
    started = time.time()
    # No record yet (downlink open racing the uplink): not gone until grace.
    assert not hub.downlink_gone(storage, cid, started, grace=1.0)
    assert hub.downlink_gone(storage, cid, started - 2.0, grace=1.0)

    downlink = hub.Downlink(storage, cid)
    assert not hub.downlink_gone(storage, cid, started - 100, grace=0.0)
    downlink.close()
    # Closed long before this pump started: the client may be about to open a
    # fresh downlink for its new stream, so the pump gets the full grace.
    monkeypatch.setattr(hub.time, "time", lambda: started + 0.5)
    assert not hub.downlink_gone(storage, cid, started, grace=1.0)
    monkeypatch.setattr(hub.time, "time", lambda: started + 1.5)
    assert hub.downlink_gone(storage, cid, started, grace=1.0)


def test_replaced_downlink_does_not_mark_the_new_one_closed():
    from dash import _stream_hub as hub

    storage = _storage("replace")
    cid = "c2"
    old = hub.Downlink(storage, cid)
    new = hub.Downlink(storage, cid, replay_from=0)  # the client reconnected
    old.close()  # the stale relay winds down late
    assert storage.get(hub.connection_key(cid))["open"] is True
    new.close()
    assert storage.get(hub.connection_key(cid))["open"] is False


def test_sync_downlink_cancel_ends_quiet_relay_thread():
    """Closing the NDJSON body (tab closed) ends the relay even when no frame
    ever arrives to wake the keepalive pump thread."""
    from dash import _stream_hub as hub
    from dash._streaming import ndjson_lines

    storage = _storage("cancel")
    cid = "c3"
    marker = hub.sync_downlink_marker(storage, cid)
    body = ndjson_lines(marker, keepalive=0.05)
    assert next(body) == "\n"  # keepalive: the topic is quiet
    before = len(_stream_threads())
    assert before >= 1
    body.close()
    assert _wait_for(lambda: len(_stream_threads()) < before, timeout=3.0)
    assert storage.get(hub.connection_key(cid))["open"] is False


def _cancellation_probe():
    """An endless async frame generator that records its cancellation."""
    state = {"cancelled": False, "frames": 0}

    async def frames():
        try:
            while True:
                state["frames"] += 1
                yield {"multi": True, "response": {"out": {"children": "x"}}}
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            state["cancelled"] = True
            raise

    return state, frames()


def test_sync_pump_cancels_callback_when_downlink_gone(monkeypatch):
    from dash import _stream_hub as hub
    from dash._streaming import StreamedCallbackResponse

    monkeypatch.setattr(hub, "DOWNLINK_GRACE", 0.3)
    monkeypatch.setattr(hub, "DOWNLINK_CHECK_INTERVAL", 0.1)
    storage = _storage("pump")
    cid = "c4"
    out = []
    downlink = hub.Downlink(storage, cid)

    def drain():
        for env in downlink.envelopes():
            out.append(env)
            if env["frame"].get("done"):
                break

    drain_th = threading.Thread(target=drain, daemon=True)
    drain_th.start()

    state, frames = _cancellation_probe()
    marker = StreamedCallbackResponse(frames, is_async=True)
    pump_th = threading.Thread(
        target=hub.pump_to_storage, args=(storage, cid, "r1", marker), daemon=True
    )
    pump_th.start()
    assert _wait_for(lambda: len(out) >= 3)
    assert not state["cancelled"]

    downlink.close()  # the tab closed
    pump_th.join(timeout=5)
    assert not pump_th.is_alive()
    assert state["cancelled"]
    # Once the frames stop, the pump published a terminal frame so a client
    # that reconnects late resolves the request instead of waiting forever.
    with storage.subscribe(hub.stream_topic(cid), replay_from=0) as sub:
        got = []
        for _seq, message in sub.iter_with_seq():
            got.append(message["frame"])
            if message["frame"].get("done"):
                break
    assert got[-1] == {"done": True}
    assert all(f.get("multi") for f in got[:-1])


def test_async_pump_cancels_callback_when_downlink_gone(monkeypatch):
    from dash import _stream_hub as hub
    from dash._streaming import StreamedCallbackResponse

    monkeypatch.setattr(hub, "DOWNLINK_GRACE", 0.3)
    monkeypatch.setattr(hub, "DOWNLINK_CHECK_INTERVAL", 0.1)
    storage = _storage("apump")
    cid = "c5"
    downlink = hub.Downlink(storage, cid)

    async def scenario():
        state, frames = _cancellation_probe()
        marker = StreamedCallbackResponse(frames, is_async=True)
        task = asyncio.ensure_future(hub.apump_to_storage(storage, cid, "r1", marker))
        while state["frames"] < 3:
            await asyncio.sleep(0.02)
        assert not state["cancelled"]
        downlink.close()  # the tab closed
        await asyncio.wait_for(task, timeout=5)
        return state

    state = asyncio.run(scenario())
    assert state["cancelled"]
    with storage.subscribe(hub.stream_topic(cid), replay_from=0) as sub:
        got = []
        for _seq, message in sub.iter_with_seq():
            got.append(message["frame"])
            if message["frame"].get("done"):
                break
    assert got[-1] == {"done": True}


def test_flask_downlink_close_over_http_releases_relay(monkeypatch):
    """Over real Flask dispatch: the client dropping its downlink response
    ends the relay thread and records the connection closed."""
    from dash import _stream_hub as hub

    app, storage = _streaming_app()
    app._stream_keepalive_interval = 50  # pylint: disable=protected-access
    client = app.server.test_client()
    cid = f"c-{uuid.uuid4().hex[:6]}"
    before = len(_stream_threads())
    response = client.post(
        "/_dash-update-component",
        json={"streamDownlink": {"connectionId": cid, "from": 0}},
        buffered=False,
    )
    assert response.status_code == 200
    lines = response.iter_encoded()
    assert next(lines) == b"\n"  # keepalive: nothing published yet
    assert storage.get(hub.connection_key(cid))["open"] is True
    response.close()  # the tab closed
    assert _wait_for(lambda: len(_stream_threads()) <= before, timeout=3.0)
    assert storage.get(hub.connection_key(cid))["open"] is False
