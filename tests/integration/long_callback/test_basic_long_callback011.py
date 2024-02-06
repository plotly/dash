import sys

import pytest

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc011_long_pattern_matching(dash_duo, manager):
    with setup_long_callback_app(manager, "app_pattern_matching") as app:
        dash_duo.start_server(app)
        for i in range(1, 4):
            for _ in range(i):
                dash_duo.find_element(f"button:nth-child({i})").click()

            dash_duo.wait_for_text_to_equal("#result", f"Clicked '{i}'")
