# pylint: disable=too-few-public-methods
"""Utils methods for pytest-dash such wait_for wrappers"""
import time
import logging
from selenium.common.exceptions import StaleElementReferenceException
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
        try:
            elem = driver.find_element_by_css_selector(self.selector)
            logger.debug(
                "text to equal {%s} => expected %s", elem.text, self.text
            )
            return (
                str(elem.text) == self.text
                or str(elem.get_attribute("value")) == self.text
            )
        except StaleElementReferenceException:
            logger.warning("text_to_equal, element is still stale")
            return False
