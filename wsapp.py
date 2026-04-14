"""
Test app for WebSocket-based callbacks.

Run with:
    python wsapp.py

Then open http://127.0.0.1:8050 in your browser.
"""

from dash import Dash, html, dcc, callback, Output, Input, ctx
import time

# Create app with FastAPI backend and WebSocket callbacks enabled
app = Dash(
    __name__,
    backend="fastapi",
    websocket_callbacks=True,
)

app.layout = html.Div([
    html.H1("WebSocket Callbacks Test"),

    html.Div([
        html.H3("Basic Callback Test"),
        html.Button("Click me", id="btn-1", n_clicks=0),
        html.Div(id="output-1"),
    ], style={"marginBottom": "20px", "padding": "10px", "border": "1px solid #ccc"}),

    html.Div([
        html.H3("Input Test"),
        dcc.Input(id="input-1", type="text", placeholder="Type something..."),
        html.Div(id="output-2"),
    ], style={"marginBottom": "20px", "padding": "10px", "border": "1px solid #ccc"}),

    html.Div([
        html.H3("Slider Test"),
        dcc.Slider(id="slider-1", min=0, max=100, value=50),
        html.Div(id="output-3"),
    ], style={"marginBottom": "20px", "padding": "10px", "border": "1px solid #ccc"}),

    html.Div([
        html.H3("set_props Test"),
        html.Button("Update via set_props", id="btn-2", n_clicks=0),
        html.Div(id="output-4", children="Initial content"),
        html.Div(id="output-5", children="Will be updated by set_props"),
    ], style={"marginBottom": "20px", "padding": "10px", "border": "1px solid #ccc"}),

    html.Div([
        html.H3("WebSocket Context Test"),
        html.Button("Check WebSocket Context", id="btn-3", n_clicks=0),
        html.Div(id="output-6"),
    ], style={"marginBottom": "20px", "padding": "10px", "border": "1px solid #ccc"}),

    html.Div(id="config-display", style={"marginTop": "20px", "fontSize": "12px", "color": "#666"}),
])


@callback(Output("output-1", "children"), Input("btn-1", "n_clicks"))
def update_output_1(n_clicks):
    return f"Button clicked {n_clicks} times"


@callback(Output("output-2", "children"), Input("input-1", "value"))
def update_output_2(value):
    return f"You typed: {value}"


@callback(Output("output-3", "children"), Input("slider-1", "value"))
def update_output_3(value):
    return f"Slider value: {value}"


@callback(Output("output-4", "children"), Input("btn-2", "n_clicks"))
def update_with_set_props(n_clicks):
    if n_clicks > 0:
        # Use set_props to update another component
        from dash._callback_context import set_props
        set_props("output-5", {"children": f"Updated via set_props at click {n_clicks}"})
    return f"set_props button clicked {n_clicks} times"


@callback(Output("output-6", "children"), Input("btn-3", "n_clicks"))
def check_websocket_context(n_clicks):
    if n_clicks > 0:
        ws = ctx.get_websocket
        if ws is not None:
            return f"WebSocket context is available! (click {n_clicks})"
        else:
            return f"WebSocket context is None (click {n_clicks}) - may be using HTTP fallback"
    return "Click to check WebSocket context"


@callback(Output("config-display", "children"), Input("btn-1", "n_clicks"))
def show_config(n_clicks):
    config = app._config()
    ws_config = config.get("websocket", {})
    if ws_config:
        return f"WebSocket enabled: {ws_config.get('enabled')}, URL: {ws_config.get('url')}"
    return "WebSocket not configured"


if __name__ == "__main__":
    print("Starting WebSocket callbacks test app...")
    print(f"WebSocket callbacks enabled: {app._websocket_callbacks}")
    print(f"Backend websocket capability: {app.backend.websocket_capability}")
    app.run(debug=True, port=8050)
