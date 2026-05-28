"""
WebSocket reconnection and disconnect handling tests.

Tests:
- Callback continuity after WebSocket reconnection
- Disconnect handling doesn't cause error spam
- Long-running callbacks with is_shutdown check
"""

import asyncio
import time

from dash import Dash, html, Input, Output, set_props, ctx
from dash.exceptions import PreventUpdate


def test_ws030_multiple_callbacks_same_connection(dash_duo):
    """Test multiple sequential callbacks on the same WebSocket connection."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn", n_clicks=0),
            html.Div("0", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return str(n_clicks or 0)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "0")

    # Multiple clicks - each should work via the same connection
    for i in range(1, 6):
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#output", str(i))

    assert dash_duo.get_logs() == []


def test_ws031_rapid_callbacks(dash_duo):
    """Test that rapid callbacks are handled correctly."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Rapid Click", id="btn", n_clicks=0),
            html.Div("0", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return str(n_clicks or 0)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "0")

    # Rapid clicks without waiting
    for _ in range(10):
        dash_duo.find_element("#btn").click()
        time.sleep(0.05)  # 50ms between clicks

    # Should eventually reach 10
    dash_duo.wait_for_text_to_equal("#output", "10", timeout=10)

    assert dash_duo.get_logs() == []


def test_ws032_long_callback_with_set_props(dash_duo):
    """Test long-running callback with intermediate set_props updates."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div("ready", id="status"),
            html.Div("0", id="progress"),
        ]
    )

    @app.callback(
        Output("status", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def long_task(n_clicks):
        set_props("status", {"children": "running"})

        # Simulate progress updates
        for i in range(1, 6):
            set_props("progress", {"children": str(i * 20)})
            await asyncio.sleep(0.1)

        return "done"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#status", "ready")

    dash_duo.find_element("#btn").click()

    # Should see intermediate updates
    dash_duo.wait_for_text_to_equal("#status", "done", timeout=10)
    dash_duo.wait_for_text_to_equal("#progress", "100")

    assert dash_duo.get_logs() == []


def test_ws033_callback_after_reconnect(dash_duo):
    """Test that callbacks work after WebSocket reconnection."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=2000,  # 2 seconds
    )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn", n_clicks=0),
            html.Div("0", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return str(n_clicks or 0)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "0")

    # First click
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "1")

    # Wait for connection to timeout
    time.sleep(3)

    # Click after reconnection - should still work
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "2")

    # Multiple clicks after reconnection
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "3")

    assert dash_duo.get_logs() == []


def test_ws034_concurrent_callbacks(dash_duo):
    """Test multiple concurrent callbacks from different inputs."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Button A", id="btn-a", n_clicks=0),
            html.Button("Button B", id="btn-b", n_clicks=0),
            html.Div("a:0", id="output-a"),
            html.Div("b:0", id="output-b"),
        ]
    )

    @app.callback(Output("output-a", "children"), Input("btn-a", "n_clicks"))
    async def on_click_a(n_clicks):
        await asyncio.sleep(0.1)  # Small delay to ensure overlap
        return f"a:{n_clicks or 0}"

    @app.callback(Output("output-b", "children"), Input("btn-b", "n_clicks"))
    async def on_click_b(n_clicks):
        await asyncio.sleep(0.1)
        return f"b:{n_clicks or 0}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output-a", "a:0")
    dash_duo.wait_for_text_to_equal("#output-b", "b:0")

    # Click both buttons rapidly
    dash_duo.find_element("#btn-a").click()
    dash_duo.find_element("#btn-b").click()

    dash_duo.wait_for_text_to_equal("#output-a", "a:1")
    dash_duo.wait_for_text_to_equal("#output-b", "b:1")

    # More concurrent clicks
    dash_duo.find_element("#btn-a").click()
    dash_duo.find_element("#btn-b").click()
    dash_duo.find_element("#btn-a").click()

    dash_duo.wait_for_text_to_equal("#output-a", "a:3")
    dash_duo.wait_for_text_to_equal("#output-b", "b:2")

    assert dash_duo.get_logs() == []


def test_ws035_long_callback_with_shutdown_check(dash_duo):
    """Test long-running callback that properly checks is_shutdown.

    Long-running callbacks should check ws.is_shutdown in their loops to
    detect disconnections and exit gracefully. This prevents wasted server
    resources when the client disconnects.
    """
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=2000,  # 2 seconds
    )

    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div("ready", id="status"),
            html.Div("0", id="progress"),
        ]
    )

    @app.callback(
        Output("status", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def long_task_with_shutdown_check(n_clicks):
        ws = ctx.websocket
        set_props("status", {"children": "running"})

        # Properly check is_shutdown in the loop
        for i in range(1, 11):
            if ws and ws.is_shutdown:
                # Exit gracefully on disconnect
                raise PreventUpdate
            set_props("progress", {"children": str(i * 10)})
            await asyncio.sleep(0.2)

        return "done"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#status", "ready")

    dash_duo.find_element("#btn").click()

    # Should see progress updates and complete
    dash_duo.wait_for_text_to_equal("#status", "done", timeout=10)
    dash_duo.wait_for_text_to_equal("#progress", "100")

    assert dash_duo.get_logs() == []
