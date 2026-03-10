"""Dynamic callback tools for MCP.

Handles listing, naming, and executing callback-based tools.
"""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, TextContent, Tool

from dash import get_app
from dash.mcp.types import CallbackExecutionError, ToolNotFoundError

from .results import format_callback_response


def get_tool_names() -> set[str]:
    return get_app().mcp_callback_map.tool_names


def get_tools() -> list[Tool]:
    """Return one Tool per server-callable callback."""
    return get_app().mcp_callback_map.as_mcp_tools()


def call_tool(tool_name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Execute a callback tool by name."""
    from .callback_utils import run_callback

    callback_map = get_app().mcp_callback_map
    cb = callback_map.find_by_tool_name(tool_name)
    if cb is None:
        raise ToolNotFoundError(
            f"Tool not found: {tool_name}."
            " The app's callbacks may have changed."
            " Please call tools/list to refresh your tool list."
        )

    try:
        dispatch_response = run_callback(cb, arguments)
    except CallbackExecutionError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=str(e))],
            isError=True,
        )
    return format_callback_response(dispatch_response)
