"""MCP tool listing and call handling."""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, CreateTaskResult, ListToolsResult

from dash.mcp.types import ToolNotFoundError

from .base import MCPToolProvider
from .tool_background_tasks import BackgroundTaskTools
from .tool_decorated_mcp_functions import DecoratedFunctionTools
from .tool_get_dash_component import GetDashComponentTool
from .tools_callbacks import CallbackTools

_TOOL_PROVIDERS: list[type[MCPToolProvider]] = [
    CallbackTools,
    BackgroundTaskTools,
    GetDashComponentTool,
    DecoratedFunctionTools,
]


def list_tools() -> ListToolsResult:
    """Build the MCP tools/list response."""
    tools = []
    for provider in _TOOL_PROVIDERS:
        tools.extend(provider.list_tools())
    return ListToolsResult(tools=tools)


def call_tool(
    tool_name: str, arguments: dict[str, Any], task: dict | None = None
) -> CallToolResult | CreateTaskResult:
    """Route a tools/call request by tool name.

    The optional ``task`` parameter (per MCP Tasks protocol) is passed
    through to providers that support background callbacks.
    """
    for provider in _TOOL_PROVIDERS:
        if tool_name in provider.get_tool_names():
            return provider.call_tool(tool_name, arguments, task=task)
    raise ToolNotFoundError(
        f"Tool not found: {tool_name}."
        " The app's callbacks may have changed."
        " Please call tools/list to refresh your tool list."
    )
