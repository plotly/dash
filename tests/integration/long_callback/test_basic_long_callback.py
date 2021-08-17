from multiprocessing import Lock
import os
from contextlib import contextmanager
import subprocess
import tempfile
import pytest
import shutil
import time

from dash.testing.application_runners import import_app
import psutil
import redis


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


if "REDIS_URL" in os.environ:
    managers = ["diskcache", "celery"]
else:
    print("Skipping celery tests because REDIS_URL is not defined")
    managers = ["diskcache"]


@pytest.fixture(params=managers)
def manager(request):
    return request.param


@contextmanager
def setup_long_callback_app(manager_name, app_name):
    if manager_name == "celery":
        os.environ["LONG_CALLBACK_MANAGER"] = "celery"
        redis_url = os.environ["REDIS_URL"].rstrip("/")
        os.environ["CELERY_BROKER"] = f"{redis_url}/0"
        os.environ["CELERY_BACKEND"] = f"{redis_url}/1"

        # Clear redis of cached values
        redis_conn = redis.Redis(host="localhost", port=6379, db=1)
        cache_keys = redis_conn.keys()
        if cache_keys:
            redis_conn.delete(*cache_keys)

        worker = subprocess.Popen(
            [
                "celery",
                "-A",
                f"tests.integration.long_callback.{app_name}:handle",
                "worker",
                "-P",
                "prefork",
                "--concurrency",
                "2",
                "--loglevel=info",
            ],
            preexec_fn=os.setpgrp,
        )
        try:
            yield import_app(f"tests.integration.long_callback.{app_name}")
        finally:
            # Interval may run one more time after settling on final app state
            # Sleep for 1 interval of time
            time.sleep(0.5)
            os.environ.pop("LONG_CALLBACK_MANAGER")
            os.environ.pop("CELERY_BROKER")
            os.environ.pop("CELERY_BACKEND")
            kill(worker.pid)

    elif manager_name == "diskcache":
        os.environ["LONG_CALLBACK_MANAGER"] = "diskcache"
        cache_directory = tempfile.mkdtemp(prefix="lc-diskcache-")
        print(cache_directory)
        os.environ["DISKCACHE_DIR"] = cache_directory
        try:
            yield import_app(f"tests.integration.long_callback.{app_name}")
        finally:
            # Interval may run one more time after settling on final app state
            # Sleep for 1 interval of time
            time.sleep(0.5)
            shutil.rmtree(cache_directory, ignore_errors=True)
            os.environ.pop("LONG_CALLBACK_MANAGER")
            os.environ.pop("DISKCACHE_DIR")


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


def test_lcbc003_long_callback_running_cancel(dash_duo, manager):
    lock = Lock()

    with setup_long_callback_app(manager, "app3") as app:
        dash_duo.start_server(app)
        dash_duo.wait_for_text_to_equal("#result", "No results", 15)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 6)

        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#result", "Processed 'initial value'", 15)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 6)

        # Update input text box
        input_ = dash_duo.find_element("#input")
        dash_duo.clear_input(input_)

        for key in "hello world":
            with lock:
                input_.send_keys(key)

        # Click run button and check that status has changed to "Running"
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Running", 8)

        # Then click Cancel button and make sure that the status changes to finish
        # without update result
        dash_duo.find_element("#cancel-button").click()
        dash_duo.wait_for_text_to_equal("#result", "Processed 'initial value'", 12)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)

        # Click run button again, and let it finish
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Running", 8)
        dash_duo.wait_for_text_to_equal("#result", "Processed 'hello world'", 8)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)

    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_lcbc004_long_callback_progress(dash_duo, manager):
    with setup_long_callback_app(manager, "app4") as app:
        dash_duo.start_server(app)
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


def test_lcbc005_long_callback_caching(dash_duo, manager):
    lock = Lock()

    with setup_long_callback_app(manager, "app5") as app:
        dash_duo.start_server(app)
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 15)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 15)
        dash_duo.wait_for_text_to_equal("#result", "Result for 'AAA'", 8)

        # Update input text box to BBB
        input_ = dash_duo.find_element("#input")
        dash_duo.clear_input(input_)
        for key in "BBB":
            with lock:
                input_.send_keys(key)

        # Click run button and check that status eventually cycles to 2/4
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result", "Result for 'BBB'", 8)

        # Update input text box back to AAA
        input_ = dash_duo.find_element("#input")
        dash_duo.clear_input(input_)
        for key in "AAA":
            with lock:
                input_.send_keys(key)

        # Click run button and this time the cached result is used,
        # So we can get the result right away
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result", "Result for 'AAA'", 8)

        # Update input text box back to BBB
        input_ = dash_duo.find_element("#input")
        dash_duo.clear_input(input_)
        for key in "BBB":
            with lock:
                input_.send_keys(key)

        # Click run button and this time the cached result is used,
        # So we can get the result right away
        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Finished", 8)
        dash_duo.wait_for_text_to_equal("#result", "Result for 'BBB'", 8)

        # Update input text box back to AAA
        input_ = dash_duo.find_element("#input")
        dash_duo.clear_input(input_)
        for key in "AAA":
            with lock:
                input_.send_keys(key)

        # Change cache key
        app._cache_key.value = 1

        dash_duo.find_element("#run-button").click()
        dash_duo.wait_for_text_to_equal("#status", "Progress 2/4", 20)
        dash_duo.wait_for_text_to_equal("#status", "Finished", 12)
        dash_duo.wait_for_text_to_equal("#result", "Result for 'AAA'", 8)

        assert not dash_duo.redux_state_is_loading
        assert dash_duo.get_logs() == []


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
