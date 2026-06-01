"""
WebSocket set_props with Patch object test.

Verifies that set_props works with Patch objects in websocket callbacks.
"""

from dash import Dash, html, Input, Output, set_props, Patch
from dash.exceptions import PreventUpdate


def test_ws037_set_props_with_patch(dash_duo):
    """Test set_props with Patch object in websocket callback."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Patch", id="btn"),
            html.Div("initial", id="output"),
            html.Div(id="result"),
        ]
    )

    @app.callback(
        Output("result", "children"), Input("btn", "n_clicks"), websocket=True
    )
    def patch_append(n):
        if not n:
            raise PreventUpdate

        p = Patch()
        p += f" + click {n}"

        set_props("output", {"children": p})
        return f"Appended {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#output", "initial + click 1", timeout=10)

    assert dash_duo.get_logs() == []
