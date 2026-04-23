"""MCP Streamable HTTP endpoint — transport-layer behavior.

Uses Flask's test_client to exercise POST/GET/DELETE at /_mcp,
session management, content-type handling, and route registration
driven by ``enable_mcp`` / ``DASH_MCP_ENABLED`` / ``routes_pathname_prefix``.
"""

import json
import os

from dash import Dash, Input, Output, html
from mcp.types import LATEST_PROTOCOL_VERSION

MCP_PATH = "_mcp"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(**kwargs):
    """Create a minimal Dash app with a layout and one callback."""
    app = Dash(__name__, **kwargs)
    app.layout = html.Div(
        [
            html.Div(id="my-input"),
            html.Div(id="my-output"),
        ]
    )

    @app.callback(Output("my-output", "children"), Input("my-input", "children"))
    def update_output(value):
        """Test callback docstring."""
        return f"echo: {value}"

    return app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_mcpe001_post_initialize_returns_protocol_version():
    app = _make_app()
    client = app.server.test_client()
    r = client.post(
        f"/{MCP_PATH}",
        data=json.dumps(
            {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
        ),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = json.loads(r.data)
    assert data["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION


def test_mcpe002_post_tools_list():
    app = _make_app()
    client = app.server.test_client()
    r = client.post(
        f"/{MCP_PATH}",
        data=json.dumps(
            {"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": {}}
        ),
        content_type="application/json",
    )
    assert r.status_code == 200
    data = json.loads(r.data)
    assert "result" in data
    assert "tools" in data["result"]


def test_mcpe003_notification_returns_202():
    app = _make_app()
    client = app.server.test_client()
    r = client.post(
        f"/{MCP_PATH}",
        data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        content_type="application/json",
    )
    assert r.status_code == 202


def test_mcpe004_delete_returns_405():
    app = _make_app()
    client = app.server.test_client()
    r = client.delete(f"/{MCP_PATH}")
    assert r.status_code == 405


def test_mcpe005_get_returns_405():
    app = _make_app()
    client = app.server.test_client()
    r = client.get(f"/{MCP_PATH}")
    assert r.status_code == 405


def test_mcpe006_post_rejects_wrong_content_type():
    app = _make_app()
    client = app.server.test_client()
    r = client.post(
        f"/{MCP_PATH}",
        data="not json",
        content_type="text/plain",
    )
    assert r.status_code == 415


def test_mcpe007_routes_not_registered_when_disabled():
    app = _make_app(enable_mcp=False)
    client = app.server.test_client()
    r = client.post(
        f"/{MCP_PATH}",
        data=json.dumps(
            {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
        ),
        content_type="application/json",
    )
    # With MCP disabled, the route doesn't exist — response is HTML, not JSON
    assert r.content_type != "application/json"


def test_mcpe008_routes_respect_pathname_prefix():
    app = _make_app(routes_pathname_prefix="/app/")
    client = app.server.test_client()

    ok = client.post(
        f"/app/{MCP_PATH}",
        data=json.dumps(
            {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
        ),
        content_type="application/json",
    )
    assert ok.status_code == 200

    miss = client.post(
        f"/{MCP_PATH}",
        data=json.dumps(
            {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
        ),
        content_type="application/json",
    )
    assert miss.status_code == 404


def test_mcpe009_enable_mcp_env_var_false():
    old = os.environ.get("DASH_MCP_ENABLED")
    try:
        os.environ["DASH_MCP_ENABLED"] = "false"
        app = _make_app()
        client = app.server.test_client()
        r = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
            ),
            content_type="application/json",
        )
        assert r.content_type != "application/json"
    finally:
        if old is None:
            os.environ.pop("DASH_MCP_ENABLED", None)
        else:
            os.environ["DASH_MCP_ENABLED"] = old


def test_mcpe010_constructor_overrides_env_var():
    old = os.environ.get("DASH_MCP_ENABLED")
    try:
        os.environ["DASH_MCP_ENABLED"] = "false"
        app = _make_app(enable_mcp=True)
        client = app.server.test_client()
        r = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
            ),
            content_type="application/json",
        )
        assert r.status_code == 200
        assert b"protocolVersion" in r.data
    finally:
        if old is None:
            os.environ.pop("DASH_MCP_ENABLED", None)
        else:
            os.environ["DASH_MCP_ENABLED"] = old
