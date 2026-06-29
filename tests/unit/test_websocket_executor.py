"""Unit tests for the shared WebSocket callback thread pool.

These verify that a single app-wide ``ThreadPoolExecutor`` is shared across all
WebSocket connections. Only *sync* callbacks run on it -- async (incl.
session-persistent) callbacks run directly on the event loop -- so a fixed-size
shared pool bounds the total worker-thread count regardless of how many
connections are open. The pool size is configurable via the
``websocket_max_workers`` argument to ``Dash``.
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
