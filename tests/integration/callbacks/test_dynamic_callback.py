from dash import html, Dash, Input, Output


# WARNING: dynamic callback creation can be dangerous, use at you own risk.
# It is not intended for use in a production app, multi-user
# or multiprocess use as it only works for a single user.
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

    dash_duo.wait_for_element("#dynamic").click()
    dash_duo.wait_for_element("#create").click()
    dash_duo.wait_for_text_to_equal("#output", "creator 1")
    dash_duo.wait_for_text_to_equal("#output-2", "initial")

    dash_duo.wait_for_element("#dynamic").click()
    dash_duo.wait_for_text_to_equal("#output-2", "Dynamic clicks 2")


def test_dync002_dynamic_callback_without_element(dash_duo):
    app = Dash()

    app.layout = html.Div(
        [
            html.Button("Add callbacks", id="add-callbacks"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("add-callbacks", "n_clicks"),
        _allow_dynamic_callbacks=True,
        prevent_initial_call=True,
    )
    def on_add_callback(_):
        @app.callback(Output("no-exist", "children"), Input("invalid", "n_clicks"))
        def addition(_):
            return "additional"

        return html.Div("add callbacks")

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#add-callbacks").click()
    dash_duo.wait_for_text_to_equal("#output", "add callbacks")

    assert dash_duo.get_logs() == []


def test_dyn003_dynamic_callback_import_library(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            html.Button("insert", id="insert"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("insert", "n_clicks"),
        _allow_dynamic_callbacks=True,
        prevent_initial_call=True,
    )
    def on_click(_):
        import dash_test_components as dt

        return dt.StyledComponent(
            value="inserted", id="inserted", style={"backgroundColor": "red"}
        )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#insert").click()
    dash_duo.wait_for_text_to_equal("#inserted", "inserted")
