from tests.integration.long_callback.utils import setup_long_callback_app


def test_lcbc013_unordered_state_input(dash_duo, manager):
    with setup_long_callback_app(manager, "app_unordered") as app:
        dash_duo.start_server(app)
        dash_duo.find_element("#click").click()

        dash_duo.wait_for_text_to_equal("#output", "stored")
