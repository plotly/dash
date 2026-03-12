import pytest
from dash_core_components_page import DashCoreComponentsMixin
from dash.testing.browser import Browser


class DashCoreComponentsComposite(Browser, DashCoreComponentsMixin):
    def __init__(self, server, **kwargs):
        super(DashCoreComponentsComposite, self).__init__(**kwargs)
        self.server = server

    def start_server(self, app, **kwargs):
        """start the local server with app"""

        # start server with app and pass Dash arguments
        self.server(app, **kwargs)

        # set the default server_url, it implicitly call wait_for_page
        self.server_url = self.server.url


class _ReusableDashCoreComponentsComposite(DashCoreComponentsMixin):
    """DCC composite that reuses an existing browser instance."""

    def __init__(self, server, browser_instance):
        self.server = server
        self._browser_instance = browser_instance
        self._driver = browser_instance._driver
        self._browser = browser_instance._browser
        self._headless = browser_instance._headless
        self._wait_timeout = browser_instance._wait_timeout
        self._percy_run = browser_instance._percy_run
        self._percy_finalize = browser_instance._percy_finalize
        self._pause = browser_instance._pause
        self._wd_wait = browser_instance._wd_wait
        self._download_path = browser_instance._download_path
        self._last_ts = 0
        self._url = ""
        self._window_idx = 0

    def __getattr__(self, name):
        # Delegate any missing attributes/methods to the browser instance
        return getattr(self._browser_instance, name)

    @property
    def driver(self):
        return self._driver

    @property
    def wait_timeout(self):
        return self._wait_timeout

    def start_server(self, app, **kwargs):
        """start the local server with app"""
        # Ensure browser is on blank page before starting new server
        self._ensure_blank_page()
        self.server(app, **kwargs)
        self.server_url = self.server.url

    def _ensure_blank_page(self):
        """Ensure browser is on a blank page with no stale content."""
        try:
            current_url = self.driver.current_url
            if current_url != "about:blank":
                self.driver.get("about:blank")
            # Wait for blank page to fully load
            from selenium.webdriver.support.wait import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            WebDriverWait(self.driver, 2).until(EC.url_to_be("about:blank"))
        except Exception:
            pass

    @property
    def server_url(self):
        return self._url

    @server_url.setter
    def server_url(self, value):
        self._url = value
        self.wait_for_page()

    def wait_for_page(self, url=None, timeout=10):
        from selenium.common.exceptions import (
            TimeoutException,
            StaleElementReferenceException,
        )
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.common.by import By
        from dash.testing.errors import DashAppLoadingError

        target_url = self._url if url is None else url

        # Navigate to the target URL
        self.driver.get(target_url)

        try:
            # Wait for URL to match (handles redirects)
            WebDriverWait(self.driver, timeout).until(
                lambda d: target_url in d.current_url
            )

            # Wait for react entry point with staleness check
            def fresh_react_entry(driver):
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, "#react-entry-point")
                    # Verify element is interactive (not stale)
                    _ = elem.is_displayed()
                    return elem
                except StaleElementReferenceException:
                    return False

            WebDriverWait(self.driver, timeout).until(fresh_react_entry)

        except TimeoutException as exc:
            raise DashAppLoadingError("Dash app failed to load") from exc

    def wait_for_element_by_css_selector(self, selector, timeout=None):
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        wait = WebDriverWait(self.driver, timeout or self._wait_timeout)
        return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

    def wait_for_element_by_id(self, element_id, timeout=None):
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By

        wait = WebDriverWait(self.driver, timeout or self._wait_timeout)
        return wait.until(EC.presence_of_element_located((By.ID, element_id)))

    def find_element(self, selector, attribute="CSS_SELECTOR"):
        from selenium.webdriver.common.by import By

        return self.driver.find_element(getattr(By, attribute.upper()), selector)

    def find_elements(self, selector, attribute="CSS_SELECTOR"):
        from selenium.webdriver.common.by import By

        return self.driver.find_elements(getattr(By, attribute.upper()), selector)

    def wait_for_element(self, selector, timeout=None):
        return self.wait_for_element_by_css_selector(selector, timeout)

    def wait_for_text_to_equal(self, selector, text, timeout=None):
        from dash.testing.wait import text_to_equal

        return self._wait_for(
            text_to_equal(selector, text, timeout or self._wait_timeout), timeout
        )

    def _wait_for(self, method, timeout):
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.common.exceptions import TimeoutException

        wait = WebDriverWait(self.driver, timeout or self._wait_timeout)
        try:
            return wait.until(method)
        except TimeoutException:
            raise

    def wait_for_style_to_equal(self, selector, style, val, timeout=None):
        from dash.testing.wait import style_to_equal

        return self._wait_for(style_to_equal(selector, style, val), timeout)

    def percy_snapshot(
        self, name="", wait_for_callbacks=False, convert_canvases=False, widths=None
    ):
        # Delegate to browser instance's percy_snapshot
        self._browser_instance.percy_snapshot(
            name, wait_for_callbacks, convert_canvases, widths
        )

    def clear_input(self, elem_or_selector):
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains

        elem = (
            self.find_element(elem_or_selector)
            if isinstance(elem_or_selector, str)
            else elem_or_selector
        )
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

    def clear_storage(self):
        self.driver.execute_script("window.localStorage.clear()")
        self.driver.execute_script("window.sessionStorage.clear()")

    def get_logs(self):
        if self._browser == "chrome":
            return [
                entry
                for entry in self.driver.get_log("browser")
                if entry["timestamp"] > self._last_ts
            ]
        return None

    def _reset_browser_state(self):
        """Clear browser state between tests."""
        try:
            # Stop any running JavaScript
            self.driver.execute_script("window.stop();")
        except Exception:
            pass

        try:
            self.driver.delete_all_cookies()
        except Exception:
            pass

        try:
            # Navigate to blank page
            self.driver.get("about:blank")

            # Wait for navigation to complete
            from selenium.webdriver.support.wait import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            WebDriverWait(self.driver, 2).until(EC.url_to_be("about:blank"))

            # Clear storage
            self.clear_storage()

            # Reset timestamp for log filtering
            self._last_ts = 0
        except Exception:
            pass

    def __enter__(self):
        self._reset_browser_state()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        pass


@pytest.fixture(scope="session")
def _dcc_browser_session(request, tmp_path_factory):
    """Session-scoped browser instance for DCC tests."""
    download_path = tmp_path_factory.mktemp("download")
    browser = Browser(
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=str(download_path),
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    )
    yield browser
    browser.__exit__(None, None, None)


@pytest.fixture
def dash_dcc(request, dash_thread_server, _dcc_browser_session):
    with _ReusableDashCoreComponentsComposite(
        dash_thread_server,
        browser_instance=_dcc_browser_session,
    ) as dc:
        yield dc


@pytest.fixture
def dash_dcc_fresh_browser(request, dash_thread_server, tmpdir):
    """DCC test fixture with a fresh browser instance (for tests that need isolation)."""
    with DashCoreComponentsComposite(
        dash_thread_server,
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as dc:
        yield dc


@pytest.fixture
def dash_dcc_headed(request, dash_thread_server, tmpdir):
    with DashCoreComponentsComposite(
        dash_thread_server,
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=False,
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as dc:
        yield dc
