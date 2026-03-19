# pylint: disable=missing-docstring,redefined-outer-name
from typing import Any

import pytest
from .consts import SELENIUM_GRID_DEFAULT


# pylint: disable=too-few-public-methods
class MissingDashTesting:
    def __init__(self, **kwargs):
        raise Exception(
            "dash[testing] was not installed. "
            "Please install to use the dash testing fixtures."
        )

    def __enter__(self) -> Any:
        """Implemented to satisfy type checking."""

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Implemented to satisfy type checking."""

        return False


try:
    from dash.testing.application_runners import (
        ThreadedRunner,
        ProcessRunner,
        RRunner,
        JuliaRunner,
        MultiProcessRunner,
    )
    from dash.testing.browser import Browser
    from dash.testing.composite import DashComposite, DashRComposite, DashJuliaComposite
    from dash.testing.errors import DashAppLoadingError

    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import (
        TimeoutException,
        StaleElementReferenceException,
    )

    # pylint: disable=unused-import
    import dash_testing_stub  # noqa: F401

    _installed = True
except ImportError:
    # Running pytest without dash[testing] installed.
    ThreadedRunner = MissingDashTesting
    ProcessRunner = MissingDashTesting
    MultiProcessRunner = MissingDashTesting
    RRunner = MissingDashTesting
    JuliaRunner = MissingDashTesting
    Browser = MissingDashTesting
    DashComposite = MissingDashTesting
    DashRComposite = MissingDashTesting
    DashJuliaComposite = MissingDashTesting
    _installed = False


def pytest_addoption(parser):
    if not _installed:
        return

    dash = parser.getgroup("Dash", "Dash Integration Tests")

    dash.addoption(
        "--webdriver",
        choices=("Chrome", "Firefox"),
        default="Chrome",
        help="Name of the selenium driver to use",
    )

    dash.addoption(
        "--remote", action="store_true", help="instruct pytest to use selenium grid"
    )

    dash.addoption(
        "--remote-url",
        action="store",
        default=SELENIUM_GRID_DEFAULT,
        help="set a different selenium grid remote url if other than default",
    )

    dash.addoption(
        "--headless", action="store_true", help="set this flag to run in headless mode"
    )

    dash.addoption(
        "--percy-assets",
        action="store",
        default="tests/assets",
        help="configure how Percy will discover your app's assets",
    )

    dash.addoption(
        "--nopercyfinalize",
        action="store_false",
        help="set this flag to control percy finalize at CI level",
    )

    dash.addoption(
        "--pause",
        action="store_true",
        help="pause using pdb after opening the test app, so you can interact with it",
    )


@pytest.mark.tryfirst
def pytest_addhooks(pluginmanager):
    if not _installed:
        return
    # https://github.com/pytest-dev/pytest-xdist/blob/974bd566c599dc6a9ea291838c6f226197208b46/xdist/plugin.py#L67
    # avoid warnings with pytest-2.8
    from dash.testing import newhooks  # pylint: disable=import-outside-toplevel

    method = getattr(pluginmanager, "add_hookspecs", None)
    if method is None:
        method = pluginmanager.addhooks  # pragma: no cover
    method(newhooks)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    # execute all other hooks to obtain the report object
    outcome = yield
    if not _installed:
        return
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.failed and hasattr(item, "funcargs"):
        for name, fixture in item.funcargs.items():
            try:
                if name in {"dash_duo", "dash_br", "dashr", "dashjl"}:
                    fixture.take_snapshot(item.name)
            except Exception as e:  # pylint: disable=broad-except
                print(e)


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def dash_thread_server() -> ThreadedRunner:  # type: ignore[reportInvalidTypeForm]
    """Start a local dash server in a new thread."""
    with ThreadedRunner() as starter:
        yield starter


@pytest.fixture
def dash_process_server() -> ProcessRunner:  # type: ignore[reportInvalidTypeForm]
    """Start a Dash server with subprocess.Popen and waitress-serve."""
    with ProcessRunner() as starter:
        yield starter


@pytest.fixture
def dash_multi_process_server() -> MultiProcessRunner:  # type: ignore[reportInvalidTypeForm]
    with MultiProcessRunner() as starter:
        yield starter


@pytest.fixture
def dashr_server() -> RRunner:  # type: ignore[reportInvalidTypeForm]
    with RRunner() as starter:
        yield starter


@pytest.fixture
def dashjl_server() -> JuliaRunner:  # type: ignore[reportInvalidTypeForm]
    with JuliaRunner() as starter:
        yield starter


@pytest.fixture
def dash_br(request, tmpdir) -> Browser:  # type: ignore[reportInvalidTypeForm]
    with Browser(
        browser=request.config.getoption("webdriver"),
        remote=request.config.getoption("remote"),
        remote_url=request.config.getoption("remote_url"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_assets_root=request.config.getoption("percy_assets"),
        percy_finalize=request.config.getoption("nopercyfinalize"),
        pause=request.config.getoption("pause"),
    ) as browser:
        yield browser


@pytest.fixture(scope="session")
def _dash_browser_session(request, tmp_path_factory):
    """Session-scoped browser instance, reused across all tests."""
    if not _installed:
        yield None
        return

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


class _ReusableDashComposite(DashComposite):
    """DashComposite that reuses an existing browser instance."""

    # pylint: disable=super-init-not-called
    def __init__(self, server, browser_instance, **kwargs):
        # Skip Browser.__init__, just set up the server
        self.server = server
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

    def _reset_browser_state(self):
        """Clear browser state between tests."""
        try:
            # Stop any running JavaScript
            self.driver.execute_script("window.stop();")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        try:
            self.driver.delete_all_cookies()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        try:
            # Navigate to blank page
            self.driver.get("about:blank")

            # Wait for navigation to complete
            WebDriverWait(self.driver, 2).until(EC.url_to_be("about:blank"))

            # Clear storage
            self.clear_storage()

            # Reset log timestamp to filter out logs from previous tests
            self.reset_log_timestamp()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def _ensure_blank_page(self):
        """Ensure browser is on a blank page with no stale content."""
        try:
            current_url = self.driver.current_url
            if current_url != "about:blank":
                self.driver.get("about:blank")
            # Wait for blank page to fully load
            WebDriverWait(self.driver, 2).until(EC.url_to_be("about:blank"))
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def start_server(self, app, navigate=True, **kwargs):
        """Start the local server with app."""
        # Ensure browser is on blank page before starting new server
        self._ensure_blank_page()
        self.clear_logs()
        self.server(app, **kwargs)
        if navigate:
            self.server_url = self.server.url

    def wait_for_page(self, url=None, timeout=10):
        """Wait for page to load with improved synchronization."""
        target_url = self.server_url if url is None else url

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
                    elem = driver.find_element(By.CSS_SELECTOR, self.dash_entry_locator)
                    # Verify element is interactive (not stale)
                    _ = elem.is_displayed()
                    return elem
                except StaleElementReferenceException:
                    return False

            WebDriverWait(self.driver, timeout).until(fresh_react_entry)

        except TimeoutException as exc:
            raise DashAppLoadingError("Dash app failed to load") from exc

    def __enter__(self):
        self._reset_browser_state()
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # Don't quit the browser - it's shared
        pass


@pytest.fixture
# pylint: disable=unused-argument
def dash_duo(request, dash_thread_server, _dash_browser_session) -> DashComposite:  # type: ignore[reportInvalidTypeForm]
    """Dash test fixture with reusable browser (session-scoped)."""
    with _ReusableDashComposite(
        server=dash_thread_server,
        browser_instance=_dash_browser_session,
    ) as dc:
        yield dc


@pytest.fixture
def dash_duo_fresh_browser(request, dash_thread_server, tmpdir) -> DashComposite:  # type: ignore[reportInvalidTypeForm]
    """Dash test fixture with a fresh browser instance (for tests that need isolation)."""
    with DashComposite(
        server=dash_thread_server,
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
def dash_duo_mp(request, dash_multi_process_server, tmpdir) -> DashComposite:  # type: ignore[reportInvalidTypeForm]
    with DashComposite(
        server=dash_multi_process_server,
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
def dashr(request, dashr_server, tmpdir) -> DashRComposite:  # type: ignore[reportInvalidTypeForm]
    with DashRComposite(
        server=dashr_server,
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
def dashjl(request, dashjl_server, tmpdir) -> DashJuliaComposite:  # type: ignore[reportInvalidTypeForm]
    with DashJuliaComposite(
        server=dashjl_server,
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
def diskcache_manager():
    from dash.background_callback import (  # pylint: disable=import-outside-toplevel
        DiskcacheManager,
    )

    return DiskcacheManager()
