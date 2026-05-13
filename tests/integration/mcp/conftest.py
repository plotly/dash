"""Shared helpers for MCP integration tests."""

import sys

import pytest
import requests

collect_ignore_glob = []
if sys.version_info < (3, 10):
    collect_ignore_glob.append("*")


@pytest.fixture(autouse=True)
def _enable_mcp_for_integration_tests(monkeypatch):
    """MCP is off by default; integration tests need it on."""
    monkeypatch.setenv("DASH_MCP_ENABLED", "true")


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
