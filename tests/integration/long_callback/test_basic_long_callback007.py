import sys

import pytest
from flaky import flaky

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
@flaky(max_runs=3)
def test_lcbc007_validation_layout(dash_duo, manager):
    with setup_long_callback_app(manager, "app7") as app:
        dash_duo.start_server(app)

        # Show layout
        dash_duo.find_element("#show-layout-button").click()

        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result", "No results", 8)

        # click run and check that status eventually cycles to 2/4
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 15)

        # Then click Cancel button and make sure that the status changes to finish
        # without updating result
        dash_duo.find_element("#cancel-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result", "No results", 8)

        # Click run button and allow callback to finish
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 15)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 15)
        dash_duo.wait_for_text_to_equal("#result", "Processed 'hello, world'", 8)

        # Click run button again with same input.
        # without caching, this should rerun callback and display progress
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 15)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 15)
        dash_duo.wait_for_text_to_equal("#result", "Processed 'hello, world'", 8)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []
