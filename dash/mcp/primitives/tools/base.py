"""Base class for MCP tool providers."""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, CreateTaskResult, Tool


class MCPToolProvider:
    """A provider of one or more MCP tools.

    Subclasses implement ``list_tools`` to return the tools they provide,
    ``get_tool_names`` to advertise those names for routing, and
    ``call_tool`` to execute a tool by name.
    """

    @classmethod
    def get_tool_names(cls) -> set[str]:
        raise NotImplementedError

    @classmethod
    def list_tools(cls) -> list[Tool]:
        raise NotImplementedError

    @classmethod
    def call_tool(
        cls, tool_name: str, arguments: dict[str, Any], task: dict | None = None
    ) -> CallToolResult | CreateTaskResult:
        raise NotImplementedError
