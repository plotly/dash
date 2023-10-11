import sys
from multiprocessing import Lock

import pytest
from flaky import flaky

from .utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
@flaky(max_runs=3)
def test_lcbc001_fast_input(dash_duo, manager):
    """
    Make sure that we settle to the correct final value when handling rapid inputs
    """
    lock = Lock()
    with setup_long_callback_app(manager, "app1") as app:
        dash_duo.start_server(app)
        dash_duo.wait_for_text_to_equal("#output-1", "initial value", 15)
        input_ = dash_duo.find_element("#input")
        dash_duo.clear_input(input_)

        for key in "hello world":
            with lock:
                input_.send_keys(key)

        dash_duo.wait_for_text_to_equal("#output-1", "hello world", 8)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []
