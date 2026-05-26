"""
WebSocket reconnection and disconnect handling tests.

Tests:
- Callback continuity after WebSocket reconnection
- Registry tracks active callbacks correctly
- Disconnect handling doesn't cause error spam
- Long-running callbacks survive reconnection
"""

import asyncio
import time
import threading

from dash import Dash, html, Input, Output, set_props
from dash.backends._ws_registry import ActiveCallbackRegistry


class TestActiveCallbackRegistry:
    """Unit tests for the ActiveCallbackRegistry class."""

    def test_registry_adopt_creates_entry(self):
        """Test that adopt_connection creates a new registry entry."""
        registry = ActiveCallbackRegistry()

        # Mock queue-like object
        class MockQueue:
            def __init__(self):
                self.sync_q = None

        outbound_queue = MockQueue()
        pending_get_props = {}
        shutdown_event = threading.Event()

        registry.adopt_connection(
            "renderer1", outbound_queue, pending_get_props, shutdown_event
        )

        assert registry.get_queue("renderer1") == outbound_queue
        assert registry.get_pending_get_props("renderer1") == pending_get_props
        assert not registry.is_shutdown("renderer1")

    def test_registry_callback_lifecycle(self):
        """Test register/unregister callback with cleanup."""
        registry = ActiveCallbackRegistry()

        class MockQueue:
            def __init__(self):
                self.sync_q = None

        outbound_queue = MockQueue()
        shutdown_event = threading.Event()

        registry.adopt_connection("renderer1", outbound_queue, {}, shutdown_event)

        # Register callback
        registry.register_callback("renderer1")
        assert not registry.is_shutdown("renderer1")

        # Unregister - should clean up entry since count becomes 0
        registry.unregister_callback("renderer1")
        assert registry.is_shutdown("renderer1")  # Returns True when not found

    def test_registry_multiple_callbacks(self):
        """Test that multiple callbacks keep entry alive."""
        registry = ActiveCallbackRegistry()

        class MockQueue:
            def __init__(self):
                self.sync_q = None

        outbound_queue = MockQueue()
        shutdown_event = threading.Event()

        registry.adopt_connection("renderer1", outbound_queue, {}, shutdown_event)

        # Register two callbacks
        registry.register_callback("renderer1")
        registry.register_callback("renderer1")

        # Unregister one - entry should still exist
        registry.unregister_callback("renderer1")
        assert not registry.is_shutdown("renderer1")

        # Unregister second - now should be cleaned up
        registry.unregister_callback("renderer1")
        assert registry.is_shutdown("renderer1")

    def test_registry_adopt_after_cleanup(self):
        """Test that adopt_connection works after cleanup."""
        registry = ActiveCallbackRegistry()

        class MockQueue:
            def __init__(self):
                self.sync_q = None

        outbound_queue = MockQueue()
        shutdown_event = threading.Event()

        # First connection
        registry.adopt_connection("renderer1", outbound_queue, {}, shutdown_event)
        registry.register_callback("renderer1")
        registry.unregister_callback("renderer1")  # Cleans up

        # Re-adopt after cleanup
        registry.adopt_connection("renderer1", outbound_queue, {}, shutdown_event)
        assert not registry.is_shutdown("renderer1")

    def test_registry_adopt_updates_existing(self):
        """Test that adopt_connection updates queues for existing entry."""
        registry = ActiveCallbackRegistry()

        class MockQueue:
            def __init__(self, name):
                self.name = name
                self.sync_q = None

        old_queue = MockQueue("old")
        new_queue = MockQueue("new")
        old_shutdown = threading.Event()
        new_shutdown = threading.Event()

        registry.adopt_connection("renderer1", old_queue, {}, old_shutdown)
        registry.register_callback("renderer1")  # Keep entry alive

        assert registry.get_queue("renderer1").name == "old"

        # Simulate reconnection
        registry.adopt_connection("renderer1", new_queue, {}, new_shutdown)

        assert registry.get_queue("renderer1").name == "new"

    def test_registry_shutdown_event_respected(self):
        """Test that shutdown event is checked correctly."""
        registry = ActiveCallbackRegistry()

        class MockQueue:
            def __init__(self):
                self.sync_q = None

        outbound_queue = MockQueue()
        shutdown_event = threading.Event()

        registry.adopt_connection("renderer1", outbound_queue, {}, shutdown_event)

        assert not registry.is_shutdown("renderer1")

        shutdown_event.set()

        assert registry.is_shutdown("renderer1")

    def test_registry_unknown_renderer_is_shutdown(self):
        """Test that unknown renderer IDs report as shutdown."""
        registry = ActiveCallbackRegistry()

        assert registry.is_shutdown("unknown_renderer")
        assert registry.get_queue("unknown_renderer") is None
        assert registry.get_pending_get_props("unknown_renderer") is None


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


def test_ws031_rapid_callbacks_registry_handling(dash_duo):
    """Test that rapid callbacks are handled correctly by registry."""
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


def test_ws035_callback_survives_inactivity_timeout(dash_duo):
    """Test that long callback completes even when inactivity timeout triggers mid-execution.

    This is the key test for Issue #3788: when a callback runs longer than the
    inactivity timeout without sending updates, the WebSocket disconnects and
    reconnects. The callback should still complete and send its result via the
    new connection.
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
            html.Div("ready", id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def silent_long_task(n_clicks):
        # Wait longer than inactivity timeout WITHOUT sending any updates
        # This will trigger WebSocket disconnect/reconnect mid-callback
        await asyncio.sleep(5)
        return f"completed:{n_clicks}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "ready")

    # Start the long task
    dash_duo.find_element("#btn").click()

    # Should complete despite inactivity timeout triggering during execution
    dash_duo.wait_for_text_to_equal("#output", "completed:1", timeout=15)

    # Verify subsequent callbacks also work
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "completed:2", timeout=15)

    assert dash_duo.get_logs() == []


def test_ws036_set_props_after_reconnect(dash_duo):
    """Test that set_props works after WebSocket reconnects mid-callback.

    This tests the registry's ability to adopt new queues so that
    set_props calls use the new connection after reconnection.
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
    async def task_with_late_set_props(n_clicks):
        set_props("status", {"children": "started"})
        set_props("progress", {"children": "10"})

        # Wait long enough for inactivity timeout to trigger
        await asyncio.sleep(5)

        # These set_props calls happen AFTER reconnection
        # They should still work via the adopted queue
        set_props("progress", {"children": "100"})

        return "done"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#status", "ready")

    dash_duo.find_element("#btn").click()

    # Should see initial updates
    dash_duo.wait_for_text_to_equal("#status", "started", timeout=5)
    dash_duo.wait_for_text_to_equal("#progress", "10", timeout=5)

    # Should see final update after reconnection
    dash_duo.wait_for_text_to_equal("#progress", "100", timeout=15)
    dash_duo.wait_for_text_to_equal("#status", "done", timeout=5)

    assert dash_duo.get_logs() == []
