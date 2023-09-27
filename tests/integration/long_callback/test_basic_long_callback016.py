import sys
import time

import pytest

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc016_multi_page_cancel(dash_duo, manager):
    with setup_long_callback_app(manager, "app_page_cancel") as app:
        dash_duo.start_server(app)
        dash_duo.find_element("#start1").click()
        dash_duo.wait_for_text_to_equal("#progress1", "running")
        dash_duo.find_element("#shared_cancel").click()
        dash_duo.wait_for_text_to_equal("#progress1", "idle")
        time.sleep(2.1)
        dash_duo.wait_for_text_to_equal("#output1", "initial")

        dash_duo.find_element("#start1").click()
        dash_duo.wait_for_text_to_equal("#progress1", "running")
        dash_duo.find_element("#cancel1").click()
        dash_duo.wait_for_text_to_equal("#progress1", "idle")
        time.sleep(2.1)
        dash_duo.wait_for_text_to_equal("#output1", "initial")

        dash_duo.server_url = dash_duo.server_url + "/2"

        dash_duo.find_element("#start2").click()
        dash_duo.wait_for_text_to_equal("#progress2", "running")
        dash_duo.find_element("#shared_cancel").click()
        dash_duo.wait_for_text_to_equal("#progress2", "idle")
        time.sleep(2.1)
        dash_duo.wait_for_text_to_equal("#output2", "initial")

        dash_duo.find_element("#start2").click()
        dash_duo.wait_for_text_to_equal("#progress2", "running")
        dash_duo.find_element("#cancel2").click()
        dash_duo.wait_for_text_to_equal("#progress2", "idle")
        time.sleep(2.1)
        dash_duo.wait_for_text_to_equal("#output2", "initial")
