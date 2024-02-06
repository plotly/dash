import sys
from multiprocessing import Lock

import pytest
from flaky import flaky

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
@flaky(max_runs=3)
def test_lcbc006_long_callback_caching_multi(dash_duo, manager):
    lock = Lock()

    with setup_long_callback_app(manager, "app6") as app:
        dash_duo.start_server(app)
        dash_duo.wait_for_text_to_equal("#status1", "Progress 2/4", 15)
        dash_duo.wait_for_text_to_equal("#status1", "Finished", 15)
        dash_duo.wait_for_text_to_equal("#result1", "Result for 'AAA'", 8)

        # Check initial status/output of second long_callback
        # prevent_initial_callback=True means no calculation should have run yet
        dash_duo.wait_for_text_to_equal("#status2", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result2", "No results", 8)

        # Click second run button
        dash_duo.find_element("#run-button2").click()
        dash_duo.wait_for_text_to_equal("#status2", "Progress 2/4", 15)
        dash_duo.wait_for_text_to_equal("#result2", "Result for 'aaa'", 8)

        # Update input text box to BBB
        input_ = dash_duo.find_element("#input1")
        dash_duo.clear_input(input_)
        for key in "BBB":
            with lock:
                input_.send_keys(key)

        # Click run button and check that status eventually cycles to 2/4
        dash_duo.find_element("#run-button1").click()
        dash_duo.wait_for_text_to_equal("#status1", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status1", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result1", "Result for 'BBB'", 8)

        # Check there were no changes in second long_callback output
        dash_duo.wait_for_text_to_equal("#status2", "Finished", 15)
        dash_duo.wait_for_text_to_equal("#result2", "Result for 'aaa'", 8)

        # Update input text box back to AAA
        input_ = dash_duo.find_element("#input1")
        dash_duo.clear_input(input_)
        for key in "AAA":
            with lock:
                input_.send_keys(key)

        # Click run button and this time the cached result is used,
        # So we can get the result right away
        dash_duo.find_element("#run-button1").click()
        dash_duo.wait_for_text_to_equal("#status1", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result1", "Result for 'AAA'", 8)

        # Update input text box back to BBB
        input_ = dash_duo.find_element("#input1")
        dash_duo.clear_input(input_)
        for key in "BBB":
            with lock:
                input_.send_keys(key)

        # Click run button and this time the cached result is used,
        # So we can get the result right away
        dash_duo.find_element("#run-button1").click()
        dash_duo.wait_for_text_to_equal("#status1", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result1", "Result for 'BBB'", 8)

        # Update second input text box to BBB, make sure there is not a cache hit
        input_ = dash_duo.find_element("#input2")
        dash_duo.clear_input(input_)
        for key in "BBB":
            with lock:
                input_.send_keys(key)
        dash_duo.find_element("#run-button2").click()
        dash_duo.wait_for_text_to_equal("#status2", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status2", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result2", "Result for 'BBB'", 8)

        # Update second input text box back to aaa, check for cache hit
        input_ = dash_duo.find_element("#input2")
        dash_duo.clear_input(input_)
        for key in "aaa":
            with lock:
                input_.send_keys(key)
        dash_duo.find_element("#run-button2").click()
        dash_duo.wait_for_text_to_equal("#status2", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result2", "Result for 'aaa'", 8)

        # Update input text box back to AAA
        input_ = dash_duo.find_element("#input1")
        dash_duo.clear_input(input_)
        for key in "AAA":
            with lock:
                input_.send_keys(key)

        # Change cache key to cause cache miss
        app._cache_key.value = 1

        # Check for cache miss for first long_callback
        dash_duo.find_element("#run-button1").click()
        dash_duo.wait_for_text_to_equal("#status1", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status1", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result1", "Result for 'AAA'", 8)

        # Check for cache miss for second long_callback
        dash_duo.find_element("#run-button2").click()
        dash_duo.wait_for_text_to_equal("#status2", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status2", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result2", "Result for 'aaa'", 8)

        assert not dash_duo.redux_state_is_loading
        assert dash_duo.get_logs() == []
