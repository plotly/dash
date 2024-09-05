import sys

import pytest

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc008_long_callbacks_error(dash_duo, manager):
    with setup_long_callback_app(manager, "app_error") as app:
        dash_duo.start_server(
            app,
            debug=True,
            use_reloader=False,
            use_debugger=True,
            dev_tools_hot_reload=False,
            dev_tools_ui=True,
        )

        clicker = dash_duo.wait_for_element("#button")

        def click_n_wait():
            clicker.click()
            dash_duo.wait_for_element("#button:disabled")
            dash_duo.wait_for_element("#button:not([disabled])")

        clicker.click()
        dash_duo.wait_for_text_to_equal("#output", "Clicked 1 times")

        click_n_wait()
        dash_duo.wait_for_element(".dash-fe-error__title").click()

        dash_duo.driver.switch_to.frame(dash_duo.find_element("iframe"))
        assert (
            "dash.exceptions.LongCallbackError: An error occurred inside a long callback:"
            in dash_duo.wait_for_element(".errormsg").text
        )
        dash_duo.driver.switch_to.default_content()

        click_n_wait()
        dash_duo.wait_for_text_to_equal("#output", "Clicked 3 times")

        click_n_wait()
        dash_duo.wait_for_text_to_equal("#output", "Clicked 3 times")
        click_n_wait()
        dash_duo.wait_for_text_to_equal("#output", "Clicked 5 times")

        def make_expect(n):
            return [str(x) for x in range(1, n + 1)] + ["" for _ in range(n + 1, 4)]

        multi = dash_duo.wait_for_element("#multi-output")

        for i in range(1, 4):
            with app.test_lock:
                multi.click()
                dash_duo.wait_for_element("#multi-output:disabled")
            expect = make_expect(i)
            dash_duo.wait_for_text_to_equal("#output-status", f"Updated: {i}")
            for j, e in enumerate(expect):
                assert dash_duo.find_element(f"#output{j + 1}").text == e
