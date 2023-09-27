import sys

import pytest

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc010_side_updates(dash_duo, manager):
    with setup_long_callback_app(manager, "app_side_update") as app:
        dash_duo.start_server(app)
        dash_duo.find_element("#run-button").click()
        for i in range(1, 4):
            dash_duo.wait_for_text_to_equal("#side-status", f"Side Progress {i}/4")
