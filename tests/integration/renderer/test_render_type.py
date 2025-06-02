from dash import Dash, Input, Output, html
import json

import dash_test_components as dt


def test_rtype001_rendertype(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(
                dt.RenderType(id="render_test"),
                id="container",
            ),
            html.Button("redraw", id="redraw"),
            html.Button("update render", id="update_render"),
            html.Button("clientside", id="clientside_render"),
            html.Div(id="render_output"),
        ]
    )

    app.clientside_callback(
        """(n) => {
            dash_clientside.set_props('render_test', {n_clicks: 20})
        }""",
        Input("clientside_render", "n_clicks"),
    )

    @app.callback(
        Output("container", "children"),
        Input("redraw", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(_):
        return dt.RenderType(id="render_test")

    @app.callback(
        Output("render_test", "n_clicks"),
        Input("update_render", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_render(_):
        return 0

    @app.callback(Output("render_output", "children"), Input("render_test", "n_clicks"))
    def display_clicks(n):
        return json.dumps(n)

    dash_duo.start_server(app)

    render_type = "#render_test > span"
    render_output = "#render_output"
    dash_duo.wait_for_text_to_equal(render_type, "parent")
    dash_duo.find_element("#update_render").click()
    dash_duo.wait_for_text_to_equal(render_type, "callback")
    dash_duo.wait_for_text_to_equal(render_output, "0")
    dash_duo.find_element("#clientside_render").click()
    dash_duo.wait_for_text_to_equal(render_type, "clientsideApi")
    dash_duo.wait_for_text_to_equal(render_output, "20")
    dash_duo.find_element("#render_test > button").click()
    dash_duo.wait_for_text_to_equal(render_type, "internal")
    dash_duo.wait_for_text_to_equal(render_output, "21")
    dash_duo.find_element("#redraw").click()
    dash_duo.wait_for_text_to_equal(render_type, "parent")
    dash_duo.wait_for_text_to_equal(render_output, "null")
