"""MCP tool listing and call handling."""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, ListToolsResult

from dash.mcp.types import ToolNotFoundError

from .base import MCPToolProvider
from .tool_get_dash_component import GetDashComponentTool
from .tools_callbacks import CallbackTools

_TOOL_PROVIDERS: list[type[MCPToolProvider]] = [
    CallbackTools,
    GetDashComponentTool,
]


def list_tools() -> ListToolsResult:
    """Build the MCP tools/list response."""
    tools = []
    for provider in _TOOL_PROVIDERS:
        tools.extend(provider.list_tools())
    return ListToolsResult(tools=tools)


def call_tool(tool_name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Route a tools/call request by tool name."""
    for provider in _TOOL_PROVIDERS:
        if tool_name in provider.get_tool_names():
            return provider.call_tool(tool_name, arguments)
    raise ToolNotFoundError(
        f"Tool not found: {tool_name}."
        " The app's callbacks may have changed."
        " Please call tools/list to refresh your tool list."
    )
