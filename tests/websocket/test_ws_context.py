"""Unit tests for WebSocket callback context creation.

These tests verify that request metadata captured from the WebSocket
handshake (cookies, headers, etc.) is propagated onto the callback
context. This is required so authentication helpers that read
``callback_context.cookies``/``headers`` (such as
``dash_enterprise_auth.get_user_data``) work inside WebSocket callbacks.
"""

from types import SimpleNamespace

import pytest

from dash.backends.ws import create_ws_context


def test_create_ws_context_propagates_request_context():
    """Request metadata from the adapter should be copied onto the context."""
    payload = {
        "inputs": [],
        "state": [],
        "outputs": [],
        "changedPropIds": [],
    }
    request_adapter = SimpleNamespace(
        cookies={"kcIdToken": "token-value"},
        headers={"Plotly-User-Data": "{}"},
        args={"foo": "bar"},
        full_path="/_dash-ws-callback",
        remote_addr="10.0.0.1",
        origin="https://example.com",
    )

    g = create_ws_context(
        payload,
        response_adapter=None,
        websocket_callback=None,
        request_adapter=request_adapter,
    )

    assert g.cookies == {"kcIdToken": "token-value"}
    assert g.headers == {"Plotly-User-Data": "{}"}
    assert g.args == {"foo": "bar"}
    assert g.path == "/_dash-ws-callback"
    assert g.remote == "10.0.0.1"
    assert g.origin == "https://example.com"


def test_create_ws_context_defaults_without_request_adapter():
    """Context should expose empty defaults when no request adapter is given."""
    payload = {
        "inputs": [],
        "state": [],
        "outputs": [],
        "changedPropIds": [],
    }

    g = create_ws_context(payload, response_adapter=None, websocket_callback=None)

    assert g.cookies == {}
    assert g.headers == {}
    assert g.args == {}
    assert g.path == ""
    assert g.remote == ""
    assert g.origin == ""


def test_run_executor_activates_request_across_thread_boundary():
    """Request activation must populate context inside the executor thread.

    WebSocket callbacks run in a ``ThreadPoolExecutor`` and ContextVars do not
    propagate into those threads, so the refactor activates the handshake
    request (via FastAPI's ``set_current_request``) *inside* the worker thread.
    This guards that seam: a request activated in the worker thread is visible
    to ``FastAPIRequestAdapter`` and gets copied onto the callback context.
    """
    pytest.importorskip("fastapi")
    from concurrent.futures import ThreadPoolExecutor
    from contextlib import contextmanager

    from dash.backends._fastapi import (
        FastAPIRequestAdapter,
        reset_current_request,
        set_current_request,
    )

    # Minimal stand-in for a Starlette ``WebSocket`` handshake connection: it
    # only needs the attributes the request adapter reads.
    handshake = SimpleNamespace(
        cookies={"kcIdToken": "token-value"},
        headers={"origin": "https://example.com"},
        query_params={"foo": "bar"},
        url="http://testserver/_dash-ws-callback",
        client=SimpleNamespace(host="10.0.0.1"),
    )

    @contextmanager
    def activate_request():
        token = set_current_request(handshake)
        try:
            yield FastAPIRequestAdapter()
        finally:
            reset_current_request(token)

    payload = {
        "inputs": [],
        "state": [],
        "outputs": [],
        "changedPropIds": [],
    }

    def worker():
        with activate_request() as request_adapter:
            return create_ws_context(
                payload,
                response_adapter=None,
                websocket_callback=None,
                request_adapter=request_adapter,
            )

    with ThreadPoolExecutor(max_workers=1) as executor:
        g = executor.submit(worker).result()

    assert g.cookies == {"kcIdToken": "token-value"}
    assert g.headers == {"origin": "https://example.com"}
    assert g.args == {"foo": "bar"}
    assert g.path == "http://testserver/_dash-ws-callback"
    assert g.remote == "10.0.0.1"
    assert g.origin == "https://example.com"
