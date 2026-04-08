"""Tool-level description generation for MCP tools.

Each source shares the same signature:
``(adapter: CallbackAdapter) -> list[str]``

This is distinct from per-parameter descriptions
(in ``input_schemas/input_descriptions/``) which populate
``inputSchema.properties.{param}.description``.
"""

from __future__ import annotations

from __future__ import annotations

from typing import TYPE_CHECKING

from .description_docstring import callback_docstring
from .description_outputs import output_summary

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter

_SOURCES = [
    output_summary,
    callback_docstring,
]


def build_tool_description(adapter: CallbackAdapter) -> str:
    """Build a human-readable description for an MCP tool."""
    lines: list[str] = []
    for source in _SOURCES:
        lines.extend(source(adapter))
    return "\n".join(lines) if lines else "Dash callback"
