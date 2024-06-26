from tests.integration.long_callback.utils import setup_long_callback_app


def test_lcbc017_long_callback_set_props(dash_duo, manager):
    with setup_long_callback_app(manager, "app_bg_on_error") as app:
        dash_duo.start_server(app)

        dash_duo.find_element("#start-cb-onerror").click()

        dash_duo.wait_for_text_to_equal("#cb-output", "callback: callback error")

        dash_duo.find_element("#start-global-onerror").click()
        dash_duo.wait_for_text_to_equal("#global-output", "global: global error")
