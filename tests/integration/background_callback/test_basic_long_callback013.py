import sys

import pytest

from tests.integration.background_callback.utils import setup_background_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc013_unordered_state_input(dash_duo, manager):
    with setup_background_callback_app(manager, "app_unordered") as app:
        dash_duo.start_server(app)
        dash_duo.find_element("#click").click()

        dash_duo.wait_for_text_to_equal("#output", "stored")
