import time
from dash import Dash, Input, Output, html

import dash_test_components as dt


def test_rdraw001_redraw(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(
                dt.DrawCounter(id="counter"),
                id="redrawer",
            ),
            html.Button("redraw", id="redraw"),
        ]
    )

    @app.callback(
        Output("redrawer", "children"),
        Input("redraw", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(_):
        return dt.DrawCounter(id="counter")

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#counter", "1")
    dash_duo.find_element("#redraw").click()
    dash_duo.wait_for_text_to_equal("#counter", "2")
    time.sleep(1)
    dash_duo.wait_for_text_to_equal("#counter", "2")
