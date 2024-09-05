import pytest
from dash import Dash, html, Output, Input


@pytest.mark.skip(reason="Hot-reload & clientside callbacks doesn't work properly")
def test_clrs001_clientside_inline_restarts(dash_duo_mp):
    # FIXME find another way to test clientside callbacks restarts
    reloads = 0

    def create_app():
        nonlocal reloads

        app = Dash(__name__)

        app.layout = html.Div(
            [
                html.Button("Click", id="click"),
                html.Div(id="output"),
                html.Div(reloads, id="reload"),
            ]
        )

        app.clientside_callback(
            "(n_clicks) => `clicked ${n_clicks}`",
            Output("output", "children"),
            Input("click", "n_clicks"),
            prevent_initial_call=True,
        )
        reloads += 1
        return app

    hot_reload_settings = dict(
        dev_tools_hot_reload=True,
        dev_tools_ui=True,
        dev_tools_serve_dev_bundles=True,
        dev_tools_hot_reload_interval=0.1,
        dev_tools_hot_reload_max_retry=100,
    )

    dash_duo_mp.start_server(create_app(), **hot_reload_settings)
    dash_duo_mp.find_element("#click").click()
    dash_duo_mp.wait_for_text_to_equal("#output", "clicked 1")

    dash_duo_mp.server.stop()

    dash_duo_mp.start_server(create_app(), navigate=False, **hot_reload_settings)
    dash_duo_mp.wait_for_text_to_equal("#reload", "1")
    dash_duo_mp.find_element("#click").click()
    # reloaded so 1 again.
    dash_duo_mp.wait_for_text_to_equal("#output", "clicked 1")
