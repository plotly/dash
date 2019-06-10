# pylint: disable=missing-docstring,redefined-outer-name
import pytest

from selenium import webdriver

from dash.testing.application_runners import ThreadedRunner, ProcessRunner
from dash.testing.browser import Browser
from dash.testing.composite import DashComposite

WEBDRIVERS = {
    "Chrome": webdriver.Chrome,
    "Firefox": webdriver.Firefox,
    "Remote": webdriver.Remote,
}


def pytest_addoption(parser):
    # Add options to the pytest parser, either on the commandline or ini
    # TODO add more options for the selenium driver.
    dash = parser.getgroup("Dash", "Dash Integration Tests")

    dash.addoption(
        "--webdriver",
        choices=tuple(WEBDRIVERS.keys()),
        default="Chrome",
        help="Name of the selenium driver to use",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # pylint: disable=unused-argument
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.failed:
        for name, fixture in item.funcargs.items():
            try:
                if name in {"dash_duo", "dash_br"}:
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
def dash_br(request):
    with Browser(request.config.getoption("webdriver")) as browser:
        yield browser


@pytest.fixture
def dash_duo(request, dash_thread_server):
    with DashComposite(
        dash_thread_server, request.config.getoption("webdriver")
    ) as dc:
        yield dc
