"""
Regression tests for lazy WebSocket connection on the FastAPI/Quart backends.

The FastAPI/Quart backends always advertise WebSocket infrastructure in the
page config (they have ``websocket_capability = True``). A regression once made
the renderer open a socket on every page load just because that infra was
present, even for apps with no WebSocket callbacks at all.

These tests pin down the intended behavior. The ``websocket_connect`` hook only
fires when a socket is actually accepted, so a connection counter driven by that
hook is a precise, server-side observable for "did a socket open":

  - no WebSocket callbacks            -> socket never opens
  - only per-callback websocket=True  -> socket opens lazily, on first dispatch
  - global websocket_callbacks=True   -> socket opens eagerly, on page load
"""

import time

from dash import Dash, html, Input, Output, hooks
from dash.testing.wait import until


def _count_connections():
    """Register a websocket_connect hook and return its connection counter."""
    counter = {"value": 0}

    @hooks.websocket_connect()
    def _on_connect(websocket):  # pylint: disable=unused-argument
        counter["value"] += 1
        return True

    return counter


def test_ws030_no_ws_callbacks_never_connects(dash_duo, ws_hook_cleanup):
    """An app with only HTTP callbacks must never open a WebSocket.

    This is the regression: the socket used to open on load for any
    FastAPI app, regardless of whether a WebSocket callback existed.
    """
    connections = _count_connections()

    app = Dash(__name__, backend="fastapi")
    app.layout = html.Div(
        [
            html.Button("Click", id="btn", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    # Drive an HTTP round-trip so we know the app is fully booted.
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    # Give any (erroneous) eager connection time to land, then assert none did.
    time.sleep(1.5)
    assert connections["value"] == 0, "no socket should open without a ws callback"
    assert dash_duo.get_logs() == []


def test_ws031_per_callback_connects_lazily(dash_duo, ws_hook_cleanup):
    """A per-callback websocket=True must open the socket only on dispatch.

    With prevent_initial_call=True the callback does not run on load, so no
    socket should exist until the button is clicked.
    """
    connections = _count_connections()

    app = Dash(__name__, backend="fastapi")
    app.layout = html.Div(
        [
            html.Button("Click", id="btn", n_clicks=0),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("btn", "n_clicks"),
        websocket=True,
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        return f"Clicked {n_clicks}"

    dash_duo.start_server(app)

    # Page is up but the ws callback hasn't run yet -> no socket.
    dash_duo.wait_for_text_to_equal("#output", "initial")
    time.sleep(1.5)
    assert connections["value"] == 0, "socket must not open before first dispatch"

    # First dispatch of the ws callback opens the socket lazily.
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")
    until(
        lambda: connections["value"] >= 1,
        timeout=5,
        msg="socket should open on first websocket callback dispatch",
    )
    assert dash_duo.get_logs() == []


def test_ws032_global_ws_connects_eagerly(dash_duo, ws_hook_cleanup):
    """Global websocket_callbacks=True keeps opening the socket on load."""
    connections = _count_connections()

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)
    app.layout = html.Div(
        [
            html.Button("Click", id="btn", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    # No interaction required: the socket opens eagerly at page load.
    until(
        lambda: connections["value"] >= 1,
        timeout=5,
        msg="global websocket_callbacks should open the socket on load",
    )
    assert dash_duo.get_logs() == []
