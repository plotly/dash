"""Per-property description generation for MCP tool input parameters.

Each source is an ``InputDescriptionSource`` subclass that can add
text to a parameter's description. All sources are accumulated.
"""

from __future__ import annotations

from dash.mcp.types import MCPInput

from .base import InputDescriptionSource
from .description_component_props import ComponentPropsDescription
from .description_docstrings import DocstringPropDescription
from .description_html_labels import LabelDescription
from .description_pattern_matching import PatternMatchingDescription

_SOURCES: list[type[InputDescriptionSource]] = [
    DocstringPropDescription,
    LabelDescription,
    ComponentPropsDescription,
    PatternMatchingDescription,
]


def get_property_description(param: MCPInput) -> str | None:
    """Build a complete description string for a callback input parameter."""
    lines: list[str] = []
    if not param.get("required", True):
        lines.append("Input is optional.")
    for source in _SOURCES:
        lines.extend(source.describe(param))
    return "\n".join(lines) if lines else None
