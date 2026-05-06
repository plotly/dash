"""
Test app for per-callback WebSocket support.

This app demonstrates using websocket=True on specific callbacks
without enabling global websocket_callbacks.
"""

from dash import Dash, html, dcc, callback, Input, Output, State

app = Dash(__name__, backend="fastapi")

app.layout = html.Div([
    html.H1("Per-Callback WebSocket Test"),

    html.Div([
        html.H3("WebSocket Callback"),
        dcc.Input(id="ws-input", type="text", placeholder="Type here..."),
        html.Div(id="ws-output", style={"padding": "10px", "background": "#e0ffe0"})
    ], style={"margin": "20px", "padding": "20px", "border": "1px solid #ccc"}),

    html.Div([
        html.H3("HTTP Callback (default)"),
        dcc.Input(id="http-input", type="text", placeholder="Type here..."),
        html.Div(id="http-output", style={"padding": "10px", "background": "#e0e0ff"})
    ], style={"margin": "20px", "padding": "20px", "border": "1px solid #ccc"}),

    html.Div([
        html.H3("WebSocket Counter"),
        html.Button("Increment", id="ws-btn"),
        html.Div(id="ws-counter", children="0", style={"padding": "10px", "background": "#ffe0e0"})
    ], style={"margin": "20px", "padding": "20px", "border": "1px solid #ccc"}),
])


@callback(
    Output("ws-output", "children"),
    Input("ws-input", "value"),
    websocket=True
)
def ws_callback(value):
    """This callback uses WebSocket."""
    return f"[WebSocket] You typed: {value or ''}"


@callback(
    Output("http-output", "children"),
    Input("http-input", "value")
)
def http_callback(value):
    """This callback uses HTTP (default)."""
    return f"[HTTP] You typed: {value or ''}"


@callback(
    Output("ws-counter", "children"),
    Input("ws-btn", "n_clicks"),
    State("ws-counter", "children"),
    websocket=True
)
def ws_counter(n_clicks, current):
    """WebSocket counter callback."""
    if n_clicks is None:
        return "0"
    return str(int(current or 0) + 1)


if __name__ == "__main__":
    app.run(debug=True)
