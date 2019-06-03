# pylint: disable=too-few-public-methods
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
    res = None
    logger.debug(
        "start wait.until with %s, timeout[%s], poll[%s]",
        wait_cond,
        timeout,
        poll,
    )
    end_time = time.time() + timeout
    while not res:
        if time.time() > end_time:
            raise TestingTimeoutError(msg)
        time.sleep(poll)
        res = wait_cond()
        logger.debug("poll => %s", time.time())

    return res


def until_not(
    wait_cond, timeout, poll=0.1, msg="expected condition met within timeout"
):  # noqa: C0330
    res = True
    logger.debug(
        "start wait.until with %s, timeout[%s], poll[%s]",
        wait_cond,
        timeout,
        poll,
    )
    end_time = time.time() + timeout
    while res:
        if time.time() > end_time:
            raise TestingTimeoutError(msg)
        time.sleep(poll)
        res = wait_cond()
        logger.debug("poll => %s", time.time())

    return res


class text_to_equal(object):
    def __init__(self, selector, text):
        self.selector = selector
        self.text = text

    def __call__(self, driver):
        elem = driver.find_element_by_css_selector(self.selector)
        return (
            str(elem.text) == self.text
            or str(elem.get_attribute("value")) == self.text
        )
