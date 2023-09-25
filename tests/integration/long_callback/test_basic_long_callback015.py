from tests.integration.long_callback.utils import setup_long_callback_app


def test_lcbc015_diff_outputs_same_func(dash_duo, manager):
    with setup_long_callback_app(manager, "app_diff_outputs") as app:
        dash_duo.start_server(app)

        for i in range(1, 3):
            dash_duo.find_element(f"#button-{i}").click()
            dash_duo.wait_for_text_to_equal(f"#output-{i}", f"Clicked on {i}")
