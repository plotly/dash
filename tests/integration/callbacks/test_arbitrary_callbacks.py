from dash import Dash, Input, Output, html, set_props, register_page


def test_arb001_global_set_props(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            html.Div(id="output"),
            html.Div(id="secondary-output"),
            html.Button("click", id="clicker"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("clicker", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        set_props("secondary-output", {"children": "secondary"})
        return f"Clicked {n_clicks} times"

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#clicker").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1 times")
    dash_duo.wait_for_text_to_equal("#secondary-output", "secondary")


def test_arb002_no_output_callbacks(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Div(id="secondary-output"),
            html.Button("no-output", id="no-output"),
            html.Button("no-output2", id="no-output2"),
        ]
    )

    @app.callback(
        Input("no-output", "n_clicks"),
        prevent_initial_call=True,
    )
    def no_output(_):
        set_props("secondary-output", {"children": "no-output"})

    @app.callback(
        Input("no-output2", "n_clicks"),
        prevent_initial_call=True,
    )
    def no_output(_):
        set_props("secondary-output", {"children": "no-output2"})

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#no-output").click()
    dash_duo.wait_for_text_to_equal("#secondary-output", "no-output")

    dash_duo.wait_for_element("#no-output2").click()
    dash_duo.wait_for_text_to_equal("#secondary-output", "no-output2")


def test_arb003_arbitrary_pages(dash_duo):
    app = Dash(use_pages=True, pages_folder="")

    register_page(
        "page",
        "/",
        layout=html.Div(
            [
                html.Div(id="secondary-output"),
                html.Button("no-output", id="no-output"),
                html.Button("no-output2", id="no-output2"),
            ]
        ),
    )

    @app.callback(
        Input("no-output", "n_clicks"),
        prevent_initial_call=True,
    )
    def no_output(_):
        set_props("secondary-output", {"children": "no-output"})

    @app.callback(
        Input("no-output2", "n_clicks"),
        prevent_initial_call=True,
    )
    def no_output(_):
        set_props("secondary-output", {"children": "no-output2"})

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#no-output").click()
    dash_duo.wait_for_text_to_equal("#secondary-output", "no-output")

    dash_duo.wait_for_element("#no-output2").click()
    dash_duo.wait_for_text_to_equal("#secondary-output", "no-output2")


def test_arb004_wildcard_set_props(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            html.Button("click", id="click"),
            html.Div(html.Div(id={"id": "output", "index": 0}), id="output"),
        ]
    )

    @app.callback(
        Input("click", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        set_props(
            {"id": "output", "index": 0}, {"children": f"Clicked {n_clicks} times"}
        )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#click").click()
    dash_duo.wait_for_text_to_equal("#output", "Clicked 1 times")
