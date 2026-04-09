"""Integration tests for the MCP Streamable HTTP endpoint.

These tests use Flask's test_client to exercise the HTTP transport layer
(POST/GET/DELETE at /_mcp), session management, content-type handling,
and route registration/configuration.
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


class TestMCPEndpoint:
    """Tests for the Streamable HTTP MCP endpoint at /_mcp."""

    def test_post_initialize_creates_session(self):
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
        assert "mcp-session-id" in r.headers
        data = json.loads(r.data)
        assert data["result"]["protocolVersion"] == LATEST_PROTOCOL_VERSION

    def test_post_without_session_returns_400(self):
        app = _make_app()
        client = app.server.test_client()
        r = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": {}}
            ),
            content_type="application/json",
        )
        assert r.status_code == 400

    def test_stale_session_returns_404(self):
        app = _make_app()
        client = app.server.test_client()
        r = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 1,
                    "params": {},
                }
            ),
            content_type="application/json",
            headers={"mcp-session-id": "old-session-from-before-restart"},
        )
        assert r.status_code == 404

    def test_post_with_valid_session(self):
        app = _make_app()
        client = app.server.test_client()
        # Initialize to get session
        r1 = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
            ),
            content_type="application/json",
        )
        session_id = r1.headers["mcp-session-id"]
        # Use session for tools/list
        r2 = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "tools/list", "id": 2, "params": {}}
            ),
            content_type="application/json",
            headers={"mcp-session-id": session_id},
        )
        assert r2.status_code == 200
        data = json.loads(r2.data)
        assert "result" in data
        assert "tools" in data["result"]

    def test_notification_returns_202(self):
        app = _make_app()
        client = app.server.test_client()
        # Initialize to get session
        r1 = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
            ),
            content_type="application/json",
        )
        session_id = r1.headers["mcp-session-id"]
        # Send notification (no id field)
        r2 = client.post(
            f"/{MCP_PATH}",
            data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            content_type="application/json",
            headers={"mcp-session-id": session_id},
        )
        assert r2.status_code == 202

    def test_delete_terminates_session(self):
        app = _make_app()
        client = app.server.test_client()
        # Initialize
        r1 = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {}}
            ),
            content_type="application/json",
        )
        session_id = r1.headers["mcp-session-id"]
        # Delete
        r2 = client.delete(
            f"/{MCP_PATH}",
            headers={"mcp-session-id": session_id},
        )
        assert r2.status_code == 204
        # Post-delete requests return 404
        r3 = client.post(
            f"/{MCP_PATH}",
            data=json.dumps(
                {"jsonrpc": "2.0", "method": "tools/list", "id": 2, "params": {}}
            ),
            content_type="application/json",
            headers={"mcp-session-id": session_id},
        )
        assert r3.status_code == 404

    def test_delete_nonexistent_session_returns_404(self):
        app = _make_app()
        client = app.server.test_client()
        r = client.delete(
            f"/{MCP_PATH}",
            headers={"mcp-session-id": "nonexistent"},
        )
        assert r.status_code == 404

    def test_get_without_session_returns_404(self):
        app = _make_app()
        client = app.server.test_client()
        r = client.get(f"/{MCP_PATH}")
        assert r.status_code == 404

    def test_get_with_stale_session_returns_404(self):
        app = _make_app()
        client = app.server.test_client()
        r = client.get(
            f"/{MCP_PATH}",
            headers={"mcp-session-id": "nonexistent"},
        )
        assert r.status_code == 404

    def test_post_rejects_wrong_content_type(self):
        app = _make_app()
        client = app.server.test_client()
        r = client.post(
            f"/{MCP_PATH}",
            data="not json",
            content_type="text/plain",
        )
        assert r.status_code == 415

    def test_routes_not_registered_when_disabled(self):
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

    def test_routes_respect_pathname_prefix(self):
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

    def test_enable_mcp_env_var_false(self):
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

    def test_constructor_overrides_env_var(self):
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
