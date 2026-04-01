"""MCP tool listing and call handling.

Each tool module exports:
- ``get_tool_names() -> set[str]``
- ``get_tools() -> list[Tool]``
- ``call_tool(tool_name, arguments) -> CallToolResult``

The __init__ assembles the list and dispatches calls by name.
"""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, ListToolsResult

from dash.mcp.types import ToolNotFoundError

from . import tool_get_dash_component as _get_component
from . import tools_callbacks as _callbacks

_TOOL_MODULES = [_callbacks, _get_component]


def list_tools() -> ListToolsResult:
    """Build the MCP tools/list response."""
    tools = []
    for mod in _TOOL_MODULES:
        tools.extend(mod.get_tools())
    return ListToolsResult(tools=tools)


def call_tool(tool_name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Dispatch a tools/call request by tool name."""
    for mod in _TOOL_MODULES:
        if tool_name in mod.get_tool_names():
            result = mod.call_tool(tool_name, arguments)
            return result
    raise ToolNotFoundError(
        f"Tool not found: {tool_name}."
        " The app's callbacks may have changed."
        " Please call tools/list to refresh your tool list."
    )
