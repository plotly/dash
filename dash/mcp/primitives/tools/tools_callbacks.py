"""Dynamic callback tools for MCP.

Exposes every server-callable callback as an MCP tool.
"""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, CreateTaskResult, TextContent, Tool

from dash import get_app
from dash.mcp.tasks import create_task
from dash.mcp.types import CallbackExecutionError, ToolNotFoundError

from .base import MCPToolProvider
from .callback_utils import run_callback
from .results import format_callback_response, task_result_to_tool_result


class CallbackTools(MCPToolProvider):
    """Exposes every server-callable callback as an MCP tool."""

    # Set by configure_mcp_server().
    callbacks_mcp_enabled_by_default: bool = True
    expose_docstrings_by_default: bool = False

    @classmethod
    def get_tool_names(cls) -> set[str]:
        return get_app().mcp_callback_map.tool_names

    @classmethod
    def list_tools(cls) -> list[Tool]:
        """Return one Tool per server-callable callback."""
        return get_app().mcp_callback_map.as_mcp_tools()

    @classmethod
    def call_tool(
        cls,
        tool_name: str,
        arguments: dict[str, Any],
        task: dict | None = None,
    ) -> CallToolResult | CreateTaskResult:
        """Execute a callback tool by name."""
        callback_map = get_app().mcp_callback_map
        cb = callback_map.find_by_tool_name(tool_name)
        if cb is None:
            raise ToolNotFoundError(
                f"Tool not found: {tool_name}."
                " The app's callbacks may have changed."
                " Please call tools/list to refresh your tool list."
            )

        # pylint: disable-next=protected-access
        is_background = bool(cb._cb_info.get("background"))

        try:
            callback_response = run_callback(cb, arguments)
        except CallbackExecutionError as e:
            return CallToolResult(
                content=[TextContent(type="text", text=str(e))],
                isError=True,
            )

        if is_background:
            task_result = create_task(dict(callback_response), cb)
            if task is not None:
                return task_result
            return task_result_to_tool_result(task_result)

        return format_callback_response(callback_response, cb)
