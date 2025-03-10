"""Tests for Dash application configuration and path handling.

This module contains pytest test cases that verify the behavior of Dash application
configuration, environment variable handling, pathname prefixing, and URL path utilities.
The tests cover various scenarios including valid and invalid configurations,
environment variable overrides, and path manipulation functions used in Dash applications.
"""

import os
import logging

import pytest
from flask import Flask

from dash import Dash, exceptions as _exc

# noinspection PyProtectedMember
from dash._configs import (
    pathname_configs,
    DASH_ENV_VARS,
    get_combined_config,
    load_dash_env_vars,
)

from dash._utils import AttributeDict
from dash._get_paths import (
    app_get_asset_url,
    app_get_relative_path,
    app_strip_relative_path,
    get_asset_url,
    get_relative_path,
    strip_relative_path,
)


def test_dash_env_vars(empty_environ):
    """
    Tests that the DASH_ENV_VARS dictionary contains None values by default when no
    environment variables are set. This ensures that without explicit configuration,
    the application does not assume any default values for these variables.

    Args:
        empty_environ: Pytest fixture providing a clean environment with no pre-set variables.
    """
    assert {None} == {
        val for _, val in DASH_ENV_VARS.items()
    }, "initial var values are None without extra OS environ setting"


@pytest.mark.parametrize(
    "route_prefix, req_prefix, expected_route, expected_req",
    [
        (None, None, "/", "/"),
        ("/dash/", None, None, "/dash/"),
        (None, "/my-dash-app/", "/", "/my-dash-app/"),
        ("/dash/", "/my-dash-app/dash/", "/dash/", "/my-dash-app/dash/"),
    ],
)
def test_valid_pathname_prefix_init(
    empty_environ, route_prefix, req_prefix, expected_route, expected_req
):
    """
    Tests the pathname_configs function with valid combinations of route and request
    pathname prefixes. Verifies that the function correctly handles default values
    and returns the expected routes and requests pathname prefixes.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        route_prefix: The routes pathname prefix to test (e.g., "/dash/").
        req_prefix: The requests pathname prefix to test (e.g., "/my-dash-app/").
        expected_route: The expected routes pathname prefix result.
        expected_req: The expected requests pathname prefix result.
    """
    _, routes, req = pathname_configs(
        routes_pathname_prefix=route_prefix, requests_pathname_prefix=req_prefix
    )

    if expected_route is not None:
        assert routes == expected_route
    assert req == expected_req


def test_invalid_pathname_prefix(empty_environ):
    """
    Tests that the pathname_configs function raises InvalidConfig exceptions for
    invalid configurations, such as mismatched url_base_pathname and requests_pathname_prefix,
    or prefixes that do not start or end with a '/'.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    with pytest.raises(_exc.InvalidConfig, match="url_base_pathname"):
        _, _, _ = pathname_configs("/my-path", "/another-path")

    with pytest.raises(_exc.InvalidConfig) as excinfo:
        _, _, _ = pathname_configs(
            url_base_pathname="/invalid", routes_pathname_prefix="/invalid"
        )
    assert str(excinfo.value).split(".")[0].endswith("`routes_pathname_prefix`")

    with pytest.raises(_exc.InvalidConfig) as excinfo:
        _, _, _ = pathname_configs(
            url_base_pathname="/my-path", requests_pathname_prefix="/another-path"
        )
    assert str(excinfo.value).split(".")[0].endswith("`requests_pathname_prefix`")

    with pytest.raises(_exc.InvalidConfig, match="start with `/`"):
        _, _, _ = pathname_configs("my-path")

    with pytest.raises(_exc.InvalidConfig, match="end with `/`"):
        _, _, _ = pathname_configs("/my-path")


def test_pathname_prefix_from_environ_app_name(empty_environ):
    """
    Tests that when the DASH_APP_NAME environment variable is set, the requests_pathname_prefix
    is derived from it, and the routes_pathname_prefix defaults to '/'.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    os.environ["DASH_APP_NAME"] = "my-dash-app"
    _, routes, req = pathname_configs()
    assert req == "/my-dash-app/"
    assert routes == "/"


def test_pathname_prefix_environ_routes(empty_environ):
    """
    Tests that the routes_pathname_prefix is correctly set from the DASH_ROUTES_PATHNAME_PREFIX
    environment variable when provided.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    os.environ["DASH_ROUTES_PATHNAME_PREFIX"] = "/routes/"
    _, routes, _ = pathname_configs()
    assert routes == "/routes/"


def test_pathname_prefix_environ_requests(empty_environ):
    """
    Tests that the requests_pathname_prefix is correctly set from the DASH_REQUESTS_PATHNAME_PREFIX
    environment variable when provided.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    os.environ["DASH_REQUESTS_PATHNAME_PREFIX"] = "/requests/"
    _, _, req = pathname_configs()
    assert req == "/requests/"


@pytest.mark.parametrize(
    "req, expected",
    [
        ("/", "/assets/reset.css"),
        ("/requests/", "/requests/assets/reset.css"),
        ("/requests/routes/", "/requests/routes/assets/reset.css"),
    ],
)
def test_pathname_prefix_assets(empty_environ, req, expected):
    """
    Tests the app_get_asset_url function to ensure it correctly generates asset URLs
    by prepending the request pathname prefix to the asset path.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        req: The request pathname prefix to test (e.g., "/requests/").
        expected: The expected asset URL (e.g., "/requests/assets/reset.css").
    """
    config = AttributeDict(assets_external_path=req, assets_url_path="assets")
    path = app_get_asset_url(config, "reset.css")
    assert path == expected


@pytest.mark.parametrize(
    "requests_pathname_prefix, assets_external_path, assets_url_path, expected",
    [
        (None, None, "assets", "/assets/reset.css"),
        ("/app/", None, "assets", "/app/assets/reset.css"),
        (None, None, "css", "/css/reset.css"),
        ("/app/", None, "css", "/app/css/reset.css"),
        (
            None,
            "http://external.com/",
            "assets",
            "http://external.com/assets/reset.css",
        ),
        ("/app/", "http://external.com/", "css", "http://external.com/css/reset.css"),
    ],
)
def test_asset_url(
    empty_environ,
    requests_pathname_prefix,
    assets_external_path,
    assets_url_path,
    expected,
):
    """
    Tests the get_asset_url function with various combinations of requests_pathname_prefix,
    assets_external_path, and assets_url_path to ensure the correct asset URL is generated.
    This includes scenarios with and without external asset paths.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        requests_pathname_prefix: The request pathname prefix (e.g., "/app/").
        assets_external_path: External path for assets (e.g., "http://external.com/").
        assets_url_path: The asset URL path (e.g., "css").
        expected: The expected asset URL result.
    """
    app = Dash(
        "Dash",
        requests_pathname_prefix=requests_pathname_prefix,
        assets_external_path=assets_external_path,
        assets_url_path=assets_url_path,
    )

    app_path = app.get_asset_url("reset.css")
    dash_path = get_asset_url("reset.css")
    assert app_path == dash_path == expected


@pytest.mark.parametrize(
    "requests_pathname_prefix, expected",
    [
        (None, "/page2"),
        ("/app/", "/app/page2"),
    ],
)
def test_get_relative_path(
    empty_environ,
    requests_pathname_prefix,
    expected,
):
    """
    Tests the get_relative_path function to ensure it correctly prepends the requests_pathname_prefix
    to the given path, which is crucial for generating correct URLs in Dash applications.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        requests_pathname_prefix: The request pathname prefix (e.g., "/app/").
        expected: The expected relative path result (e.g., "/app/page2").
    """
    app = Dash(
        "Dash",
        requests_pathname_prefix=requests_pathname_prefix,
    )
    app_path = app.get_relative_path("/page2")
    dash_path = get_relative_path("/page2")
    assert app_path == dash_path == expected


@pytest.mark.parametrize(
    "requests_pathname_prefix, expected",
    [
        (None, "/app/page2"),
        ("/app/", "/page2"),
    ],
)
def test_strip_relative_path(
    empty_environ,
    requests_pathname_prefix,
    expected,
):
    """
    Tests the strip_relative_path function to ensure it correctly removes the requests_pathname_prefix
    from the given path, which is useful for internal path handling in Dash applications.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        requests_pathname_prefix: The request pathname prefix (e.g., "/app/").
        expected: The expected stripped path result (e.g., "/page2").
    """
    app = Dash(
        "Dash",
        requests_pathname_prefix=requests_pathname_prefix,
    )
    app_path = app.strip_relative_path("/app/page2")
    dash_path = strip_relative_path("/app/page2")
    assert app_path == dash_path == expected


def test_get_combined_config_dev_tools_ui(empty_environ):
    """
    Tests the get_combined_config function for the 'ui' configuration, verifying the priority
    order: init value > environment variable > default value. This ensures the correct configuration
    value is used based on the provided inputs and environment settings.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    val1 = get_combined_config("ui", None, default=False)
    assert (
        not val1
    ), "should return the default value if None is provided for init and environment"

    os.environ["DASH_UI"] = "true"
    val2 = get_combined_config("ui", None, default=False)
    assert val2, "should return the set environment value as True"

    val3 = get_combined_config("ui", False, default=True)
    assert not val3, "init value overrides the environment value"


def test_get_combined_config_props_check(empty_environ):
    """
    Tests the get_combined_config function for the 'props_check' configuration, verifying the
    priority order: init value > environment variable > default value. This ensures the correct
    configuration value is used for property checking in Dash components.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    val1 = get_combined_config("props_check", None, default=False)
    assert (
        not val1
    ), "should return the default value if None is provided for init and environment"

    os.environ["DASH_PROPS_CHECK"] = "true"
    val2 = get_combined_config("props_check", None, default=False)
    assert val2, "should return the set environment value as True"

    val3 = get_combined_config("props_check", False, default=True)
    assert not val3, "init value overrides the environment value"


def test_load_dash_env_vars_refects_to_os_environ(empty_environ):
    """
    Tests the load_dash_env_vars function to ensure it accurately reflects changes in the OS
    environment variables, updating the configuration values accordingly.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    for var in DASH_ENV_VARS.keys():
        os.environ[var] = "true"
        vars = load_dash_env_vars()
        assert vars[var] == "true"

        os.environ[var] = "false"
        vars = load_dash_env_vars()
        assert vars[var] == "false"


@pytest.mark.parametrize(
    "name, server, expected",
    [
        (None, True, "__main__"),
        ("test", True, "test"),
        ("test", False, "test"),
        (None, Flask("test"), "test"),
        ("test", Flask("other"), "test"),
    ],
)
def test_app_name_server(empty_environ, name, server, expected):
    """
    Tests the Dash application name assignment logic, verifying that the name is correctly set
    based on the provided name parameter and server configuration. This includes scenarios where
    the name is explicitly provided, inferred from the server, or defaults to '__main__'.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        name: The explicit name to set for the app, if provided.
        server: The server configuration (e.g., True, False, or a Flask instance).
        expected: The expected application name result.
    """
    app = Dash(name=name, server=server)
    assert app.config.name == expected


@pytest.mark.parametrize(
    "prefix, partial_path, expected",
    [
        ("/", "", "/"),
        ("/my-dash-app/", "", "/my-dash-app/"),
        ("/", "/", "/"),
        ("/my-dash-app/", "/", "/my-dash-app/"),
        ("/", "/page-1", "/page-1"),
        ("/my-dash-app/", "/page-1", "/my-dash-app/page-1"),
        ("/", "/page-1/", "/page-1/"),
        ("/my-dash-app/", "/page-1/", "/my-dash-app/page-1/"),
        ("/", "/page-1/sub-page-1", "/page-1/sub-page-1"),
        ("/my-dash-app/", "/page-1/sub-page-1", "/my-dash-app/page-1/sub-page-1"),
    ],
)
def test_pathname_prefix_relative_url(prefix, partial_path, expected):
    """
    Tests the app_get_relative_path function to ensure it correctly constructs relative URLs
    by combining the pathname prefix with the partial path, which is essential for routing in Dash.

    Args:
        prefix: The pathname prefix to prepend (e.g., "/my-dash-app/").
        partial_path: The partial path to append (e.g., "/page-1").
        expected: The expected full relative URL result.
    """
    path = app_get_relative_path(prefix, partial_path)
    assert path == expected


@pytest.mark.parametrize(
    "prefix, partial_path",
    [("/", "relative-page-1"), ("/my-dash-app/", "relative-page-1")],
)
def test_invalid_get_relative_path(prefix, partial_path):
    """
    Tests that the app_get_relative_path function raises an UnsupportedRelativePath exception
    when provided with a partial path that does not start with a '/', ensuring proper path validation.

    Args:
        prefix: The pathname prefix to test.
        partial_path: The invalid partial path to test (e.g., "relative-page-1").
    """
    with pytest.raises(_exc.UnsupportedRelativePath):
        app_get_relative_path(prefix, partial_path)


@pytest.mark.parametrize(
    "prefix, partial_path, expected",
    [
        ("/", None, None),
        ("/my-dash-app/", None, None),
        ("/", "/", ""),
        ("/my-dash-app/", "/my-dash-app", ""),
        ("/my-dash-app/", "/my-dash-app/", ""),
        ("/", "/page-1", "page-1"),
        ("/my-dash-app/", "/my-dash-app/page-1", "page-1"),
        ("/", "/page-1/", "page-1"),
        ("/my-dash-app/", "/my-dash-app/page-1/", "page-1"),
        ("/", "/page-1/sub-page-1", "page-1/sub-page-1"),
        ("/my-dash-app/", "/my-dash-app/page-1/sub-page-1", "page-1/sub-page-1"),
        ("/", "/page-1/sub-page-1/", "page-1/sub-page-1"),
        ("/my-dash-app/", "/my-dash-app/page-1/sub-page-1/", "page-1/sub-page-1"),
        ("/my-dash-app/", "/my-dash-app/my-dash-app/", "my-dash-app"),
        (
            "/my-dash-app/",
            "/my-dash-app/something-else/my-dash-app/",
            "something-else/my-dash-app",
        ),
    ],
)
def test_strip_relative_path(prefix, partial_path, expected):
    """
    Tests the app_strip_relative_path function to ensure it correctly removes the pathname prefix
    from the full path, returning the relative path component used internally by the application.

    Args:
        prefix: The pathname prefix to strip (e.g., "/my-dash-app/").
        partial_path: The full path to strip (e.g., "/my-dash-app/page-1").
        expected: The expected stripped path result (e.g., "page-1").
    """
    path = app_strip_relative_path(prefix, partial_path)
    assert path == expected


@pytest.mark.parametrize(
    "prefix, partial_path",
    [
        ("/", "relative-page-1"),
        ("/my-dash-app", "relative-page-1"),
        ("/my-dash-app", "/some-other-path"),
    ],
)
def test_invalid_strip_relative_path(prefix, partial_path):
    """
    Tests that the app_strip_relative_path function raises an UnsupportedRelativePath exception
    when the full path does not start with the expected pathname prefix, ensuring correct path handling.

    Args:
        prefix: The pathname prefix to test.
        partial_path: The invalid full path to test (e.g., "relative-page-1").
    """
    with pytest.raises(_exc.UnsupportedRelativePath):
        app_strip_relative_path(prefix, partial_path)


def test_port_env_fail_str(empty_environ):
    """
    Tests that providing a non-integer port value (e.g., 'garbage') to the app.run method
    raises a ValueError with a specific message, ensuring proper input validation.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    app = Dash()
    with pytest.raises(Exception) as excinfo:
        app.run(port="garbage")
    assert (
        excinfo.exconly()
        == "ValueError: Expecting an integer from 1 to 65535, found port='garbage'"
    )


def test_port_env_fail_range(empty_environ):
    """
    Tests that providing port values outside the valid range (1 to 65535) to the app.run method
    raises an AssertionError with a specific message, ensuring ports are within the acceptable range.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    app = Dash()
    with pytest.raises(Exception) as excinfo:
        app.run(port="0")
    assert (
        excinfo.exconly()
        == "AssertionError: Expecting an integer from 1 to 65535, found port=0"
    )

    with pytest.raises(Exception) as excinfo:
        app.run(port="65536")
    assert (
        excinfo.exconly()
        == "AssertionError: Expecting an integer from 1 to 65535, found port=65536"
    )


@pytest.mark.parametrize(
    "setlevel_warning",
    [False, True],
)
def test_no_proxy_success(mocker, caplog, empty_environ, setlevel_warning):
    """
    Tests that the Dash application can run successfully without a proxy configuration,
    verifying the correct startup message is logged unless the logging level is set to WARNING.

    Args:
        mocker: Pytest fixture for mocking objects.
        caplog: Pytest fixture for capturing log output.
        empty_environ: Pytest fixture providing a clean environment.
        setlevel_warning: Boolean indicating whether to set the logging level to WARNING.
    """
    app = Dash()

    if setlevel_warning:
        app.logger.setLevel(logging.WARNING)

    mocker.patch.object(app.server, "run")
    app.run(port=8787)

    STARTUP_MESSAGE = "Dash is running on http://127.0.0.1:8787/\n"
    if setlevel_warning:
        assert caplog.text is None or STARTUP_MESSAGE not in caplog.text
    else:
        assert STARTUP_MESSAGE in caplog.text


@pytest.mark.parametrize(
    "proxy, host, port, path",
    [
        ("https://daash.plot.ly", "127.0.0.1", 8050, "/"),
        ("https://daaash.plot.ly", "0.0.0.0", 8050, "/a/b/c/"),
        ("https://daaaash.plot.ly", "127.0.0.1", 1234, "/"),
        ("http://go.away", "127.0.0.1", 8050, "/now/"),
        ("http://my.server.tv:8765", "0.0.0.0", 80, "/"),
    ],
)
def test_proxy_success(mocker, caplog, empty_environ, proxy, host, port, path):
    """
    Tests that the Dash application can run successfully with various proxy configurations,
    ensuring the correct startup message reflecting the proxy URL and path is logged.

    Args:
        mocker: Pytest fixture for mocking objects.
        caplog: Pytest fixture for capturing log output.
        empty_environ: Pytest fixture providing a clean environment.
        proxy: The proxy URL to test (e.g., "https://daash.plot.ly").
        host: The host address (e.g., "127.0.0.1").
        port: The port number (e.g., 8050).
        path: The URL path (e.g., "/a/b/c/").
    """
    proxystr = "http://{}:{}::{}".format(host, port, proxy)
    app = Dash(url_base_pathname=path)
    mocker.patch.object(app.server, "run")

    app.run(proxy=proxystr, host=host, port=port)

    assert "Dash is running on {}{}\n".format(proxy, path) in caplog.text


def test_proxy_failure(mocker, empty_environ):
    """
    Tests that invalid proxy configurations, such as mismatched protocols, hosts, or ports,
    raise ProxyError exceptions with appropriate error messages.

    Args:
        mocker: Pytest fixture for mocking objects.
        empty_environ: Pytest fixture providing a clean environment.
    """
    app = Dash()
    mocker.patch.object(app.server, "run")

    with pytest.raises(_exc.ProxyError) as excinfo:
        app.run(
            proxy="https://127.0.0.1:8055::http://plot.ly", host="127.0.0.1", port=8055
        )
    assert "protocol: http is incompatible with the proxy" in excinfo.exconly()
    assert "you must use protocol: https" in excinfo.exconly()

    with pytest.raises(_exc.ProxyError) as excinfo:
        app.run(
            proxy="http://0.0.0.0:8055::http://plot.ly", host="127.0.0.1", port=8055
        )
    assert "host: 127.0.0.1 is incompatible with the proxy" in excinfo.exconly()
    assert "you must use host: 0.0.0.0" in excinfo.exconly()

    with pytest.raises(_exc.ProxyError) as excinfo:
        app.run(proxy="http://0.0.0.0:8155::http://plot.ly", host="0.0.0.0", port=8055)
    assert "port: 8055 is incompatible with the proxy" in excinfo.exconly()
    assert "you must use port: 8155" in excinfo.exconly()


def test_title():
    """
    Tests that the Dash application's title can be set via the constructor or property assignment,
    and that it is correctly rendered in the HTML index page.

    Args:
        None
    """
    app = Dash()
    assert "<title>Dash</title>" in app.index()
    app = Dash()
    app.title = "Hello World"
    assert "<title>Hello World</title>" in app.index()
    app = Dash(title="Custom Title")
    assert "<title>Custom Title</title>" in app.index()


def test_app_delayed_config():
    """
    Tests the delayed configuration of the Dash application by initializing it without a server
    and later attaching it to a Flask app with a specified requests_pathname_prefix.

    Args:
        None
    """
    app = Dash(server=False)
    app.init_app(app=Flask("test"), requests_pathname_prefix="/dash/")

    assert app.config.requests_pathname_prefix == "/dash/"

    with pytest.raises(AttributeError):
        app.config.name = "cannot update me"


def test_app_invalid_delayed_config():
    """
    Tests that attempting to set the application name after initialization raises an AttributeError,
    ensuring that certain configurations cannot be changed post-initialization.

    Args:
        None
    """
    app = Dash(server=False)
    with pytest.raises(AttributeError):
        app.init_app(app=Flask("test"), name="too late 2 update")


@pytest.mark.parametrize(
    "debug_env, debug, expected",
    [
        (None, None, False),
        (None, True, True),
        (None, False, False),
        ("True", None, True),
        ("True", True, True),
        ("True", False, False),
        ("False", None, False),
        ("False", True, True),
        ("False", False, False),
    ],
)
def test_debug_mode_run(empty_environ, debug_env, debug, expected):
    """
    Tests the debug mode configuration when running the Dash application, verifying how the
    debug parameter and DASH_DEBUG environment variable influence the dev_tools.ui setting.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        debug_env: The value of the DASH_DEBUG environment variable (e.g., "True").
        debug: The debug parameter passed to app.run (e.g., True).
        expected: The expected value of dev_tools.ui (True or False).
    """
    if debug_env:
        os.environ["DASH_DEBUG"] = debug_env
    app = Dash()
    with pytest.raises(AssertionError):
        app.run(debug=debug, port=-1)
    assert app._dev_tools.ui == expected


@pytest.mark.parametrize(
    "debug_env, debug, expected",
    [
        (None, None, True),
        (None, True, True),
        (None, False, False),
        ("True", None, True),
        ("True", True, True),
        ("True", False, False),
        ("False", None, False),
        ("False", True, True),
        ("False", False, False),
    ],
)
def test_debug_mode_enable_dev_tools(empty_environ, debug_env, debug, expected):
    """
    Tests the enable_dev_tools method of the Dash application, ensuring that the debug parameter
    and DASH_DEBUG environment variable correctly set the dev_tools.ui configuration.

    Args:
        empty_environ: Pytest fixture providing a clean environment.
        debug_env: The value of the DASH_DEBUG environment variable (e.g., "True").
        debug: The debug parameter passed to enable_dev_tools (e.g., True).
        expected: The expected value of dev_tools.ui (True or False).
    """
    if debug_env:
        os.environ["DASH_DEBUG"] = debug_env
    app = Dash()
    app.enable_dev_tools(debug=debug)
    assert app._dev_tools.ui == expected


def test_missing_flask_compress_raises():
    """
    Tests that attempting to enable compression in the Dash application without the Flask-Compress
    dependency installed raises an ImportError, ensuring proper dependency checks.

    Args:
        None
    """
    with pytest.raises(ImportError):
        Dash(compress=True)