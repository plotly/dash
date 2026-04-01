"""Shared helpers for MCP integration tests."""

import requests


def _mcp_post(server_url, method, params=None, session_id=None, request_id=1):
    headers = {"Content-Type": "application/json"}
    if session_id:
        headers["mcp-session-id"] = session_id
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


def _mcp_session(server_url):
    resp = _mcp_post(server_url, "initialize")
    resp.raise_for_status()
    return resp.headers["mcp-session-id"]


def _mcp_tools(server_url):
    sid = _mcp_session(server_url)
    resp = _mcp_post(server_url, "tools/list", session_id=sid, request_id=2)
    resp.raise_for_status()
    return resp.json()["result"]["tools"]


def _mcp_call_tool(server_url, tool_name, arguments=None):
    sid = _mcp_session(server_url)
    resp = _mcp_post(
        server_url,
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
        session_id=sid,
        request_id=2,
    )
    resp.raise_for_status()
    return resp.json()


def _mcp_method(server_url, method, params=None):
    sid = _mcp_session(server_url)
    resp = _mcp_post(server_url, method, params, session_id=sid, request_id=2)
    resp.raise_for_status()
    return resp.json()
