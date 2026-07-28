"""WebSocket streaming callback tests.

Protocol-level tests (FastAPI TestClient, no browser) verifying that
streaming callbacks emit intermediate callback_response frames with
``stream: true`` followed by a terminal done frame, plus browser tests for the
full renderer round-trip.
"""
import asyncio
import json

import pytest

from dash import Dash, Input, Output, Patch, html


def _collect_stream_messages(ws):
    """Read ws messages, flattening batched arrays, until the terminal frame."""
    out = []
    while True:
        parsed = json.loads(ws.receive_text())
        msgs = parsed if isinstance(parsed, list) else [parsed]
        for msg in msgs:
            if msg.get("type") != "callback_response":
                continue
            out.append(msg)
            payload = msg.get("payload") or {}
            if payload.get("done") or not payload.get("stream"):
                return out


def _make_ws_app():
    from fastapi import FastAPI

    server = FastAPI()
    app = Dash(__name__, server=server, websocket_callbacks=True)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])
    return app, server


def _callback_request(request_id, output_id="out", prop="children"):
    return {
        "type": "callback_request",
        "requestId": request_id,
        "rendererId": "rend1",
        "payload": {
            "output": f"{output_id}.{prop}",
            "outputs": {"id": output_id, "property": prop},
            "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
            "changedPropIds": ["btn.n_clicks"],
        },
    }


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_wsst001_async_stream_frames_over_ws():
    pytest.importorskip("httpx", reason="fastapi.testclient requires httpx")
    from fastapi.testclient import TestClient

    app, server = _make_ws_app()

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream_cb(n):
        yield "start"
        await asyncio.sleep(0.01)
        yield "final"

    app._setup_server()

    client = TestClient(server)
    with client.websocket_connect(
        "/_dash-ws-callback", headers={"origin": "http://testserver"}
    ) as ws:
        ws.send_text(json.dumps(_callback_request("r1")))
        msgs = _collect_stream_messages(ws)

    assert [m["requestId"] for m in msgs] == ["r1"] * 3
    assert msgs[0]["payload"]["stream"] is True
    assert msgs[0]["payload"]["data"]["response"] == {"out": {"children": "start"}}
    assert msgs[1]["payload"]["data"]["response"] == {"out": {"children": "final"}}
    assert msgs[2]["payload"] == {"status": "ok", "stream": True, "done": True}


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_wsst002_sync_stream_frames_over_ws():
    pytest.importorskip("httpx", reason="fastapi.testclient requires httpx")
    from fastapi.testclient import TestClient

    app, server = _make_ws_app()

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def stream_cb(n):
        yield "s1"
        yield "s2"

    app._setup_server()

    client = TestClient(server)
    with client.websocket_connect(
        "/_dash-ws-callback", headers={"origin": "http://testserver"}
    ) as ws:
        ws.send_text(json.dumps(_callback_request("r1")))
        msgs = _collect_stream_messages(ws)

    assert msgs[0]["payload"]["data"]["response"] == {"out": {"children": "s1"}}
    assert msgs[1]["payload"]["data"]["response"] == {"out": {"children": "s2"}}
    assert msgs[2]["payload"] == {"status": "ok", "stream": True, "done": True}


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_wsst003_stream_error_over_ws():
    pytest.importorskip("httpx", reason="fastapi.testclient requires httpx")
    from fastapi.testclient import TestClient

    app, server = _make_ws_app()

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream_cb(n):
        yield "one"
        raise ValueError("boom")

    app._setup_server()

    client = TestClient(server)
    with client.websocket_connect(
        "/_dash-ws-callback", headers={"origin": "http://testserver"}
    ) as ws:
        ws.send_text(json.dumps(_callback_request("r1")))
        msgs = _collect_stream_messages(ws)

    assert msgs[0]["payload"]["data"]["response"] == {"out": {"children": "one"}}
    assert msgs[1]["payload"]["status"] == "error"
    assert "boom" in msgs[1]["payload"]["message"]


def test_wsst004_browser_stream_over_websocket(dash_duo):
    """Full round-trip: streamed frames render progressively over WS."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="out", children="idle"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        yield "streaming"
        for token in ["a", "b", "c"]:
            await asyncio.sleep(0.2)
            patch = Patch()
            patch += token
            yield patch

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "idle")
    dash_duo.find_element("#btn").click()
    # Intermediate frame renders before the stream finishes.
    dash_duo.wait_for_text_to_equal("#out", "streaming")
    # Patch frames appended exactly once each.
    dash_duo.wait_for_text_to_equal("#out", "streamingabc")
    assert dash_duo.get_logs() == []
