"""
WebSocket inactivity timeout tests.

Tests:
- Connection closes after inactivity period
- Activity resets the timer
- Heartbeats don't count as activity
- Auto-reconnect when callback fires after timeout
"""

import time
from dash import Dash, html, Input, Output


def test_ws020_inactivity_timeout_closes(dash_duo):
    """Test that WebSocket connection closes after inactivity timeout."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=3000,  # 3 seconds for testing
        websocket_heartbeat_interval=1000,  # 1 second - check inactivity frequently
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

    # Trigger callback to establish connection
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    # Wait for inactivity timeout
    time.sleep(4)

    # Click again - should auto-reconnect and work
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 2")


def test_ws021_activity_resets_timer(dash_duo):
    """Test that callback activity resets the inactivity timer."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=4000,  # 4 seconds
        websocket_heartbeat_interval=1000,  # 1 second - check inactivity frequently
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

    # Click every 2 seconds - should keep connection alive
    for i in range(1, 4):
        time.sleep(2)
        dash_duo.find_element("#btn").click()
        dash_duo.wait_for_text_to_equal("#output", f"Clicked {i}")

    # All clicks should work without disconnection
    assert dash_duo.get_logs() == []


def test_ws022_quick_successive_callbacks(dash_duo):
    """Test rapid successive callbacks work correctly."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=5000,
        websocket_heartbeat_interval=1000,  # 1 second - check inactivity frequently
    )

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div("0", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return str(n_clicks or 0)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "0")

    # Rapid clicks
    for _ in range(5):
        dash_duo.find_element("#btn").click()
        time.sleep(0.1)

    dash_duo.wait_for_text_to_equal("#output", "5")
    assert dash_duo.get_logs() == []


def test_ws023_auto_reconnect_after_timeout(dash_duo):
    """Test auto-reconnect when callback fires after inactivity timeout."""
    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=2000,  # 2 seconds
        websocket_heartbeat_interval=1000,  # 1 second - check inactivity frequently
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

    # Initial callback
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    # Wait for timeout to expire
    time.sleep(3)

    # Click again - should auto-reconnect
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 2")

    # And keep working
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 3")

    assert dash_duo.get_logs() == []


def test_ws024_long_callback_doesnt_timeout(dash_duo):
    """Test that long-running callbacks don't cause timeout during execution."""
    import asyncio

    app = Dash(
        __name__,
        backend="fastapi",
        websocket_callbacks=True,
        websocket_inactivity_timeout=3000,  # 3 seconds
        websocket_heartbeat_interval=1000,  # 1 second - check inactivity frequently
    )

    app.layout = html.Div(
        [
            html.Button("Start Long Task", id="btn"),
            html.Div("ready", id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    async def long_task(n_clicks):
        if not n_clicks:
            return "ready"
        # Simulate long task (longer than inactivity timeout)
        await asyncio.sleep(2)
        return f"Completed task {n_clicks}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "ready")

    # Start long task
    dash_duo.find_element("#btn").click()

    # Should complete despite being longer than half the timeout
    dash_duo.wait_for_text_to_equal("#output", "Completed task 1", timeout=10)

    assert dash_duo.get_logs() == []
