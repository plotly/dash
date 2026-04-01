"""Tool-level description generation for MCP tools.

Each source shares the same signature:
``(outputs, docstring) -> list[str]``

This is distinct from per-parameter descriptions
(in ``input_schemas/input_descriptions/``) which populate
``inputSchema.properties.{param}.description``.
"""

from __future__ import annotations

from typing import Any

from .description_docstring import callback_docstring
from .description_outputs import output_summary

_SOURCES = [
    output_summary,
    callback_docstring,
]


def build_tool_description(
    outputs: list[dict[str, Any]],
    docstring: str | None = None,
) -> str:
    """Build a human-readable description for an MCP tool."""
    lines: list[str] = []
    for source in _SOURCES:
        lines.extend(source(outputs, docstring))
    return "\n".join(lines) if lines else "Dash callback"
