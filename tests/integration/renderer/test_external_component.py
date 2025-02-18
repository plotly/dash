from dash import Dash, html, dcc, html, Input, Output, State
from dash_test_components import ExternalComponent


def test_rext001_render_external_component(dash_duo):
    app = Dash()
    app.layout = html.Div(
        [
            dcc.Input(id="sync", value="synced"),
            html.Button("sync", id="sync-btn"),
            ExternalComponent("ext", input_id="external", text="external"),
        ]
    )

    @app.callback(
        Output("ext", "text"),
        Input("sync-btn", "n_clicks"),
        State("sync", "value"),
        prevent_initial_call=True,
    )
    def on_sync(_, value):
        return value

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#external", "external")
    dash_duo.find_element("#sync-btn").click()
    dash_duo.wait_for_text_to_equal("#external", "synced")
