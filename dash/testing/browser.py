# pylint: disable=missing-docstring
import os
import sys
import logging
import warnings
import percy

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import WebDriverException, TimeoutException

from dash.testing.wait import text_to_equal
from dash.testing.errors import DashAppLoadingError

logger = logging.getLogger(__name__)


class Browser:
    def __init__(self, browser, remote=None, wait_timeout=10):
        self._browser = browser.lower()
        self._wait_timeout = wait_timeout

        self._driver = self.get_webdriver(remote)
        self._driver.implicitly_wait(2)

        self._wd_wait = WebDriverWait(
            driver=self.driver, timeout=wait_timeout, poll_frequency=0.2
        )
        self._last_ts = 0
        self._url = None

        self.percy_runner = percy.Runner(
            loader=percy.ResourceLoader(
                webdriver=self.driver,
                base_url="/assets",
                root_dir="tests/assets",
            )
        )
        self.percy_runner.initialize_build()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        try:
            self.driver.quit()
            self.percy_runner.finalize_build()
        except WebDriverException:
            logger.exception("webdriver quit was not successfully")
        except percy.errors.Error:
            logger.exception("percy runner failed to finalize properly")

    def percy_snapshot(self, name=""):
        snapshot_name = "{} - py{}.{}".format(
            name, sys.version_info.major, sys.version_info.minor
        )
        logger.info("taking snapshot name => %s", snapshot_name)
        self.percy_runner.snapshot(name=snapshot_name)

    def _wait_for(self, method, args, timeout, msg):
        """abstract generic pattern for explicit webdriver wait"""
        _wait = (
            self._wd_wait
            if timeout is None
            else WebDriverWait(self.driver, timeout)
        )
        return _wait.until(method(*args), msg)

    def wait_for_element(self, css_selector, timeout=None):
        self.wait_for_element_by_css_selector(css_selector, timeout)

    # keep these two wait_for API for easy migration
    def wait_for_element_by_css_selector(self, selector, timeout=None):
        return self._wait_for(
            EC.presence_of_element_located,
            ((By.CSS_SELECTOR, selector),),
            timeout,
            "cannot find_element using the css selector",
        )

    def wait_for_text_to_equal(self, selector, text, timeout=None):
        return self._wait_for(
            text_to_equal,
            (selector, text),
            timeout,
            "cannot wait until element contains expected text {}".format(text),
        )

    def wait_for_page(self, timeout=10):

        self.driver.get(self.server_url)
        try:
            self.wait_for_element_by_css_selector(
                "#react-entry-point", timeout=timeout
            )
        except TimeoutException:
            logger.exception(
                "dash server is not loaded within %s seconds", timeout
            )
            raise DashAppLoadingError(
                "the expected Dash react entry point cannot be loaded"
                " in browser\n HTML => {}\n Console Logs => {}\n".format(
                    self.driver.find_element_by_tag_name("body").get_property(
                        "innerHTML"
                    ),
                    "\n".join(self.get_logs()),
                )
            )

    def get_webdriver(self, remote):
        return (
            getattr(self, "_get_{}".format(self._browser))()
            if remote is None
            else webdriver.Remote(
                command_executor=remote,
                desired_capabilities=getattr(
                    DesiredCapabilities, self._browser.upper()
                ),
            )
        )

    @staticmethod
    def _get_chrome():
        options = Options()
        options.add_argument("--no-sandbox")

        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"browser": "SEVERE"}

        if "DASH_TEST_CHROMEPATH" in os.environ:
            options.binary_location = os.environ["DASH_TEST_CHROMEPATH"]

        chrome = webdriver.Chrome(
            options=options, desired_capabilities=capabilities
        )
        chrome.set_window_position(0, 0)
        return chrome

    @staticmethod
    def _get_firefox():

        capabilities = DesiredCapabilities.FIREFOX
        capabilities["loggingPrefs"] = {"browser": "SEVERE"}
        capabilities["marionette"] = True

        # https://developer.mozilla.org/en-US/docs/Download_Manager_preferences
        fp = webdriver.FirefoxProfile()

        # this will be useful if we wanna test download csv or other data
        # files with selenium
        # TODO this can be fed as a tmpdir fixture from pytest
        fp.set_preference("browser.download.dir", "/tmp")
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)

        return webdriver.Firefox(fp, capabilities=capabilities)

    def get_logs(self):
        """get_logs works only with chrome webdriver"""
        if self.driver.name == 'Chrome':
            return (
                [
                    entry
                    for entry in self.driver.get_log("browser")
                    if entry["timestamp"] > self._last_ts
                ]
            )
        warnings.warn(
            "get_logs always return None with your webdriver {}".format(
                self.driver.name
            ))
        return None

    def reset_log_timestamp(self):
        """reset_log_timestamp only work with chrome webdrier"""
        if self.driver.name == "chrome":
            entries = self.driver.get_log("browser")
            if entries:
                self._last_ts = entries[-1]["timestamp"]

    @property
    def driver(self):
        return self._driver

    @property
    def session_id(self):
        return self.driver.session_id

    @property
    def server_url(self):
        return self._url

    @server_url.setter
    def server_url(self, value):
        """property setter for server_url

        Note: set server_url will implicitly check the server is ready
        for selenium testing
        """
        self._url = value
        self.wait_for_page()
