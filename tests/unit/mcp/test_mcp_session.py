"""MCP session management — ``Mcp-Session-Id`` header and hot-reload hash."""

import json
import sys

import pytest

if sys.version_info < (3, 10):
    pytest.skip("MCP requires Python 3.10+", allow_module_level=True)

from tests.unit.mcp.conftest import _make_app  # pylint: disable=wrong-import-position


def _make_mcp_app(**kwargs):
    return _make_app(enable_mcp=True, **kwargs)


def _post(client, method, params=None, request_id=1, session_id=None):
    """POST a JSON-RPC message to the MCP endpoint."""
    headers = {"Content-Type": "application/json"}
    if session_id is not None:
        headers["Mcp-Session-Id"] = session_id
    body = {"jsonrpc": "2.0", "method": method, "id": request_id}
    body["params"] = params if params is not None else {}
    return client.post("/_mcp", data=json.dumps(body), headers=headers)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_mcpse001_initialize_returns_session_id():
    app = _make_mcp_app()
    with app.server.test_client() as client:
        resp = _post(client, "initialize")
        assert resp.status_code == 200
        session_id = resp.headers.get("Mcp-Session-Id")
        assert session_id is not None
        assert len(session_id) > 0


def test_mcpse003_request_with_valid_session_succeeds():
    app = _make_mcp_app()
    with app.server.test_client() as client:
        init_resp = _post(client, "initialize")
        session_id = init_resp.headers["Mcp-Session-Id"]
        resp = _post(client, "tools/list", session_id=session_id)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "result" in data


def test_mcpse004_stale_session_recovers_transparently():
    app = _make_mcp_app()
    app._hot_reload.hash = "hash_v1"

    with app.server.test_client() as client:
        init_resp = _post(client, "initialize")
        old_session = init_resp.headers["Mcp-Session-Id"]
        assert old_session == "hash_v1"

        app._hot_reload.hash = "hash_v2"

        resp = _post(client, "tools/list", session_id=old_session)
        assert resp.status_code == 200

        data = json.loads(resp.data)
        assert isinstance(data, list)
        assert len(data) == 3

        new_session = resp.headers.get("Mcp-Session-Id")
        assert new_session is not None
        assert new_session == "hash_v2"


def test_mcpse005_stale_session_includes_list_changed_notifications():
    app = _make_mcp_app()
    app._hot_reload.hash = "hash_v1"

    with app.server.test_client() as client:
        init_resp = _post(client, "initialize")
        old_session = init_resp.headers["Mcp-Session-Id"]

        app._hot_reload.hash = "hash_v2"

        resp = _post(client, "tools/list", session_id=old_session)
        data = json.loads(resp.data)

        assert data[0]["method"] == "notifications/tools/list_changed"
        assert data[1]["method"] == "notifications/resources/list_changed"
        assert "result" in data[2]


def test_mcpse006_reinitialize_after_hot_reload_gets_new_session():
    app = _make_mcp_app()
    app._hot_reload.hash = "hash_v1"

    with app.server.test_client() as client:
        init_resp = _post(client, "initialize")
        old_session = init_resp.headers["Mcp-Session-Id"]
        assert old_session == "hash_v1"

        app._hot_reload.hash = "hash_v2"

        # Stale request triggers transparent recovery.
        resp = _post(client, "tools/list", session_id=old_session)
        assert resp.status_code == 200
        recovered_session = resp.headers["Mcp-Session-Id"]
        assert recovered_session == "hash_v2"

        # Re-initialize picks up the new hash.
        init_resp2 = _post(client, "initialize")
        assert init_resp2.status_code == 200
        new_session = init_resp2.headers["Mcp-Session-Id"]
        assert new_session == "hash_v2"

        # Subsequent requests with the new session work.
        resp = _post(client, "tools/list", session_id=new_session)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "result" in data


def test_mcpse007_no_session_required_before_first_initialize():
    app = _make_mcp_app()
    with app.server.test_client() as client:
        resp = _post(client, "tools/list")
        assert resp.status_code == 200


def test_mcpse008_production_mode_generates_stable_session():
    app = _make_mcp_app()
    assert app._hot_reload.hash is None

    with app.server.test_client() as client:
        init_resp = _post(client, "initialize")
        session_id = init_resp.headers["Mcp-Session-Id"]
        assert session_id is not None

        resp = _post(client, "tools/list", session_id=session_id)
        assert resp.status_code == 200

        resp = _post(client, "tools/list", session_id=session_id)
        assert resp.status_code == 200


def test_mcpse009_session_header_on_every_response():
    app = _make_mcp_app()
    with app.server.test_client() as client:
        init_resp = _post(client, "initialize")
        session_id = init_resp.headers["Mcp-Session-Id"]

        resp = _post(client, "tools/list", session_id=session_id)
        assert resp.status_code == 200
        assert resp.headers.get("Mcp-Session-Id") == session_id
