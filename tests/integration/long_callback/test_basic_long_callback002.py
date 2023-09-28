import sys

import pytest
from flaky import flaky

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
@flaky(max_runs=3)
def test_lcbc002_long_callback_running(dash_duo, manager):
    with setup_long_callback_app(manager, "app2") as app:
        dash_duo.start_server(app)
        dash_duo.wait_for_text_to_equal("#result", "Not clicked", 15)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)

        # Click button and check that status has changed to "Running"
        dash_duo.find_element("#button-1").click()
        dash_duo.wait_for_text_to_equal("#status", "Running", 8)

        # Wait for calculation to finish, then check that status is "Finished"
        dash_duo.wait_for_text_to_equal("#result", "Clicked 1 time(s)", 12)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)

        # Click button twice and check that status has changed to "Running"
        dash_duo.find_element("#button-1").click()
        dash_duo.find_element("#button-1").click()
        dash_duo.wait_for_text_to_equal("#status", "Running", 8)

        # Wait for calculation to finish, then check that status is "Finished"
        dash_duo.wait_for_text_to_equal("#result", "Clicked 3 time(s)", 12)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []
