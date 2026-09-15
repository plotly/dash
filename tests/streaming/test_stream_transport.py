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
from dash import _callback_signing
from dash._shared_storage import LocalSharedStorage
from dash._stream_hub import subscribe_envelopes

# The connection topic is keyed on the server-signed end_id, not on anything the
# client sends. A test uplink/downlink must carry a validly signed endId (the
# raw value becomes the connection id / topic) or the server refuses to
# multiplex it. See dash/_callback.get_stream_connection_id.
CONNECTION_ID = "conn-test"


def _signed_end_id(app):
    secret = app._get_signing_secret()  # pylint: disable=protected-access
    return _callback_signing.sign(secret, _callback_signing.END_SCOPE, CONNECTION_ID)


def _uplink_url(app):
    return f"/_dash-update-component?endId={_signed_end_id(app)}"


def _uplink_body(request_id):
    return {
        "output": "out.children",
        "outputs": {"id": "out", "property": "children"},
        "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
        "changedPropIds": ["btn.n_clicks"],
        "streamConnection": {"requestId": request_id},
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
    th = _start_drain(storage, CONNECTION_ID, out)

    resp = app.server.test_client().post(_uplink_url(app), json=_uplink_body("r1"))
    assert resp.status_code == 200
    assert json.loads(resp.get_data(as_text=True)) == {"multi": True, "stream": True}

    th.join(timeout=5)
    _assert_delivered(out)
    storage.close()


def test_flask_uplink_without_valid_end_id_is_rejected():
    # A multiplexed uplink (carries a streamConnection) whose endId does not
    # verify is refused outright: it is never run some other way, so no frame is
    # ever published onto a topic without a valid token.
    app, storage = _streaming_app()
    out = []
    th = _start_drain(storage, CONNECTION_ID, out)

    resp = app.server.test_client().post(
        "/_dash-update-component?endId=forged~deadbeef", json=_uplink_body("r1")
    )
    assert resp.status_code == 403
    th.join(timeout=1)
    assert out == []
    storage.close()


def test_flask_downlink_rejects_missing_end_id():
    # A downlink with no valid signed endId cannot name a topic at all: the
    # server refuses it (403) rather than serving an attacker-named connection.
    app, storage = _streaming_app()
    resp = app.server.test_client().post(
        "/_dash-update-component", json={"streamDownlink": {"from": 0}}
    )
    assert resp.status_code == 403
    storage.close()


def test_flask_downlink_resets_a_stale_cursor():
    # A downlink resuming from a cursor the fresh topic never reached (the page's
    # server restarted, so the topic is back at seq 0) gets a reset line, not a
    # silent stall until the new sequence climbs past the stale cursor.
    app, storage = _streaming_app()
    resp = app.server.test_client().post(
        _uplink_url(app), json={"streamDownlink": {"from": 99}}
    )
    assert resp.status_code == 200
    lines = [line for line in resp.get_data(as_text=True).splitlines() if line.strip()]
    assert json.loads(lines[0]) == {"reset": True}
    storage.close()


def test_fastapi_uplink_pumps_callback_frames_to_storage():
    pytest.importorskip("httpx", reason="fastapi.testclient requires httpx")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    server = FastAPI()
    app, storage = _streaming_app(server=server)
    app._setup_server()  # pylint: disable=protected-access
    out = []
    th = _start_drain(storage, CONNECTION_ID, out)

    with TestClient(server) as client:
        resp = client.post(_uplink_url(app), json=_uplink_body("r1"))
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
    th = _start_drain(storage, CONNECTION_ID, out)

    async def run():
        client = server.test_client()
        resp = await client.post(_uplink_url(app), json=_uplink_body("r1"))
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
    pump = hub.pump_to_storage(storage, cid, "r1", marker)
    assert _wait_for(lambda: len(out) >= 3)
    assert not state["cancelled"]

    downlink.close()  # the tab closed
    pump.result(timeout=5)
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


# --- explicit cancellation (a tab closed while the downlink stays shared) -----


def test_stream_cancel_stops_sync_pump_while_downlink_stays_open(monkeypatch):
    from dash import _stream_hub as hub
    from dash._streaming import StreamedCallbackResponse

    monkeypatch.setattr(hub, "DOWNLINK_CHECK_INTERVAL", 0.1)
    storage = _storage("cancel-pump")
    cid = "c6"
    downlink = hub.Downlink(storage, cid)  # stays open: other tabs still stream
    state, frames = _cancellation_probe()
    marker = StreamedCallbackResponse(frames, is_async=True)
    pump = hub.pump_to_storage(storage, cid, "r1", marker)
    assert _wait_for(lambda: state["frames"] >= 2)

    hub.cancel_stream(storage, cid, "r1")
    pump.result(timeout=5)
    assert state["cancelled"]
    assert storage.get(hub.connection_key(cid))["open"] is True
    # The pump cleans up its cancel record once it has acted on it.
    assert storage.get(hub.cancel_key(cid, "r1")) is None
    downlink.close()


_CANCEL_BODY = {"streamCancel": {"requestId": "r9"}}


def _assert_cancel_recorded(storage, status, data):
    from dash import _stream_hub as hub

    assert status == 200
    assert data == hub.STREAM_CANCEL_ACK
    assert hub.stream_cancelled(storage, CONNECTION_ID, "r9")


def test_flask_stream_cancel_endpoint_records_the_request():
    app, storage = _streaming_app()
    client = app.server.test_client()
    response = client.post(_uplink_url(app), json=_CANCEL_BODY)
    _assert_cancel_recorded(storage, response.status_code, response.get_json())
    # Without a valid signed endId a cancel cannot name a connection at all.
    assert client.post("/_dash-update-component", json=_CANCEL_BODY).status_code == 403
    storage.close()


def test_fastapi_stream_cancel_endpoint_records_the_request():
    pytest.importorskip("httpx", reason="fastapi.testclient requires httpx")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    server = FastAPI()
    app, storage = _streaming_app(server=server)
    app._setup_server()  # pylint: disable=protected-access
    with TestClient(server) as client:
        response = client.post(_uplink_url(app), json=_CANCEL_BODY)
    _assert_cancel_recorded(storage, response.status_code, response.json())
    storage.close()


def test_quart_stream_cancel_endpoint_records_the_request():
    quart = pytest.importorskip("quart")

    server = quart.Quart(__name__)
    app, storage = _streaming_app(server=server)
    app._setup_server()  # pylint: disable=protected-access

    async def run():
        resp = await server.test_client().post(_uplink_url(app), json=_CANCEL_BODY)
        return resp.status_code, await resp.get_json()

    status, data = asyncio.run(run())
    _assert_cancel_recorded(storage, status, data)
    storage.close()


# --- process shutdown: Ctrl+C ends live downlinks and pumps -------------------


def test_shutdown_active_streams_ends_live_downlinks_and_pumps():
    from dash import _stream_hub as hub
    from dash._streaming import StreamedCallbackResponse

    storage = _storage("shutdown")
    downlink = hub.Downlink(storage, "c8")
    relayed = []

    def relay():
        for env in downlink.envelopes():
            relayed.append(env)

    relay_th = threading.Thread(target=relay, daemon=True)
    relay_th.start()

    async def scenario():
        state, frames = _cancellation_probe()
        marker = StreamedCallbackResponse(frames, is_async=True)
        hub.spawn_async_pump(storage, "c8", "r1", marker)
        while state["frames"] < 2:
            await asyncio.sleep(0.02)
        hub.shutdown_active_streams()  # what the SIGINT hook does
        await asyncio.sleep(0.3)
        return state

    state = asyncio.run(scenario())
    assert state["cancelled"]
    relay_th.join(timeout=3)
    assert not relay_th.is_alive()  # the downlink response ended
    assert storage.get(hub.connection_key("c8"))["open"] is False


# --- polling downlink (WSGI) --------------------------------------------------


def test_subscription_poll_is_non_blocking_and_advances_the_cursor():
    storage = _storage("poll")
    sub = storage.subscribe("t", replay_from=0)
    started = time.monotonic()
    assert sub.poll(0.0) == []
    assert time.monotonic() - started < 0.2
    storage.publish("t", {"n": 1})
    storage.publish("t", {"n": 2})
    assert sub.poll(0.0) == [(1, {"n": 1}), (2, {"n": 2})]
    assert sub.poll(0.0) == []  # cursor advanced past what was delivered
    sub.close()


def test_poll_downlink_returns_queued_frames_and_heartbeats(monkeypatch):
    from dash import _stream_hub as hub

    storage = _storage("polldl")
    cid = "c9"
    assert hub.poll_downlink(storage, cid, 0) == []
    record = storage.get(hub.connection_key(cid))
    assert record["mode"] == "poll" and record["open"] is True
    first_beat = record["at"]

    hub.publish_frame(storage, cid, "r1", {"multi": True, "response": {"a": 1}})
    hub.publish_frame(storage, cid, "r1", {"multi": True, "response": {"a": 2}})
    envelopes = hub.poll_downlink(storage, cid, 0)
    assert [e["frame"]["response"] for e in envelopes] == [{"a": 1}, {"a": 2}]
    assert [e["seq"] for e in envelopes] == [1, 2]
    # Resuming from the cursor yields only what came after it.
    hub.publish_frame(storage, cid, "r1", {"multi": True, "response": {"a": 3}})
    assert [e["seq"] for e in hub.poll_downlink(storage, cid, 2)] == [3]
    # Heartbeats are throttled: many polls a second, one record write.
    assert storage.get(hub.connection_key(cid))["at"] == first_beat
    monkeypatch.setattr(hub.time, "time", lambda: first_beat + 2.0)
    hub.poll_downlink(storage, cid, 3)
    assert storage.get(hub.connection_key(cid))["at"] == first_beat + 2.0
    monkeypatch.undo()

    # A polling browser counts as present while its heartbeat is fresh, and as
    # gone once it stops polling for longer than POLL_GRACE -- wider than the
    # closed-downlink grace, since a loaded pool can delay polls for seconds.
    beat = storage.get(hub.connection_key(cid))["at"]
    assert not hub.downlink_gone(storage, cid, beat - 100)
    monkeypatch.setattr(hub.time, "time", lambda: beat + hub.DOWNLINK_GRACE + 5.0)
    assert not hub.downlink_gone(storage, cid, beat - 100)
    monkeypatch.setattr(hub.time, "time", lambda: beat + hub.POLL_GRACE + 1.0)
    assert hub.downlink_gone(storage, cid, beat - 100)
    # ...but a pump that just started gives it the grace to resume polling.
    assert not hub.downlink_gone(storage, cid, beat + hub.POLL_GRACE)


def test_flask_downlink_poll_returns_at_once_with_the_queued_frames():
    from dash import _stream_hub as hub

    app, storage = _streaming_app()
    client = app.server.test_client()
    hub.publish_frame(
        storage, CONNECTION_ID, "r1", {"multi": True, "response": {"a": 1}}
    )

    started = time.monotonic()
    response = client.post(_uplink_url(app), json={"streamDownlink": {"from": 0}})
    assert time.monotonic() - started < 1.0  # no waiting: a poll, not a stream
    assert response.status_code == 200
    assert response.content_type.startswith("application/x-ndjson")
    lines = [line for line in response.get_data(as_text=True).split("\n") if line]
    envelopes = [json.loads(line) for line in lines]
    assert [e["frame"]["response"] for e in envelopes] == [{"a": 1}]
    cursor = envelopes[-1]["seq"]

    # Nothing new: an empty body, still at once.
    response = client.post(_uplink_url(app), json={"streamDownlink": {"from": cursor}})
    assert response.get_data(as_text=True) == ""
    assert storage.get(hub.connection_key(CONNECTION_ID))["mode"] == "poll"
    storage.close()


def test_wsgi_pumps_share_one_loop_thread():
    """Many streams on a WSGI worker cost one pump thread, not one each."""
    from dash import _stream_hub as hub
    from dash._streaming import StreamedCallbackResponse

    storage = _storage("pumploop")
    hub.Downlink(storage, "c10")  # a browser is present
    pumps = []
    for i in range(25):
        _state, frames = _cancellation_probe()
        marker = StreamedCallbackResponse(frames, is_async=True)
        pumps.append(hub.pump_to_storage(storage, "c10", f"r{i}", marker))
    assert _wait_for(
        lambda: storage.subscribe(hub.stream_topic("c10"), 0).poll(0.0) != []
    )
    names = [t.name for t in threading.enumerate() if t.name.startswith("dash-stream")]
    assert names.count("dash-stream-pumps") == 1
    assert "dash-stream-bridge" not in names and "dash-stream-pump" not in names
    for i in range(25):
        hub.cancel_stream(storage, "c10", f"r{i}")
    for pump in pumps:
        pump.result(timeout=5)


def test_wsgi_pump_loop_survives_an_exception_raised_into_it():
    """The pump loop carries every stream in the process: an exception raised
    into its thread (a harness that stops every thread an app started) must
    not end it -- and if the thread is gone anyway, the next pump gets a
    fresh loop instead of being scheduled onto a dead one."""
    import ctypes

    from dash import _stream_hub as hub
    from dash._streaming import StreamedCallbackResponse

    storage = _storage("pumprestart")
    hub.Downlink(storage, "c11")
    hub._shared_pump_loop()  # pylint: disable=protected-access
    thread = hub._pump_thread  # pylint: disable=protected-access
    _state, frames = _cancellation_probe()
    pump = hub.pump_to_storage(
        storage, "c11", "r1", StreamedCallbackResponse(frames, is_async=True)
    )
    assert _wait_for(
        lambda: storage.subscribe(hub.stream_topic("c11"), 0).poll(0.0) != []
    )
    # What dash.testing's KillerThread does to "new" threads at teardown.
    assert (
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(thread.ident), ctypes.py_object(SystemExit)
        )
        == 1
    )
    time.sleep(0.3)
    assert thread.is_alive()  # shrugged it off
    _state2, frames2 = _cancellation_probe()
    pump2 = hub.pump_to_storage(
        storage, "c11", "r2", StreamedCallbackResponse(frames2, is_async=True)
    )
    assert _wait_for(lambda: _state2["frames"] >= 2)
    for rid in ("r1", "r2"):
        hub.cancel_stream(storage, "c11", rid)
    pump2.result(timeout=5)
    pump.result(timeout=5)

    # And if the thread is truly gone, the loop is replaced.
    loop = hub._pump_loop  # pylint: disable=protected-access
    loop.call_soon_threadsafe(loop.stop)
    thread.join(timeout=5)
    assert not thread.is_alive()
    _state3, frames3 = _cancellation_probe()
    pump3 = hub.pump_to_storage(
        storage, "c11", "r3", StreamedCallbackResponse(frames3, is_async=True)
    )
    assert _wait_for(lambda: _state3["frames"] >= 1)
    assert hub._pump_thread is not thread  # pylint: disable=protected-access
    hub.cancel_stream(storage, "c11", "r3")
    pump3.result(timeout=5)
