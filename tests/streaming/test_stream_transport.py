"""Multiplexed streaming transport over shared storage (server side, Flask).

The uplink: a streaming callback POST that carries a streamConnection returns a
fast ack and pumps its frames onto the connection's shared-storage topic (from
which the client's single downlink relays them). Exercised over the real HTTP
dispatch with the default Flask backend.
"""
import json
import threading
import time
import uuid

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


def test_uplink_pumps_callback_frames_to_storage():
    storage = LocalSharedStorage(namespace=f"tx-{uuid.uuid4().hex[:8]}")
    app = Dash(__name__, shared_storage=storage)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def cb(n):
        yield "a"
        yield "b"

    conn, rid = "c1", "r1"
    out = []

    def drain():
        gen = subscribe_envelopes(storage, conn)
        for env in gen:
            out.append(env)
            if env["frame"].get("done"):
                break
        gen.close()

    th = threading.Thread(target=drain, daemon=True)
    th.start()
    time.sleep(0.3)  # subscription established before the pump publishes

    resp = app.server.test_client().post(
        "/_dash-update-component", json=_uplink_body(conn, rid)
    )
    # Fast ack -- the POST does not hold a connection for the stream's life.
    assert resp.status_code == 200
    assert json.loads(resp.get_data(as_text=True)) == {"multi": True, "stream": True}

    th.join(timeout=5)
    assert [e["rid"] for e in out] == ["r1", "r1", "r1"]
    frames = [e["frame"] for e in out]
    assert frames[0]["response"] == {"out": {"children": "a"}}
    assert frames[1]["response"] == {"out": {"children": "b"}}
    assert frames[2] == {"done": True}
    storage.close()
