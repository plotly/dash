"""Shared helpers for MCP integration tests."""

import requests


def _mcp_post(server_url, method, params=None, request_id=1):
    return requests.post(
        f"{server_url}/_mcp",
        json={
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id,
            "params": params or {},
        },
        headers={"Content-Type": "application/json"},
        timeout=5,
    )


def _mcp_tools(server_url):
    resp = _mcp_post(server_url, "tools/list")
    resp.raise_for_status()
    return resp.json()["result"]["tools"]


def _mcp_call_tool(server_url, tool_name, arguments=None):
    resp = _mcp_post(
        server_url,
        "tools/call",
        {"name": tool_name, "arguments": arguments or {}},
    )
    resp.raise_for_status()
    return resp.json()


def _mcp_method(server_url, method, params=None):
    resp = _mcp_post(server_url, method, params)
    resp.raise_for_status()
    return resp.json()
