import pytest

from selenium import webdriver

from dash.testing.application_runners import ThreadedRunner, ProcessRunner

WEBDRIVERS = {
    "Chrome": webdriver.Chrome,
    "Firefox": webdriver.Firefox,
    "Remote": webdriver.Remote,
}


def _get_config(config, key, default=None):
    opt = config.getoption(key)
    ini = config.getini(key)
    return opt or ini or default


###############################################################################
# Plugin hooks.
###############################################################################

# pylint: disable=missing-docstring
def pytest_addoption(parser):
    # Add options to the pytest parser, either on the commandline or ini
    # TODO add more options for the selenium driver.
    dash = parser.getgroup("Dash", "Dash Integration Tests")
    help_msg = "Name of the selenium driver to use"
    dash.addoption(
        "--webdriver", choices=tuple(WEBDRIVERS.keys()), help=help_msg
    )
    parser.addini("webdriver", help=help_msg)


###############################################################################
# Fixtures
###############################################################################


@pytest.fixture
def thread_server():
    """
    Start a local dash server in a new thread. Stop the server in teardown.
    :Example:
    .. code-block:: python
        import dash
        import dash_html_components as html
        def test_application(dash_threaded):
            app = dash.Dash(__name__)
            app.layout = html.Div('My app)
            dash_threaded(app)
    .. seealso:: :py:class:`pytest_dash.application_runners.DashThreaded`
    """

    with ThreadedRunner() as starter:
        yield starter


@pytest.fixture
def process_server():
    """
    Start a Dash server with subprocess.Popen and waitress-serve.
    :Example:
    .. code-block:: python
        def test_application(dash_subprocess):
            # consider the application file is named `app.py`
            dash_subprocess('app')
    .. seealso:: :py:class:`pytest_dash.application_runners.DashSubprocess`
    """
    with ProcessRunner() as starter:
        yield starter
