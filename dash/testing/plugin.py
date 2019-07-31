# pylint: disable=missing-docstring,redefined-outer-name
import warnings

try:
    import pytest

    from dash.testing.application_runners import (
        ThreadedRunner,
        ProcessRunner,
        RRunner,
    )
    from dash.testing.browser import Browser
    from dash.testing.composite import DashComposite, DashRComposite
except ImportError:
    warnings.warn("run `pip install dash[testing]` if you need dash.testing")

WEBDRIVERS = {"Chrome", "Firefox", "Remote"}


def pytest_addoption(parser):
    # Add options to the pytest parser, either on the commandline or ini
    # TODO add more options for the selenium driver.
    dash = parser.getgroup("Dash", "Dash Integration Tests")

    dash.addoption(
        "--webdriver",
        choices=tuple(WEBDRIVERS),
        default="Chrome",
        help="Name of the selenium driver to use",
    )

    dash.addoption(
        "--headless",
        action="store_true",
        help="set this flag to run in headless mode",
    )

    dash.addoption(
        "--nopercyfinalize",
        action="store_false",
        help="set this flag to control percy finalize at CI level",
    )


@pytest.mark.tryfirst
def pytest_addhooks(pluginmanager):
    # https://github.com/pytest-dev/pytest-xdist/blob/974bd566c599dc6a9ea291838c6f226197208b46/xdist/plugin.py#L67
    # avoid warnings with pytest-2.8
    from dash.testing import newhooks

    method = getattr(pluginmanager, "add_hookspecs", None)
    if method is None:
        method = pluginmanager.addhooks  # pragma: no cover
    method(newhooks)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.failed:
        for name, fixture in item.funcargs.items():
            try:
                if name in {"dash_duo", "dash_br", "dashr"}:
                    fixture.take_snapshot(item.name)
            except Exception as e:  # pylint: disable=broad-except
                print(e)


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def dash_thread_server():
    """Start a local dash server in a new thread"""
    with ThreadedRunner() as starter:
        yield starter


@pytest.fixture
def dash_process_server():
    """Start a Dash server with subprocess.Popen and waitress-serve"""
    with ProcessRunner() as starter:
        yield starter


@pytest.fixture
def dashr_server():
    with RRunner() as starter:
        yield starter


@pytest.fixture
def dash_br(request, tmpdir):
    with Browser(
        browser=request.config.getoption("webdriver"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_finalize=request.config.getoption("nopercyfinalize"),
    ) as browser:
        yield browser


@pytest.fixture
def dash_duo(request, dash_thread_server, tmpdir):
    with DashComposite(
        dash_thread_server,
        browser=request.config.getoption("webdriver"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_finalize=request.config.getoption("nopercyfinalize"),
    ) as dc:
        yield dc


@pytest.fixture
def dashr(request, dashr_server, tmpdir):
    with DashRComposite(
        dashr_server,
        browser=request.config.getoption("webdriver"),
        headless=request.config.getoption("headless"),
        options=request.config.hook.pytest_setup_options(),
        download_path=tmpdir.mkdir("download").strpath,
        percy_finalize=request.config.getoption("nopercyfinalize"),
    ) as dc:
        yield dc
