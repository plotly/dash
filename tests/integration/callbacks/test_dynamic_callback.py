from dash import html, Dash, Input, Output


def test_dync001_dynamic_callback(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(id="output"),
            html.Button("create", id="create"),
            html.Div("initial", id="output-2"),
            html.Button("dynamic", id="dynamic"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("create", "n_clicks"),
        _allow_dynamic_callbacks=True,
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        @app.callback(
            Output("output-2", "children"),
            Input("dynamic", "n_clicks"),
            prevent_initial_call=True,
        )
        def on_click2(n_clicks2):
            return f"Dynamic clicks {n_clicks2}"

        return f"creator {n_clicks}"

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#create").click()
    dash_duo.wait_for_text_to_equal("#output", "creator 1")

    dash_duo.wait_for_element("#dynamic").click()
    dash_duo.wait_for_text_to_equal("#output-2", "Dynamic clicks 1")
