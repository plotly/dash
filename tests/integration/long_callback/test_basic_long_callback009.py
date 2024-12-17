import sys
import time

import pytest

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc009_short_interval(dash_duo, manager):
    with setup_long_callback_app(manager, "app_short_interval") as app:
        dash_duo.start_server(app)
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result", "Clicked '1'")

        time.sleep(2)
        # Ensure the progress is still not running
        assert dash_duo.find_element("#status").text == "Finished"
