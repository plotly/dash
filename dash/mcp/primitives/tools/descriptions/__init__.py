"""Tool-level description generation for MCP tools.

Each source is a ``ToolDescriptionSource`` subclass that can add text
to the tool's description. All sources are accumulated.

This is distinct from per-parameter descriptions
(in ``input_schemas/input_descriptions/``) which populate
``inputSchema.properties.{param}.description``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ToolDescriptionSource
from .description_docstring import DocstringDescription
from .description_outputs import OutputSummaryDescription

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter

_SOURCES: list[type[ToolDescriptionSource]] = [
    OutputSummaryDescription,
    DocstringDescription,
]


def build_tool_description(callback: CallbackAdapter) -> str:
    """Build a human-readable description for an MCP tool."""
    lines: list[str] = []
    for source in _SOURCES:
        lines.extend(source.describe(callback))
    return "\n".join(lines) if lines else "Dash callback"
