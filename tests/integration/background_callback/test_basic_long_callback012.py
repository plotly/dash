import json
import sys

import pytest

from tests.integration.background_callback.utils import setup_background_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc012_long_callback_ctx(dash_duo, manager):
    with setup_background_callback_app(manager, "app_callback_ctx") as app:
        dash_duo.start_server(app)
        dash_duo.find_element("button:nth-child(1)").click()
        dash_duo.wait_for_text_to_equal("#running", "off")

        output = json.loads(dash_duo.find_element("#result").text)

        assert output["triggered"]["index"] == 0
