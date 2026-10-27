"""before_request hooks on the Quart backend also gate the WebSocket handshake."""

import asyncio

import pytest

from dash import Dash, html

pytest.importorskip("quart")


def test_qbr001_hook_gates_websocket_handshake():
    from quart.testing import WebsocketResponseError

    app = Dash(__name__, backend="quart", websocket_callbacks=True)
    app.layout = html.Div("layout")
    app.backend.before_request(
        lambda: (
            None
            if app.backend.request_adapter().headers.get("authorization") == "good"
            else ("denied", 401)
        )
    )
    origin = {"origin": "http://localhost"}

    async def connect(headers):
        client = app.server.test_client()
        try:
            async with client.websocket("/_dash-ws-callback", headers=headers) as ws:
                # The test client only surfaces a rejected handshake on receive.
                try:
                    await asyncio.wait_for(ws.receive(), 1)
                except asyncio.TimeoutError:
                    pass
                return "accepted"
        except WebsocketResponseError as err:
            return err.response.status_code

    assert asyncio.run(connect(origin)) == 401
    assert asyncio.run(connect({**origin, "authorization": "good"})) == "accepted"
