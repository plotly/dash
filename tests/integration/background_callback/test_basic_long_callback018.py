from tests.integration.background_callback.utils import setup_background_callback_app


def test_lcbc018_background_callback_on_error(dash_duo, manager):
    with setup_background_callback_app(manager, "app_bg_on_error") as app:
        dash_duo.start_server(app)

        dash_duo.find_element("#start-cb-onerror").click()

        dash_duo.wait_for_contains_text("#cb-output", "callback error")

        dash_duo.find_element("#start-global-onerror").click()
        dash_duo.wait_for_contains_text("#global-output", "global error")
