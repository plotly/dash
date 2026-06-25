"""MCP session lifecycle — end-to-end over a real Dash server.

Exercises the full MCP session flow (initialize → operate → hot-reload
recovery) against a live ``dash_duo`` server using real HTTP requests.
Unit-level checks (status codes, header mechanics) live in
``tests/unit/mcp/test_mcp_session.py``; these tests verify the broader
behavioral contract.
"""

import requests

from dash import Dash, Input, Output, html

from tests.integration.mcp.conftest import _mcp_post


def _mcp_post_with_session(
    server_url, method, params=None, request_id=1, session_id=None
):
    """Like ``_mcp_post`` but forwards an ``Mcp-Session-Id`` header."""
    headers = {"Content-Type": "application/json"}
    if session_id is not None:
        headers["Mcp-Session-Id"] = session_id
    return requests.post(
        f"{server_url}/_mcp",
        json={
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id,
            "params": params or {},
        },
        headers=headers,
        timeout=5,
    )


def test_mcpse_e2e001_full_session_lifecycle(dash_duo):
    """Initialize → tools/list → tools/call with session headers throughout."""
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "children"))
    def echo(v):
        return f"echo: {v}"

    dash_duo.start_server(app)
    url = dash_duo.server.url

    init = _mcp_post_with_session(url, "initialize")
    assert init.status_code == 200
    sid = init.headers.get("Mcp-Session-Id")
    assert sid

    notif = _mcp_post_with_session(
        url, "notifications/initialized", session_id=sid, request_id=None
    )
    assert notif.status_code == 202

    tools_resp = _mcp_post_with_session(url, "tools/list", session_id=sid, request_id=2)
    assert tools_resp.status_code == 200
    tools = tools_resp.json()["result"]["tools"]
    assert any("echo" in t["name"] for t in tools)

    tool_name = next(t["name"] for t in tools if "echo" in t["name"])
    call_resp = _mcp_post_with_session(
        url,
        "tools/call",
        params={"name": tool_name, "arguments": {"v": "hello"}},
        session_id=sid,
        request_id=3,
    )
    assert call_resp.status_code == 200
    assert call_resp.headers.get("Mcp-Session-Id") == sid


def test_mcpse_e2e002_stale_session_recovers_with_notifications(dash_duo):
    """Simulate a hot-reload hash change and verify transparent recovery."""
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "children"))
    def echo(v):
        return f"echo: {v}"

    dash_duo.start_server(app)
    url = dash_duo.server.url

    app._hot_reload.hash = "original_hash"

    init = _mcp_post_with_session(url, "initialize")
    sid = init.headers["Mcp-Session-Id"]
    assert sid == "original_hash"

    resp = _mcp_post_with_session(url, "tools/list", session_id=sid, request_id=2)
    assert resp.status_code == 200

    app._hot_reload.hash = "new_hash"

    resp = _mcp_post_with_session(url, "tools/list", session_id=sid, request_id=3)
    assert resp.status_code == 200
    new_sid = resp.headers["Mcp-Session-Id"]
    assert new_sid == "new_hash"

    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["method"] == "notifications/tools/list_changed"
    assert data[1]["method"] == "notifications/resources/list_changed"
    assert "result" in data[2]
    assert "tools" in data[2]["result"]

    resp = _mcp_post_with_session(url, "tools/list", session_id=new_sid, request_id=4)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "result" in data


def test_mcpse_e2e003_capabilities_advertise_list_changed(dash_duo):
    """Server capabilities include listChanged for tools and resources."""
    app = Dash(__name__)
    app.layout = html.Div(id="root")
    dash_duo.start_server(app)

    resp = _mcp_post(dash_duo.server.url, "initialize")
    caps = resp.json()["result"]["capabilities"]
    assert caps["tools"]["listChanged"] is True
    assert caps["resources"]["listChanged"] is True
