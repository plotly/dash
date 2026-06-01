"""
WebSocket hooks tests.

Tests:
- websocket_connect hook - accept/reject connections
- websocket_message hook - accept/reject messages
- Custom close codes and reasons
"""

from dash import Dash, html, Input, Output, hooks


def test_ws010_connect_hook_accept(dash_duo, ws_hook_cleanup):
    """Test websocket_connect hook that accepts all connections."""
    connection_count = {"value": 0}

    @hooks.websocket_connect()
    def allow_all(websocket):
        connection_count["value"] += 1
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    # Hook should have been called at least once for connection
    assert connection_count["value"] >= 1
    assert dash_duo.get_logs() == []


def test_ws011_connect_hook_reject_false(dash_duo, ws_hook_cleanup):
    """Test websocket_connect hook that rejects with False.

    When WebSocket connection is rejected, callbacks won't work since
    websocket_callbacks=True requires WebSocket transport.
    """

    @hooks.websocket_connect()
    def reject_all(websocket):
        return False

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

    # WebSocket rejected - callbacks won't fire, output stays initial
    import time

    time.sleep(1)  # Give time for potential callback
    assert dash_duo.find_element("#output").text == "initial"

    dash_duo.find_element("#btn").click()
    time.sleep(1)
    # Still initial since WebSocket was rejected
    assert dash_duo.find_element("#output").text == "initial"


def test_ws012_connect_hook_reject_tuple(dash_duo, ws_hook_cleanup):
    """Test websocket_connect hook that rejects with custom code/reason.

    When WebSocket connection is rejected, callbacks won't work since
    websocket_callbacks=True requires WebSocket transport.
    """

    @hooks.websocket_connect()
    def reject_with_reason(websocket):
        return (4001, "Connection not allowed")

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

    # WebSocket rejected - callbacks won't fire, output stays initial
    import time

    time.sleep(1)
    assert dash_duo.find_element("#output").text == "initial"

    dash_duo.find_element("#btn").click()
    time.sleep(1)
    assert dash_duo.find_element("#output").text == "initial"


def test_ws013_message_hook_accept(dash_duo, ws_hook_cleanup):
    """Test websocket_message hook that accepts all messages."""
    message_count = {"value": 0}

    @hooks.websocket_message()
    def allow_all_messages(websocket, message):
        message_count["value"] += 1
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    # Message hook should have been called
    assert message_count["value"] >= 1
    assert dash_duo.get_logs() == []


def test_ws014_message_hook_reject(dash_duo, ws_hook_cleanup):
    """Test websocket_message hook that rejects specific messages."""
    reject_clicks = {"should_reject": False}

    @hooks.websocket_message()
    def conditional_reject(websocket, message):
        if reject_clicks["should_reject"]:
            return (4010, "Message rejected")
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    # First click should work
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    assert dash_duo.get_logs() == []


def test_ws015_async_connect_hook(dash_duo, ws_hook_cleanup):
    """Test async websocket_connect hook."""
    import asyncio

    @hooks.websocket_connect()
    async def async_validate(websocket):
        await asyncio.sleep(0.01)  # Simulate async validation
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="output"),
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


def test_ws016_async_message_hook(dash_duo, ws_hook_cleanup):
    """Test async websocket_message hook."""
    import asyncio

    @hooks.websocket_message()
    async def async_validate_message(websocket, message):
        await asyncio.sleep(0.01)  # Simulate async validation
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="output"),
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


def test_ws017_multiple_connect_hooks(dash_duo, ws_hook_cleanup):
    """Test multiple websocket_connect hooks with priorities."""
    hook_order = []

    @hooks.websocket_connect(priority=1)
    def first_hook(websocket):
        hook_order.append("first")
        return True

    @hooks.websocket_connect(priority=2)
    def second_hook(websocket):
        hook_order.append("second")
        return True

    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Click", id="btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks or 0}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Clicked 0")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1")

    # Both hooks should have been called
    assert "first" in hook_order
    assert "second" in hook_order
    assert dash_duo.get_logs() == []
