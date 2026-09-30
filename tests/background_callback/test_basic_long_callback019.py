from tests.background_callback.utils import setup_background_callback_app


def test_lcbc019_background_callback_on_error_without_output(dash_duo, manager):
    with setup_background_callback_app(manager, "app_bg_on_error") as app:
        dash_duo.start_server(app)

        dash_duo.find_element("#start-no-output-cb-onerror").click()
        dash_duo.wait_for_contains_text(
            "#no-output-cb-onerror-output",
            "callback: An error occurred inside a background callback: no output callback error",
        )
