import os

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
from dash._utils import get_asset_path


@pytest.fixture
def empty_environ():
    for k in DASH_ENV_VARS.keys():
        if k in os.environ:
            os.environ.pop(k)


def test_dash_env_vars(empty_environ):
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
    _, routes, req = pathname_configs(
        routes_pathname_prefix=route_prefix,
        requests_pathname_prefix=req_prefix,
    )

    if expected_route is not None:
        assert routes == expected_route
    assert req == expected_req


def test_invalid_pathname_prefix(empty_environ):
    with pytest.raises(_exc.InvalidConfig, match="url_base_pathname"):
        _, _, _ = pathname_configs("/my-path", "/another-path")

    with pytest.raises(_exc.InvalidConfig) as excinfo:
        _, _, _ = pathname_configs(
            url_base_pathname="/invalid", routes_pathname_prefix="/invalid"
        )
    assert (
        str(excinfo.value).split(".")[0].endswith("`routes_pathname_prefix`")
    )

    with pytest.raises(_exc.InvalidConfig) as excinfo:
        _, _, _ = pathname_configs(
            url_base_pathname="/my-path",
            requests_pathname_prefix="/another-path",
        )
    assert (
        str(excinfo.value).split(".")[0].endswith("`requests_pathname_prefix`")
    )

    with pytest.raises(_exc.InvalidConfig, match="start with `/`"):
        _, _, _ = pathname_configs("my-path")

    with pytest.raises(_exc.InvalidConfig, match="end with `/`"):
        _, _, _ = pathname_configs("/my-path")


def test_pathname_prefix_from_environ_app_name(empty_environ):
    os.environ["DASH_APP_NAME"] = "my-dash-app"
    _, routes, req = pathname_configs()
    assert req == "/my-dash-app/"
    assert routes == "/"


def test_pathname_prefix_environ_routes(empty_environ):
    os.environ["DASH_ROUTES_PATHNAME_PREFIX"] = "/routes/"
    _, routes, _ = pathname_configs()
    assert routes == "/routes/"


def test_pathname_prefix_environ_requests(empty_environ):
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
    path = get_asset_path(req, "reset.css", "assets")
    assert path == expected


def test_get_combined_config_dev_tools_ui(empty_environ):
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
    app = Dash(name=name, server=server)
    assert app.config.name == expected
