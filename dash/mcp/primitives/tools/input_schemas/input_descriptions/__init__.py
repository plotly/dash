"""Per-property description generation for MCP tool input parameters.

Each source shares the same signature:
``(param: MCPInput) -> list[str]``

Sources are tried in order from most generic to most instance-specific.
All sources that produce lines are combined.
"""

from __future__ import annotations

from dash.mcp.types import MCPInput
from .description_component_props import component_props_description
from .description_docstrings import docstring_prop_description
from .description_html_labels import label_description

_SOURCES = [
    docstring_prop_description,
    label_description,
    component_props_description,
]


def get_property_description(param: MCPInput) -> str | None:
    """Build a complete description string for a callback input parameter."""
    lines: list[str] = []
    if not param.get("required", True):
        lines.append("Input is optional.")
    for source in _SOURCES:
        lines.extend(source(param))
    return "\n".join(lines) if lines else None
