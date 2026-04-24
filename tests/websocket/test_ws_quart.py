"""
Quart WebSocket callback tests.

Tests the Quart backend websocket implementation which mirrors the FastAPI backend.
"""

from dash import Dash, html, dcc, Input, Output, State, ctx


def test_wsq001_per_callback_websocket_quart(dash_duo):
    """Test single callback with websocket=True on Quart backend."""
    app = Dash(__name__, backend="quart")

    app.layout = html.Div(
        [
            html.H1("Per-Callback WebSocket Test (Quart)"),
            dcc.Input(id="ws-input", type="text", placeholder="Type here..."),
            html.Div(id="ws-output"),
        ]
    )

    @app.callback(
        Output("ws-output", "children"), Input("ws-input", "value"), websocket=True
    )
    def ws_callback(value):
        return f"WS: {value or ''}"

    dash_duo.start_server(app)

    # Test initial state (trailing space is trimmed by HTML rendering)
    dash_duo.wait_for_text_to_equal("#ws-output", "WS:")

    # Type into the input and verify callback executes
    input_elem = dash_duo.find_element("#ws-input")
    input_elem.send_keys("hello")

    dash_duo.wait_for_text_to_equal("#ws-output", "WS: hello")
    assert dash_duo.get_logs() == []


def test_wsq002_global_websocket_callbacks_quart(dash_duo):
    """Test global websocket_callbacks=True enables WebSocket for all callbacks on Quart."""
    app = Dash(
        __name__,
        backend="quart",
        websocket_callbacks=True,
    )

    app.layout = html.Div(
        [
            html.Button("Click me", id="btn", n_clicks=0),
            html.Div(id="output"),
            dcc.Input(id="input", type="text"),
            html.Div(id="input-output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def on_click(n_clicks):
        return f"Clicked {n_clicks} times"

    @app.callback(Output("input-output", "children"), Input("input", "value"))
    def on_input(value):
        return f"Input: {value or ''}"

    dash_duo.start_server(app)

    # Test button callback
    dash_duo.wait_for_text_to_equal("#output", "Clicked 0 times")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1 times")

    # Test input callback
    dash_duo.find_element("#input").send_keys("test")
    dash_duo.wait_for_text_to_equal("#input-output", "Input: test")

    assert dash_duo.get_logs() == []


def test_wsq003_mixed_http_and_websocket_quart(dash_duo):
    """Test mixing WebSocket and HTTP callbacks in the same app on Quart."""
    app = Dash(__name__, backend="quart")

    app.layout = html.Div(
        [
            # WebSocket callback section
            html.Div(
                [
                    dcc.Input(id="ws-input", type="text"),
                    html.Div(id="ws-output"),
                ]
            ),
            # HTTP callback section (default)
            html.Div(
                [
                    dcc.Input(id="http-input", type="text"),
                    html.Div(id="http-output"),
                ]
            ),
        ]
    )

    @app.callback(
        Output("ws-output", "children"), Input("ws-input", "value"), websocket=True
    )
    def ws_callback(value):
        return f"[WebSocket] {value or ''}"

    @app.callback(Output("http-output", "children"), Input("http-input", "value"))
    def http_callback(value):
        return f"[HTTP] {value or ''}"

    dash_duo.start_server(app)

    # Test WebSocket callback
    dash_duo.find_element("#ws-input").send_keys("ws-test")
    dash_duo.wait_for_text_to_equal("#ws-output", "[WebSocket] ws-test")

    # Test HTTP callback
    dash_duo.find_element("#http-input").send_keys("http-test")
    dash_duo.wait_for_text_to_equal("#http-output", "[HTTP] http-test")

    assert dash_duo.get_logs() == []


def test_wsq004_websocket_with_state_quart(dash_duo):
    """Test WebSocket callback with State inputs on Quart."""
    app = Dash(__name__, backend="quart", websocket_callbacks=True)

    app.layout = html.Div(
        [
            dcc.Input(id="state-input", type="text", value="initial"),
            html.Button("Submit", id="btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("btn", "n_clicks"),
        State("state-input", "value"),
    )
    def on_click(n_clicks, state_value):
        if not n_clicks:
            return "Click to submit"
        return f"Submitted: {state_value}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Click to submit")

    # Update state input
    state_input = dash_duo.find_element("#state-input")
    dash_duo.clear_input(state_input)
    state_input.send_keys("new value")

    # Click button to trigger callback
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "Submitted: new value")

    assert dash_duo.get_logs() == []


def test_wsq005_websocket_context_available_quart(dash_duo):
    """Test that WebSocket context is available in WebSocket callbacks on Quart."""
    app = Dash(__name__, backend="quart", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Check context", id="btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("btn", "n_clicks"))
    def check_context(n_clicks):
        if not n_clicks:
            return "Click to check"
        ws = ctx.get_websocket
        if ws is not None:
            return "WebSocket context available"
        return "No WebSocket context"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output", "Click to check")
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output", "WebSocket context available")

    assert dash_duo.get_logs() == []


def test_wsq006_websocket_multiple_outputs_quart(dash_duo):
    """Test WebSocket callback with multiple outputs on Quart."""
    app = Dash(__name__, backend="quart", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update", id="btn"),
            html.Div(id="output1"),
            html.Div(id="output2"),
            html.Div(id="output3"),
        ]
    )

    @app.callback(
        Output("output1", "children"),
        Output("output2", "children"),
        Output("output3", "children"),
        Input("btn", "n_clicks"),
    )
    def multi_output(n_clicks):
        n = n_clicks or 0
        return f"First: {n}", f"Second: {n * 2}", f"Third: {n * 3}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#output1", "First: 0")
    dash_duo.wait_for_text_to_equal("#output2", "Second: 0")
    dash_duo.wait_for_text_to_equal("#output3", "Third: 0")

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#output1", "First: 1")
    dash_duo.wait_for_text_to_equal("#output2", "Second: 2")
    dash_duo.wait_for_text_to_equal("#output3", "Third: 3")

    assert dash_duo.get_logs() == []
