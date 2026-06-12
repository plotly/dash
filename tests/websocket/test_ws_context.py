"""Unit tests for WebSocket callback context creation.

These tests verify that request metadata captured from the WebSocket
handshake (cookies, headers, etc.) is propagated onto the callback
context. This is required so authentication helpers that read
``callback_context.cookies``/``headers`` (such as
``dash_enterprise_auth.get_user_data``) work inside WebSocket callbacks.
"""

from dash.backends.ws import create_ws_context


def test_create_ws_context_propagates_request_context():
    """Request metadata should be copied onto the callback context."""
    payload = {
        "inputs": [],
        "state": [],
        "outputs": [],
        "changedPropIds": [],
    }
    request_context = {
        "cookies": {"kcIdToken": "token-value"},
        "headers": {"Plotly-User-Data": "{}"},
        "args": {"foo": "bar"},
        "path": "/_dash-ws-callback",
        "remote": "10.0.0.1",
        "origin": "https://example.com",
    }

    g = create_ws_context(payload, response_adapter=None, websocket_callback=None, request_context=request_context)

    assert g.cookies == {"kcIdToken": "token-value"}
    assert g.headers == {"Plotly-User-Data": "{}"}
    assert g.args == {"foo": "bar"}
    assert g.path == "/_dash-ws-callback"
    assert g.remote == "10.0.0.1"
    assert g.origin == "https://example.com"


def test_create_ws_context_defaults_without_request_context():
    """Context should expose empty defaults when no request context is given."""
    payload = {
        "inputs": [],
        "state": [],
        "outputs": [],
        "changedPropIds": [],
    }

    g = create_ws_context(payload, response_adapter=None, websocket_callback=None)

    assert g.cookies == {}
    assert g.headers == {}
    assert g.args == ""
    assert g.path == ""
    assert g.remote == ""
    assert g.origin == ""
