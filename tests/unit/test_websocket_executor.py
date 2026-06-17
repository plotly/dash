"""Unit tests for the per-connection WebSocket callback thread pool.

These verify that each WebSocket connection gets its own ThreadPoolExecutor
(rather than a single shared, app-wide pool), so that long-lived
(session-persistent) callbacks on one connection cannot exhaust worker threads
shared with other connections, and that the per-connection size is configurable
via the ``websocket_max_workers`` argument to ``Dash``.
"""

from concurrent.futures import ThreadPoolExecutor

from dash import Dash


def test_websocket_max_workers_default():
    """websocket_max_workers defaults to 4."""
    app = Dash(__name__)
    assert app._websocket_max_workers == 4


def test_websocket_max_workers_custom():
    """websocket_max_workers is stored when provided."""
    app = Dash(__name__, websocket_max_workers=16)
    assert app._websocket_max_workers == 16


def test_create_callback_executor_is_per_connection():
    """Each call returns a fresh executor, not a cached shared one."""
    backend = Dash(__name__).backend

    ex1 = backend.create_callback_executor(4)
    ex2 = backend.create_callback_executor(4)
    try:
        assert isinstance(ex1, ThreadPoolExecutor)
        assert isinstance(ex2, ThreadPoolExecutor)
        # Distinct instances => one connection's pool can't starve another's.
        assert ex1 is not ex2
    finally:
        ex1.shutdown(wait=False)
        ex2.shutdown(wait=False)


def test_create_callback_executor_honors_max_workers():
    """max_workers is forwarded to the ThreadPoolExecutor."""
    backend = Dash(__name__).backend

    ex = backend.create_callback_executor(7)
    try:
        assert ex._max_workers == 7
    finally:
        ex.shutdown(wait=False)
