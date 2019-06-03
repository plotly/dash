"""Utils methods for pytest-dash such wait_for wrappers"""
import time
import logging
from dash.testing.errors import TestingTimeoutError


logger = logging.getLogger(__name__)


def until(
    wait_cond,
    timeout,
    poll=0.1,
    msg="expected condition not met within timeout",
):  # noqa: C0330
    end_time = time.time() + timeout
    while not wait_cond():
        if time.time() > end_time:
            raise TestingTimeoutError(msg)
        time.sleep(poll)


def until_not(
    wait_cond, timeout, poll=0.1, msg="expected condition met within timeout"
):  # noqa: C0330
    end_time = time.time() + timeout
    while wait_cond():
        if time.time() > end_time:
            raise TestingTimeoutError(msg)
        time.sleep(poll)


class text_to_equal(object):  # pylint: disable=too-few-public-methods
    def __init__(self, selector, text):
        self.selector = selector
        self.text = text

    def __call__(self, driver):
        elem = driver.find_element_by_css_selector(self.selector)
        return (
            str(elem.text) == self.text
            or str(elem.get_attribute("value")) == self.text
        )
