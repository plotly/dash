# pylint: disable=missing-docstring
import pytest

from selenium import webdriver

from dash.testing.application_runners import ThreadedRunner, ProcessRunner
from dash.testing.browser import Browser

WEBDRIVERS = {
    "Chrome": webdriver.Chrome,
    "Firefox": webdriver.Firefox,
    "Remote": webdriver.Remote,
}


# pylint: disable=missing-docstring
def pytest_addoption(parser):

    # Add options to the pytest parser, either on the commandline or ini
    # TODO add more options for the selenium driver.
    dash = parser.getgroup("Dash", "Dash Integration Tests")

    dash.addoption(
        "-w",
        "--webdriver",
        choices=tuple(WEBDRIVERS.keys()),
        default="Chrome",
        help="Name of the selenium driver to use",
    )

###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def thread_server():
    """Start a local dash server in a new thread"""
    with ThreadedRunner() as starter:
        yield starter


@pytest.fixture
def process_server():
    """Start a Dash server with subprocess.Popen and waitress-serve"""
    with ProcessRunner() as starter:
        yield starter


@pytest.fixture
def br(request):
    with Browser(request.config.getoption("webdriver")) as browser:
        yield browser
