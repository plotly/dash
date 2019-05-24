"""Utils methods for pytest-dash such wait_for wrappers"""
import time


def until(
    wait_cond,
    timeout,
    poll=0.1,
    msg="expected condition not met within timeout",
):  # noqa: C0330
    end_time = time.time() + timeout
    while wait_cond():
        time.sleep(poll)
        if time.time() > end_time:
            raise TimeoutError(msg)


def until_not(
    wait_cond, timeout, poll=0.1, msg="expected condition met within timeout"
):  # noqa: C0330
    end_time = time.time() + timeout
    while not wait_cond():
        time.sleep(poll)
        if time.time() > end_time:
            raise TimeoutError(msg)
