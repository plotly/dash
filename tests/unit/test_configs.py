"""Tests for Dash application configuration and path handling.

This module contains test cases that verify the behavior of the application
configuration, environment variable handling, pathname prefixing, and URL path utilities.
The pytest tests cover scenarios such as valid and invalid configurations,
environment variable overrides, and path manipulation functions used in the application.
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
    Tests that DASH_ENV_VARS are None by default without OS environment settings.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
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
    Tests valid pathname prefix configurations.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        route_prefix: Routes pathname prefix to test.
        req_prefix: Requests pathname prefix to test.
        expected_route: Expected routes pathname result.
        expected_req: Expected requests pathname result.
    """
    _, routes, req = pathname_configs(
        routes_pathname_prefix=route_prefix, requests_pathname_prefix=req_prefix
    )

    if expected_route is not None:
        assert routes == expected_route
    assert req == expected_req


def test_invalid_pathname_prefix(empty_environ):
    """
    Tests invalid pathname prefix configurations raise appropriate exceptions.
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
    Tests pathname prefix derivation from DASH_APP_NAME environment variable.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    os.environ["DASH_APP_NAME"] = "my-dash-app"
    _, routes, req = pathname_configs()
    assert req == "/my-dash-app/"
    assert routes == "/"


def test_pathname_prefix_environ_routes(empty_environ):
    """
    Tests routes prefix from DASH_ROUTES_PATHNAME_PREFIX environment variable.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
    """
    os.environ["DASH_ROUTES_PATHNAME_PREFIX"] = "/routes/"
    _, routes, _ = pathname_configs()
    assert routes == "/routes/"


def test_pathname_prefix_environ_requests(empty_environ):
    """
    Tests requests prefix from DASH_REQUESTS_PATHNAME_PREFIX environment variable.
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
    Tests asset URL generation with different request prefixes.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        req: Request pathname prefix to test.
        expected: Expected asset URL result.
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
    Tests asset URL generation with various configuration combinations.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        requests_pathname_prefix: Request pathname prefix to test.
        assets_external_path: External assets path to test.
        assets_url_path: Assets URL path to test.
        expected: Expected asset URL result.
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
    Tests relative path generation with request prefix.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        requests_pathname_prefix: Request pathname prefix to test.
        expected: Expected relative path result.
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
    Tests stripping of relative path with request prefix.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        requests_pathname_prefix: Request pathname prefix to test.
        expected: Expected stripped path result.
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
    Tests dev tools UI configuration priority and defaults.
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
    Tests props check configuration priority and defaults.
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
    Tests that environment variable loading reflects OS environment changes.
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
    Tests application name assignment with different server configurations.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        name: Application name to test.
        server: Server configuration to test.
        expected: Expected application name result.
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
    Tests relative URL generation with different prefixes.
    Args:
        prefix: Pathname prefix to test.
        partial_path: Partial path to append.
        expected: Expected full path result.
    """
    path = app_get_relative_path(prefix, partial_path)
    assert path == expected


@pytest.mark.parametrize(
    "prefix, partial_path",
    [("/", "relative-page-1"), ("/my-dash-app/", "relative-page-1")],
)
def test_invalid_get_relative_path(prefix, partial_path):
    """
    Tests invalid relative path handling raises appropriate exception.
    Args:
        prefix: Pathname prefix to test.
        partial_path: Invalid partial path to test.
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
    Tests stripping of relative paths with different prefixes.
    Args:
        prefix: Pathname prefix to test.
        partial_path: Full path to strip.
        expected: Expected stripped path result.
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
    Tests invalid path stripping raises appropriate exception.
    Args:
        prefix: Pathname prefix to test.
        partial_path: Invalid path to test.
    """
    with pytest.raises(_exc.UnsupportedRelativePath):
        app_strip_relative_path(prefix, partial_path)


def test_port_env_fail_str(empty_environ):
    """
    Tests invalid port string raises appropriate exception.
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
    Tests out-of-range port values raise appropriate exception.
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
    Tests successful app run without proxy configuration.
    Args:
        mocker: Pytest fixture for mocking.
        caplog: Pytest fixture for capturing log output.
        empty_environ: Pytest fixture providing a clean environment.
        setlevel_warning: Whether to set logging level to WARNING.
    """
    app = Dash()

    if setlevel_warning:
        app.logger.setLevel(logging.WARNING)

    # mock out the run method so we don't actually start listening forever
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
    Tests successful app run with various proxy configurations.
    Args:
        mocker: Pytest fixture for mocking.
        caplog: Pytest fixture for capturing log output.
        empty_environ: Pytest fixture providing a clean environment.
        proxy: Proxy URL to test.
        host: Host address to test.
        port: Port number to test.
        path: URL path to test.
    """
    proxystr = "http://{}:{}::{}".format(host, port, proxy)
    app = Dash(url_base_pathname=path)
    mocker.patch.object(app.server, "run")

    app.run(proxy=proxystr, host=host, port=port)

    assert "Dash is running on {}{}\n".format(proxy, path) in caplog.text


def test_proxy_failure(mocker, empty_environ):
    """
    Tests proxy configuration failures raise appropriate exceptions.
    Args:
        mocker: Pytest fixture for mocking.
        empty_environ: Pytest fixture providing a clean environment.
    """
    app = Dash()

    # if the tests work we'll never get to server.run, but keep the mock
    # in case something is amiss and we don't get an exception.
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
    Tests application title configuration and rendering.
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
    Tests delayed application configuration functionality.
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
    Tests invalid delayed configuration raises appropriate exception.
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
    Tests debug mode configuration during run.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        debug_env: Debug environment variable setting to test.
        debug: Debug parameter to test.
        expected: Expected debug mode result.
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
    Tests debug mode configuration with dev tools enablement.
    Args:
        empty_environ: Pytest fixture providing a clean environment.
        debug_env: Debug environment variable setting to test.
        debug: Debug parameter to test.
        expected: Expected debug mode result.
    """
    if debug_env:
        os.environ["DASH_DEBUG"] = debug_env
    app = Dash()
    app.enable_dev_tools(debug=debug)
    assert app._dev_tools.ui == expected


def test_missing_flask_compress_raises():
    """
    Tests missing Flask-Compress dependency raises ImportError.
    Args:
        None
    """
    with pytest.raises(ImportError):
        Dash(compress=True)
