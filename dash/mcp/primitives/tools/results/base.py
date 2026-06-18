"""Base class for result formatters."""

from __future__ import annotations

from typing import Any

from mcp.types import ImageContent, TextContent

from dash.mcp.types import MCPOutput


class ResultFormatter:
    """A formatter that can enrich an MCP tool result with additional content.

    Subclasses implement ``format`` to return content items (text, images)
    for a specific callback output. All formatters are accumulated — every
    formatter can add content to the overall tool result.
    """

    @classmethod
    def format(
        cls, output: MCPOutput, returned_output_value: Any
    ) -> list[TextContent | ImageContent]:
        raise NotImplementedError
