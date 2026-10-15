"""The app the streaming load test serves.

One streaming callback that yields ``FRAMES`` frames, ``INTERVAL`` seconds
apart. Each frame carries the server's ``time.time()`` so the client can
measure delivery latency (clients run on the same machine, so the clocks
agree).

Configured from the environment so gunicorn, uvicorn and hypercorn can all
import it: ``LOAD_BACKEND`` (flask, fastapi, quart), ``LOAD_FRAMES``,
``LOAD_INTERVAL``. ``LOAD_REDIS_URL`` switches shared storage to Redis (needed
across workers), and ``LOAD_SECRET`` gives every worker the same signing secret
so they verify each other's stream tokens.
"""
import asyncio
import os
import time

from dash import Dash, Input, Output, LocalSharedStorage, RedisSharedStorage, html

BACKEND = os.environ.get("LOAD_BACKEND", "flask")
FRAMES = int(os.environ.get("LOAD_FRAMES", "20"))
INTERVAL = float(os.environ.get("LOAD_INTERVAL", "0.1"))

REDIS_URL = os.environ.get("LOAD_REDIS_URL")

app = Dash(
    __name__,
    backend=BACKEND,
    shared_storage=RedisSharedStorage(url=REDIS_URL)
    if REDIS_URL
    else LocalSharedStorage,
)
app.server.secret_key = os.environ.get("LOAD_SECRET", "load-test")
app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), html.Div(id="out")])


@app.callback(Output("out", "children"), Input("btn", "n_clicks"))
async def stream(n):
    if not n:
        return
    for _ in range(FRAMES):
        yield f"{time.time():.6f}"
        await asyncio.sleep(INTERVAL)


server = app.server
