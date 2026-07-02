"""Built-in tools for background callback task lifecycle.

Thin wrappers around the spec-aligned core in dash.mcp.tasks.
Only registered when the app has background callbacks.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import CallToolResult, TextContent, Tool

from dash import get_app
from dash.mcp.tasks import get_task, get_task_result, cancel_task

from .base import MCPToolProvider


GET_RESULT_TOOL_NAME = "get_background_task_result"
CANCEL_TOOL_NAME = "cancel_background_task"


def _has_background_callbacks() -> bool:
    return any(cb_info.get("background") for cb_info in get_app().callback_map.values())


class BackgroundTaskTools(MCPToolProvider):
    """Built-in tools for polling and cancelling background callback tasks.

    Only registered when the app has background callbacks.
    """

    @classmethod
    def get_tool_names(cls) -> set[str]:
        if not _has_background_callbacks():
            return set()
        return {GET_RESULT_TOOL_NAME, CANCEL_TOOL_NAME}

    @classmethod
    def list_tools(cls) -> list[Tool]:
        if not _has_background_callbacks():
            return []
        return [
            Tool(
                name=GET_RESULT_TOOL_NAME,
                description=(
                    "Poll for the result of a long-running background callback. "
                    "Pass the taskId returned by the original tool call. "
                    "If the task is still running, call this tool again. "
                    "If complete, returns the callback result."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "taskId": {
                            "type": "string",
                            "description": "The taskId returned by the background callback tool.",
                        },
                    },
                    "required": ["taskId"],
                },
            ),
            Tool(
                name=CANCEL_TOOL_NAME,
                description="Cancel a running background callback.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "taskId": {
                            "type": "string",
                            "description": "The taskId of the background task to cancel.",
                        },
                    },
                    "required": ["taskId"],
                },
            ),
        ]

    @classmethod
    def call_tool(
        cls,
        tool_name: str,
        arguments: dict[str, Any],
        task: dict | None = None,
    ) -> CallToolResult:
        task_id = arguments.get("taskId", "")

        if tool_name == GET_RESULT_TOOL_NAME:
            task_status = get_task(task_id)
            if task_status.status == "completed":
                return get_task_result(task_id)
            return CallToolResult(
                content=[TextContent(type="text", text=task_status.model_dump_json())],
            )

        if tool_name == CANCEL_TOOL_NAME:
            result = cancel_task(task_id)
            return CallToolResult(
                content=[TextContent(type="text", text=result.model_dump_json())],
            )

        raise ValueError(f"Unknown tool: {tool_name}")
