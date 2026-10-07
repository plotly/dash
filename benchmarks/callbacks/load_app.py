"""The app the callback load test serves.

One button and one output: each click runs a callback that returns the
click count. ``LOAD_TRANSPORT`` picks how the renderer sends it: ``http`` (a
POST per callback) or ``ws`` (``websocket_callbacks=True``, one websocket per
browser). ``LOAD_KIND`` makes the callback a plain ``def`` (``sync``) or an
``async def``, and ``LOAD_WORK_MS`` adds that much work to each call: CPU for
a sync callback, ``asyncio.sleep`` for an async one, like a query.

Configured from the environment so gunicorn and uvicorn can import it:
``LOAD_BACKEND`` (flask, fastapi, quart) plus the above.
"""
import asyncio
import os
import time

from dash import Dash, Input, Output, html

BACKEND = os.environ.get("LOAD_BACKEND", "flask")
TRANSPORT = os.environ.get("LOAD_TRANSPORT", "http")
KIND = os.environ.get("LOAD_KIND", "sync")
WORK = float(os.environ.get("LOAD_WORK_MS", "0")) / 1000

app = Dash(__name__, backend=BACKEND, websocket_callbacks=TRANSPORT == "ws")
app.layout = html.Div([html.Button("go", id="btn", n_clicks=0), html.Div(id="out")])


def _burn(seconds):
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        pass


if KIND == "async":

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def clicked(n):
        if WORK:
            await asyncio.sleep(WORK)
        return f"clicked {n}"

else:

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def clicked(n):
        if WORK:
            _burn(WORK)
        return f"clicked {n}"


server = app.server
