import dash


def test_pare001_redirect_home(dash_duo):

    app = dash.Dash(__name__, use_pages=True, pages_folder="")

    dash.register_page("home", path="/", layout="Home")

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
    del dash.page_registry["home"]
    del dash.page_registry["redirect_home"]
