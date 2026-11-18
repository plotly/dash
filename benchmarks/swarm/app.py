"""The app a browser swarm loads.

One page, three things to click, each measured by the agents in the browser:

- ``#http-btn`` -> ``#http-out``: a plain callback over an HTTP POST.
- ``#ws-btn`` -> ``#ws-out``: the same callback over the websocket
  (``websocket=True``; FastAPI and Quart only).
- ``#stream-btn`` -> ``#stream-out``: a streaming callback, ``SWARM_FRAMES``
  frames ``SWARM_INTERVAL`` seconds apart, the last one ending in ``done``.

``SWARM_WORK_MS`` adds that much ``asyncio.sleep`` to the plain callbacks, like
a query. Serve it the way a deployment would, for example::

    SWARM_BACKEND=fastapi SWARM_REDIS_URL=redis://redis:6379/0 \\
        uvicorn benchmarks.swarm.app:server --host 0.0.0.0 --workers 4

``SWARM_REDIS_URL`` is needed for streaming with more than one worker or
instance, and ``SWARM_SECRET`` must be the same everywhere the app runs.
"""
import asyncio
import os

from dash import Dash, Input, Output, LocalSharedStorage, RedisSharedStorage, html

BACKEND = os.environ.get("SWARM_BACKEND", "fastapi")
REDIS_URL = os.environ.get("SWARM_REDIS_URL")
FRAMES = int(os.environ.get("SWARM_FRAMES", "20"))
INTERVAL = float(os.environ.get("SWARM_INTERVAL", "0.1"))
WORK = float(os.environ.get("SWARM_WORK_MS", "0")) / 1000
WS = BACKEND != "flask"

app = Dash(
    __name__,
    backend=BACKEND,
    shared_storage=RedisSharedStorage(url=REDIS_URL)
    if REDIS_URL
    else LocalSharedStorage,
)
app.server.secret_key = os.environ.get("SWARM_SECRET", "swarm")


def _section(name):
    return html.Div(
        [
            html.Button(name, id=f"{name}-btn", n_clicks=0),
            html.Div(id=f"{name}-out"),
        ]
    )


app.layout = html.Div(
    [_section("http"), _section("ws"), _section("stream"), html.Div(id="ready")]
)


@app.callback(
    Output("http-out", "children"),
    Input("http-btn", "n_clicks"),
    prevent_initial_call=True,
)
async def http_clicked(n):
    if WORK:
        await asyncio.sleep(WORK)
    return f"clicked {n}"


if WS:

    @app.callback(
        Output("ws-out", "children"),
        Input("ws-btn", "n_clicks"),
        prevent_initial_call=True,
        websocket=True,
    )
    async def ws_clicked(n):
        if WORK:
            await asyncio.sleep(WORK)
        return f"clicked {n}"


@app.callback(
    Output("stream-out", "children"),
    Input("stream-btn", "n_clicks"),
    prevent_initial_call=True,
)
async def stream(n):
    for i in range(FRAMES):
        yield f"{n}:{i}" + (" done" if i == FRAMES - 1 else "")
        if i < FRAMES - 1:
            await asyncio.sleep(INTERVAL)


server = app.server
