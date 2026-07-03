"""Unit tests for the shared WebSocket callback thread pool.

These verify that a single app-wide ``ThreadPoolExecutor`` is shared across all
WebSocket connections. Only *sync* callbacks run on it -- async (incl.
session-persistent) callbacks run directly on the event loop -- so a fixed-size
shared pool bounds the total worker-thread count regardless of how many
connections are open. The pool size is configurable via the
``websocket_max_workers`` argument to ``Dash``.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from typing import cast

import janus

from dash import Dash, Input, Output
from dash.backends.ws import DashWebsocketCallback, run_callback_in_executor
from dash.types import CallbackExecutionBody


def test_websocket_max_workers_default():
    """websocket_max_workers defaults to 4."""
    app = Dash(__name__)
    assert app._websocket_max_workers == 4


def test_websocket_max_workers_custom():
    """websocket_max_workers is stored when provided."""
    app = Dash(__name__, websocket_max_workers=16)
    assert app._websocket_max_workers == 16


def test_get_callback_executor_is_shared():
    """Repeated calls return the same cached, app-wide executor."""
    backend = Dash(__name__).backend

    ex1 = backend.get_callback_executor(4)
    ex2 = backend.get_callback_executor(4)
    try:
        assert isinstance(ex1, ThreadPoolExecutor)
        # Same instance => total thread count is bounded across connections.
        assert ex1 is ex2
    finally:
        backend.shutdown_executor(wait=False)


def test_get_callback_executor_honors_max_workers():
    """max_workers is forwarded to the ThreadPoolExecutor."""
    backend = Dash(__name__).backend

    ex = backend.get_callback_executor(7)
    try:
        assert ex._max_workers == 7
    finally:
        backend.shutdown_executor(wait=False)


def test_shutdown_executor_allows_recreation():
    """After shutdown the next get_callback_executor call creates a fresh pool."""
    backend = Dash(__name__).backend

    ex1 = backend.get_callback_executor(4)
    backend.shutdown_executor(wait=False)
    ex2 = backend.get_callback_executor(4)
    try:
        assert ex1 is not ex2
    finally:
        backend.shutdown_executor(wait=False)


def test_run_callback_in_executor_propagates_contextvars():
    """Sync WS callbacks inherit ContextVars bound on the calling thread.

    Regression test for gh-3861: ``copy_context()`` must be captured in
    ``run_callback_in_executor`` (on the event-loop thread, where ASGI middleware
    binds per-request ContextVars) rather than inside the worker-thread ``execute``
    closure, which would only ever see default values.
    """
    myvar: ContextVar = ContextVar("myvar", default="DEFAULT")

    app = Dash(__name__)

    @app.callback(Output("out", "children"), Input("in", "value"), websocket=True)
    def cb(value):
        return f"{myvar.get()}:{value}"

    payload = cast(
        CallbackExecutionBody,
        {
            "output": "out.children",
            "outputs": {"id": "out", "property": "children"},
            "inputs": [{"id": "in", "property": "value", "value": "hi"}],
            "state": [],
            "changedPropIds": ["in.value"],
        },
    )

    executor = ThreadPoolExecutor(max_workers=2)

    async def run():
        # janus.Queue must be constructed with a running loop on Python < 3.10.
        outbound_queue: janus.Queue = janus.Queue()
        ws_cb = DashWebsocketCallback(
            {}, "rid", outbound_queue, threading.Event(), None
        )
        try:
            # Bind the ContextVar on this (calling/event-loop) thread, as
            # middleware would; run_callback_in_executor must snapshot it here.
            myvar.set("MIDDLEWARE_VALUE")
            future = run_callback_in_executor(
                executor, app, payload, ws_cb, app.backend.response_adapter()
            )
            return future.result(timeout=10)
        finally:
            outbound_queue.close()
            await outbound_queue.wait_closed()

    try:
        result = asyncio.run(run())
    finally:
        executor.shutdown(wait=False)

    assert result["status"] == "ok"
    # The worker thread would see the default without the calling-thread snapshot.
    assert result["data"]["response"]["out"]["children"] == "MIDDLEWARE_VALUE:hi"
