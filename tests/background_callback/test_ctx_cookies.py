from tests.background_callback.utils import setup_background_callback_app


def test_lcbc019_ctx_cookies(dash_duo, manager):
    with setup_background_callback_app(manager, "app_ctx_cookies") as app:
        dash_duo.start_server(app)

        dash_duo.find_element("#set-cookies").click()
        dash_duo.wait_for_contains_text("#intermediate", "ok")

        dash_duo.find_element("#use-cookies").click()
        dash_duo.wait_for_contains_text("#output", "cookie-value")
