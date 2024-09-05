from dash import Dash, html, Input, Output, set_props


def test_cber001_error_handler(dash_duo):
    def global_callback_error_handler(err):
        set_props("output-global", {"children": f"global: {err}"})

    app = Dash(on_error=global_callback_error_handler)

    app.layout = [
        html.Button("start", id="start-local"),
        html.Button("start-global", id="start-global"),
        html.Div(id="output"),
        html.Div(id="output-global"),
        html.Div(id="error-message"),
    ]

    def on_callback_error(err):
        set_props("error-message", {"children": f"message: {err}"})
        return f"callback: {err}"

    @app.callback(
        Output("output", "children"),
        Input("start-local", "n_clicks"),
        on_error=on_callback_error,
        prevent_initial_call=True,
    )
    def on_start(_):
        raise Exception("local error")

    @app.callback(
        Output("output-global", "children"),
        Input("start-global", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_start_global(_):
        raise Exception("global error")

    dash_duo.start_server(app)
    dash_duo.find_element("#start-local").click()

    dash_duo.wait_for_text_to_equal("#output", "callback: local error")
    dash_duo.wait_for_text_to_equal("#error-message", "message: local error")

    dash_duo.find_element("#start-global").click()
    dash_duo.wait_for_text_to_equal("#output-global", "global: global error")
