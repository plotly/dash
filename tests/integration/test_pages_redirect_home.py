import dash
import pytest


def test_pare001_redirect_home(dash_duo):
    pytest.skip("Revisit later")

    app = dash.Dash(__name__, use_pages=True, pages_folder="")

    dash.register_page(
        "multi_layout1",
        layout=dash.html.Div("text for multi_layout1", id="text_multi_layout1"),
        path="/",
    )

    dash.register_page(
        "redirect_home",
        redirect_from=["/"],
        layout=dash.html.Div("Redirect", id="redirect"),
    )

    app.layout = dash.page_container

    dash_duo.start_server(app)

    dash_duo.wait_for_page(url=f"http://localhost:{dash_duo.server.port}/redirect-home")
    dash_duo.wait_for_text_to_equal("#redirect", "Redirect")

    assert dash_duo.get_logs() == [], "browser console should contain no error"

    # clean up after this test, so this redirect does not affect other pages tests
    del dash.page_registry["redirect_home"]
