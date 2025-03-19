# pylint: disable=missing-docstring,redefined-outer-name
import pytest
from .consts import SELENIUM_GRID_DEFAULT


# pylint: disable=too-few-public-methods
class MissingDashTesting:
    def __init__(self, **kwargs):
        raise Exception(
            "dash[testing] was not installed. "
            "Please install to use the dash testing fixtures."
        )


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
def dash_thread_server() -> ThreadedRunner:
    """Start a local dash server in a new thread."""
    with ThreadedRunner() as starter:
        yield starter


@pytest.fixture
def dash_process_server() -> ProcessRunner:
    """Start a Dash server with subprocess.Popen and waitress-serve."""
    with ProcessRunner() as starter:
        yield starter


@pytest.fixture
def dash_multi_process_server() -> MultiProcessRunner:
    with MultiProcessRunner() as starter:
        yield starter


@pytest.fixture
def dashr_server() -> RRunner:
    with RRunner() as starter:
        yield starter


@pytest.fixture
def dashjl_server() -> JuliaRunner:
    with JuliaRunner() as starter:
        yield starter


@pytest.fixture
def dash_br(request, tmpdir) -> Browser:
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


@pytest.fixture
def dash_duo(request, dash_thread_server, tmpdir) -> DashComposite:
    with DashComposite(
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
def dash_duo_mp(request, dash_multi_process_server, tmpdir) -> DashComposite:
    with DashComposite(
        dash_multi_process_server,
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
def dashr(request, dashr_server, tmpdir) -> DashRComposite:
    with DashRComposite(
        dashr_server,
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
def dashjl(request, dashjl_server, tmpdir) -> DashJuliaComposite:
    with DashJuliaComposite(
        dashjl_server,
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
