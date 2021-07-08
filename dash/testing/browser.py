# pylint: disable=missing-docstring
import os
import sys
import time
import logging
import warnings
import percy

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    MoveTargetOutOfBoundsException,
)

from dash.testing.wait import text_to_equal, style_to_equal, contains_text, until
from dash.testing.dash_page import DashPageMixin
from dash.testing.errors import DashAppLoadingError, BrowserError, TestingTimeoutError
from dash.testing.consts import SELENIUM_GRID_DEFAULT


logger = logging.getLogger(__name__)


class Browser(DashPageMixin):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        browser,
        remote=False,
        remote_url=None,
        headless=False,
        options=None,
        download_path="",
        percy_run=True,
        percy_finalize=True,
        percy_assets_root="",
        wait_timeout=10,
        pause=False,
    ):
        self._browser = browser.lower()
        self._remote_url = remote_url
        self._remote = (
            True if remote_url and remote_url != SELENIUM_GRID_DEFAULT else remote
        )
        self._headless = headless
        self._options = options
        self._download_path = download_path
        self._wait_timeout = wait_timeout
        self._percy_finalize = percy_finalize
        self._percy_run = percy_run
        self._pause = pause

        self._driver = until(self.get_webdriver, timeout=1)
        self._driver.implicitly_wait(2)

        self._wd_wait = WebDriverWait(self.driver, wait_timeout)
        self._last_ts = 0
        self._url = None

        self._window_idx = 0  # switch browser tabs

        if self._percy_run:
            self.percy_runner = percy.Runner(
                loader=percy.ResourceLoader(
                    webdriver=self.driver,
                    base_url="/assets",
                    root_dir=percy_assets_root,
                )
            )
            self.percy_runner.initialize_build()

        logger.debug("initialize browser with arguments")
        logger.debug("  headless => %s", self._headless)
        logger.debug("  download_path => %s", self._download_path)
        logger.debug("  percy asset root => %s", os.path.abspath(percy_assets_root))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        try:
            self.driver.quit()
            if self._percy_run and self._percy_finalize:
                logger.info("percy runner finalize build now")
                self.percy_runner.finalize_build()
            else:
                logger.info("percy finalize relies on CI job")
        except WebDriverException:
            logger.exception("webdriver quit was not successful")
        except percy.errors.Error:
            logger.exception("percy runner failed to finalize properly")

    def visit_and_snapshot(
        self,
        resource_path,
        hook_id,
        wait_for_callbacks=True,
        convert_canvases=False,
        assert_check=True,
        stay_on_page=False,
    ):
        try:
            path = resource_path.lstrip("/")
            if path != resource_path:
                logger.warning("we stripped the left '/' in resource_path")
            self.driver.get("{}/{}".format(self.server_url.rstrip("/"), path))

            # wait for the hook_id to present and all callbacks get fired
            self.wait_for_element_by_id(hook_id)
            self.percy_snapshot(
                path,
                wait_for_callbacks=wait_for_callbacks,
                convert_canvases=convert_canvases,
            )
            if assert_check:
                assert not self.driver.find_elements_by_css_selector(
                    "div.dash-debug-alert"
                ), "devtools should not raise an error alert"
            if not stay_on_page:
                self.driver.back()
        except WebDriverException as e:
            logger.exception("snapshot at resource %s error", path)
            raise e

    def percy_snapshot(self, name="", wait_for_callbacks=False, convert_canvases=False):
        """percy_snapshot - visual test api shortcut to `percy_runner.snapshot`.
        It also combines the snapshot `name` with the Python version.
        """
        snapshot_name = "{} - py{}.{}".format(
            name, sys.version_info.major, sys.version_info.minor
        )
        logger.info("taking snapshot name => %s", snapshot_name)
        try:
            if wait_for_callbacks:
                # the extra one second sleep adds safe margin in the context
                # of wait_for_callbacks
                time.sleep(1)
                until(self._wait_for_callbacks, timeout=40, poll=0.3)
        except TestingTimeoutError:
            # API will log the error but this TimeoutError should not block
            # the test execution to continue and it will still do a snapshot
            # as diff reference for the build run.
            logger.error(
                "wait_for_callbacks failed => status of invalid rqs %s",
                self.redux_state_rqs,
            )

        if convert_canvases:
            self.driver.execute_script(
                """
                const stash = window._canvasStash = [];
                Array.from(document.querySelectorAll('canvas')).forEach(c => {
                    const i = document.createElement('img');
                    i.src = c.toDataURL();
                    i.width = c.width;
                    i.height = c.height;
                    i.setAttribute('style', c.getAttribute('style'));
                    i.className = c.className;
                    i.setAttribute('data-canvasnum', stash.length);
                    stash.push(c);
                    c.parentElement.insertBefore(i, c);
                    c.parentElement.removeChild(c);
                });
            """
            )

            self.percy_runner.snapshot(name=snapshot_name)

            self.driver.execute_script(
                """
                const stash = window._canvasStash;
                Array.from(
                    document.querySelectorAll('img[data-canvasnum]')
                ).forEach(i => {
                    const c = stash[+i.getAttribute('data-canvasnum')];
                    i.parentElement.insertBefore(c, i);
                    i.parentElement.removeChild(i);
                });
                delete window._canvasStash;
            """
            )

        else:
            self.percy_runner.snapshot(name=snapshot_name)

    def take_snapshot(self, name):
        """Hook method to take snapshot when a selenium test fails. The
        snapshot is placed under.

            - `/tmp/dash_artifacts` in linux
            - `%TEMP` in windows
        with a filename combining test case name and the
        running selenium session id
        """
        target = "/tmp/dash_artifacts" if not self._is_windows() else os.getenv("TEMP")
        if not os.path.exists(target):
            try:
                os.mkdir(target)
            except OSError:
                logger.exception("cannot make artifacts")

        self.driver.save_screenshot(
            "{}/{}_{}.png".format(target, name, self.session_id)
        )

    def find_element(self, selector):
        """find_element returns the first found element by the css `selector`
        shortcut to `driver.find_element_by_css_selector`."""
        return self.driver.find_element_by_css_selector(selector)

    def find_elements(self, selector):
        """find_elements returns a list of all elements matching the css
        `selector`.

        shortcut to `driver.find_elements_by_css_selector`.
        """
        return self.driver.find_elements_by_css_selector(selector)

    def _get_element(self, elem_or_selector):
        if isinstance(elem_or_selector, str):
            return self.find_element(elem_or_selector)
        return elem_or_selector

    def _wait_for(self, method, args, timeout, msg):
        """Abstract generic pattern for explicit WebDriverWait."""
        _wait = (
            self._wd_wait if timeout is None else WebDriverWait(self.driver, timeout)
        )
        logger.debug(
            "method, timeout, poll => %s %s %s",
            method,
            _wait._timeout,  # pylint: disable=protected-access
            _wait._poll,  # pylint: disable=protected-access
        )

        return _wait.until(method(*args), msg)

    def wait_for_element(self, selector, timeout=None):
        """wait_for_element is shortcut to `wait_for_element_by_css_selector`
        timeout if not set, equals to the fixture's `wait_timeout`."""
        return self.wait_for_element_by_css_selector(selector, timeout)

    def wait_for_element_by_css_selector(self, selector, timeout=None):
        """Explicit wait until the element is present, timeout if not set,
        equals to the fixture's `wait_timeout` shortcut to `WebDriverWait` with
        `EC.presence_of_element_located`."""
        return self._wait_for(
            EC.presence_of_element_located,
            ((By.CSS_SELECTOR, selector),),
            timeout,
            "timeout {}s => waiting for selector {}".format(
                timeout if timeout else self._wait_timeout, selector
            ),
        )

    def wait_for_no_elements(self, selector, timeout=None):
        """Explicit wait until an element is NOT found. timeout defaults to
        the fixture's `wait_timeout`."""
        until(
            # if we use get_elements it waits a long time to see if they appear
            # so this one calls out directly to execute_script
            lambda: self.driver.execute_script(
                "return document.querySelectorAll('{}').length".format(selector)
            )
            == 0,
            timeout if timeout else self._wait_timeout,
        )

    def wait_for_element_by_id(self, element_id, timeout=None):
        """Explicit wait until the element is present, timeout if not set,
        equals to the fixture's `wait_timeout` shortcut to `WebDriverWait` with
        `EC.presence_of_element_located`."""
        return self._wait_for(
            EC.presence_of_element_located,
            ((By.ID, element_id),),
            timeout,
            "timeout {}s => waiting for element id {}".format(
                timeout if timeout else self._wait_timeout, element_id
            ),
        )

    def wait_for_style_to_equal(self, selector, style, val, timeout=None):
        """Explicit wait until the element's style has expected `value` timeout
        if not set, equals to the fixture's `wait_timeout` shortcut to
        `WebDriverWait` with customized `style_to_equal` condition."""
        return self._wait_for(
            method=style_to_equal,
            args=(selector, style, val),
            timeout=timeout,
            msg="style val => {} {} not found within {}s".format(
                style, val, timeout if timeout else self._wait_timeout
            ),
        )

    def wait_for_text_to_equal(self, selector, text, timeout=None):
        """Explicit wait until the element's text equals the expected `text`.

        timeout if not set, equals to the fixture's `wait_timeout`
        shortcut to `WebDriverWait` with customized `text_to_equal`
        condition.
        """
        return self._wait_for(
            method=text_to_equal,
            args=(selector, text),
            timeout=timeout,
            msg="text -> {} not found within {}s".format(
                text, timeout if timeout else self._wait_timeout
            ),
        )

    def wait_for_contains_text(self, selector, text, timeout=None):
        """Explicit wait until the element's text contains the expected `text`.

        timeout if not set, equals to the fixture's `wait_timeout`
        shortcut to `WebDriverWait` with customized `contains_text`
        condition.
        """
        return self._wait_for(
            method=contains_text,
            args=(selector, text),
            timeout=timeout,
            msg="text -> {} not found inside element within {}s".format(
                text, timeout if timeout else self._wait_timeout
            ),
        )

    def wait_for_page(self, url=None, timeout=10):
        """wait_for_page navigates to the url in webdriver wait until the
        renderer is loaded in browser.

        use the `server_url` if url is not provided.
        """
        self.driver.get(self.server_url if url is None else url)
        try:
            self.wait_for_element_by_css_selector(
                self.dash_entry_locator, timeout=timeout
            )
        except TimeoutException:
            logger.exception("dash server is not loaded within %s seconds", timeout)
            logger.debug(self.get_logs())
            raise DashAppLoadingError(
                "the expected Dash react entry point cannot be loaded"
                " in browser\n HTML => {}\n Console Logs => {}\n".format(
                    self.driver.find_element_by_tag_name("body").get_property(
                        "innerHTML"
                    ),
                    "\n".join((str(log) for log in self.get_logs())),
                )
            )

        if self._pause:
            try:
                import pdb as pdb_  # pylint: disable=import-outside-toplevel
            except ImportError:
                import ipdb as pdb_  # pylint: disable=import-outside-toplevel

            pdb_.set_trace()

    def select_dcc_dropdown(self, elem_or_selector, value=None, index=None):
        dropdown = self._get_element(elem_or_selector)
        dropdown.click()

        menu = dropdown.find_element_by_css_selector("div.Select-menu-outer")
        logger.debug("the available options are %s", "|".join(menu.text.split("\n")))

        options = menu.find_elements_by_css_selector("div.VirtualizedSelectOption")
        if options:
            if isinstance(index, int):
                options[index].click()
                return

            for option in options:
                if option.text == value:
                    option.click()
                    return

        logger.error(
            "cannot find matching option using value=%s or index=%s", value, index
        )

    def toggle_window(self):
        """Switch between the current working window and the new opened one."""
        idx = (self._window_idx + 1) % 2
        self.switch_window(idx=idx)
        self._window_idx += 1

    def switch_window(self, idx=0):
        """Switch to window by window index shortcut to
        `driver.switch_to.window`."""
        if len(self.driver.window_handles) <= idx:
            raise BrowserError("there is no second window in Browser")

        self.driver.switch_to.window(self.driver.window_handles[idx])

    def open_new_tab(self, url=None):
        """Open a new tab in browser url is not set, equals to `server_url`."""
        self.driver.execute_script(
            'window.open("{}", "new window")'.format(
                self.server_url if url is None else url
            )
        )

    def get_webdriver(self):
        try:
            return getattr(self, "_get_{}".format(self._browser))()
        except WebDriverException:
            logger.exception("<<<Webdriver not initialized correctly>>>")
            return None

    def _get_wd_options(self):
        options = (
            self._options[0]
            if self._options and isinstance(self._options, list)
            else getattr(webdriver, self._browser).options.Options()
        )

        if self._headless:
            options.headless = True

        return options

    def _get_chrome(self):
        options = self._get_wd_options()

        capabilities = DesiredCapabilities.CHROME
        capabilities["loggingPrefs"] = {"browser": "SEVERE"}
        capabilities["goog:loggingPrefs"] = {"browser": "SEVERE"}

        if "DASH_TEST_CHROMEPATH" in os.environ:
            options.binary_location = os.environ["DASH_TEST_CHROMEPATH"]

        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self.download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
            },
        )

        chrome = (
            webdriver.Remote(
                command_executor=self._remote_url,
                options=options,
                desired_capabilities=capabilities,
            )
            if self._remote
            else webdriver.Chrome(options=options, desired_capabilities=capabilities)
        )

        # https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        if self._headless:
            # pylint: disable=protected-access
            chrome.command_executor._commands["send_command"] = (
                "POST",
                "/session/$sessionId/chromium/send_command",
            )
            params = {
                "cmd": "Page.setDownloadBehavior",
                "params": {"behavior": "allow", "downloadPath": self.download_path},
            }
            res = chrome.execute("send_command", params)
            logger.debug("enabled headless download returns %s", res)

        chrome.set_window_position(0, 0)
        return chrome

    def _get_firefox(self):
        options = self._get_wd_options()

        capabilities = DesiredCapabilities.FIREFOX
        capabilities["loggingPrefs"] = {"browser": "SEVERE"}
        capabilities["marionette"] = True

        # https://developer.mozilla.org/en-US/docs/Download_Manager_preferences
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.dir", self.download_path)
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/octet-stream",  # this MIME is generic for binary
        )
        return (
            webdriver.Remote(
                command_executor=self._remote_url,
                options=options,
                desired_capabilities=capabilities,
            )
            if self._remote
            else webdriver.Firefox(
                firefox_profile=fp, options=options, capabilities=capabilities
            )
        )

    @staticmethod
    def _is_windows():
        return sys.platform == "win32"

    def multiple_click(self, elem_or_selector, clicks):
        """multiple_click click the element with number of `clicks`."""
        for _ in range(clicks):
            self._get_element(elem_or_selector).click()

    def clear_input(self, elem_or_selector):
        """Simulate key press to clear the input."""
        elem = self._get_element(elem_or_selector)
        logger.debug("clear input with %s => %s", elem_or_selector, elem)
        (
            ActionChains(self.driver)
            .move_to_element(elem)
            .pause(0.2)
            .click(elem)
            .send_keys(Keys.END)
            .key_down(Keys.SHIFT)
            .send_keys(Keys.HOME)
            .key_up(Keys.SHIFT)
            .send_keys(Keys.DELETE)
        ).perform()

    def zoom_in_graph_by_ratio(
        self, elem_or_selector, start_fraction=0.5, zoom_box_fraction=0.2, compare=True
    ):
        """Zoom out a graph with a zoom box fraction of component dimension
        default start at middle with a rectangle of 1/5 of the dimension use
        `compare` to control if we check the svg get changed."""
        elem = self._get_element(elem_or_selector)

        prev = elem.get_attribute("innerHTML")
        w, h = elem.size["width"], elem.size["height"]
        try:
            ActionChains(self.driver).move_to_element_with_offset(
                elem, w * start_fraction, h * start_fraction
            ).drag_and_drop_by_offset(
                elem, w * zoom_box_fraction, h * zoom_box_fraction
            ).perform()
        except MoveTargetOutOfBoundsException:
            logger.exception("graph offset outside of the boundary")
        if compare:
            assert prev != elem.get_attribute(
                "innerHTML"
            ), "SVG content should be different after zoom"

    def click_at_coord_fractions(self, elem_or_selector, fx, fy):
        elem = self._get_element(elem_or_selector)

        ActionChains(self.driver).move_to_element_with_offset(
            elem, elem.size["width"] * fx, elem.size["height"] * fy
        ).click().perform()

    def get_logs(self):
        """Return a list of `SEVERE` level logs after last reset time stamps
        (default to 0, resettable by `reset_log_timestamp`.

        Chrome only
        """
        if self.driver.name.lower() == "chrome":
            return [
                entry
                for entry in self.driver.get_log("browser")
                if entry["timestamp"] > self._last_ts
            ]
        warnings.warn("get_logs always return None with webdrivers other than Chrome")
        return None

    def reset_log_timestamp(self):
        """reset_log_timestamp only work with chrome webdriver."""
        if self.driver.name.lower() == "chrome":
            entries = self.driver.get_log("browser")
            if entries:
                self._last_ts = entries[-1]["timestamp"]

    @property
    def driver(self):
        """Expose the selenium webdriver as fixture property."""
        return self._driver

    @property
    def session_id(self):
        return self.driver.session_id

    @property
    def server_url(self):
        return self._url

    @server_url.setter
    def server_url(self, value):
        """Set the server url so the selenium is aware of the local server
        port.

        It also implicitly calls `wait_for_page`.
        """
        self._url = value
        self.wait_for_page()

    @property
    def download_path(self):
        return self._download_path
