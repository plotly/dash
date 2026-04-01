"""Input schema generation for MCP tool inputSchema fields.

Mirrors ``output_schemas/`` which generates ``outputSchema``.

Each source is tried in priority order. All share the same signature:
``(param: MCPInput) -> dict | None``.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput
from .schema_callback_type_annotations import annotation_to_schema
from .schema_component_proptypes_overrides import get_override_schema
from .schema_component_proptypes import get_component_prop_schema
from .input_descriptions import get_property_description

_SOURCES = [
    annotation_to_schema,
    get_override_schema,
    get_component_prop_schema,
]


def get_input_schema(param: MCPInput) -> dict[str, Any]:
    """Return the complete JSON Schema for a callback input parameter.

    Type sources provide ``type``/``enum`` (first non-None wins).
    Description is assembled by ``input_descriptions``.
    """
    schema: dict[str, Any] = {}
    for source in _SOURCES:
        result = source(param)
        if result is not None:
            schema = result
            break

    description = get_property_description(param)
    if description:
        schema = {**schema, "description": description}

    return schema
