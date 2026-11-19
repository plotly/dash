import asyncio
import json
import logging
import time

import websocket

from dash import Dash, html, hooks


class _ListHandler(logging.Handler):
    def __init__(self):
        super().__init__(logging.ERROR)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def test_ws060_disconnect_seen_by_sender_first(dash_thread_server, ws_hook_cleanup):
    """A disconnect the sender hits first must not log an ASGI error (#4157)."""
    handled = []

    @hooks.websocket_message()
    async def slow(_websocket, message):
        # Keep the receive loop busy so the sender finds the closed socket
        # before the next receive.
        await asyncio.sleep(0.5)
        handled.append(message)
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)
    app.layout = html.Div()

    dash_thread_server(app)
    # Added after start: uvicorn's dictConfig resets this logger's handlers.
    log_handler = _ListHandler()
    uvicorn_logger = logging.getLogger("uvicorn.error")
    uvicorn_logger.addHandler(log_handler)
    try:
        ws_url = dash_thread_server.url.replace("http", "ws", 1) + "/_dash-ws-callback"
        client = websocket.create_connection(ws_url, origin=dash_thread_server.url)
        client.send(json.dumps({"type": "heartbeat"}))
        client.send(json.dumps({"type": "heartbeat"}))
        client.close()

        deadline = time.time() + 5
        while len(handled) < 2 and time.time() < deadline:
            time.sleep(0.05)
        time.sleep(0.5)
    finally:
        uvicorn_logger.removeHandler(log_handler)

    assert len(handled) == 2
    assert [r.getMessage() for r in log_handler.records] == []
