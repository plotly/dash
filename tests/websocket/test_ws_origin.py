"""
WebSocket origin validation tests.

Tests:
- Same-origin connections allowed by default
- Cross-origin rejected unless explicitly allowed
- websocket_allowed_origins configuration
"""

from dash import Dash, html, Input, Output


def test_ws040_same_origin_allowed(dash_duo):
    """Test that same-origin WebSocket connections work by default."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    # Same-origin request should work
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    assert dash_duo.get_logs() == []


def test_ws041_websocket_allowed_origins_empty(dash_duo):
    """Test with empty websocket_allowed_origins (only same-origin)."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_allowed_origins=[],  # Only same-origin
    )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    # Same-origin should still work
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    assert dash_duo.get_logs() == []


def test_ws042_websocket_allowed_origins_wildcard(dash_duo):
    """Test with wildcard in websocket_allowed_origins."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_allowed_origins=["*"],  # Allow all origins
    )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    assert dash_duo.get_logs() == []


def test_ws043_websocket_allowed_origins_specific(dash_duo):
    """Test with specific origins in websocket_allowed_origins."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_allowed_origins=["http://localhost:*", "http://127.0.0.1:*"],
    )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    # Should work since we're running on localhost
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    assert dash_duo.get_logs() == []


def test_ws044_origin_with_per_callback_websocket(dash_duo):
    """Test origin validation with per-callback websocket=True."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_allowed_origins=["http://localhost:*", "http://127.0.0.1:*"],
    )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div("initial", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"), Input("btn", "n_clicks"), websocket=True
    )
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    assert dash_duo.get_logs() == []
