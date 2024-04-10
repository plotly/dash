from tests.integration.long_callback.utils import setup_long_callback_app


def test_lcbc017_long_callback_set_props(dash_duo, manager):
    with setup_long_callback_app(manager, "app_arbitrary") as app:
        dash_duo.start_server(app)

        with app.test_lock:
            dash_duo.find_element("#start").click()

        dash_duo.wait_for_text_to_equal("#secondary", "first")
        dash_duo.wait_for_text_to_equal("#output", "initial")
        dash_duo.wait_for_text_to_equal("#secondary", "second")
        dash_duo.wait_for_text_to_equal("#output", "completed")

        dash_duo.find_element("#start-no-output").click()

        dash_duo.wait_for_text_to_equal("#no-output", "started")
        dash_duo.wait_for_text_to_equal("#no-output", "completed")
