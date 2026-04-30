"""Input schema generation for MCP tool inputSchema fields.

Each source is an ``InputSchemaSource`` subclass that can type
an input parameter. Sources are tried in priority order — first
non-None wins.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput

from .base import InputSchemaSource
from .schema_callback_type_annotations import AnnotationSchema
from .schema_component_proptypes_overrides import OverrideSchema
from .schema_component_proptypes import ComponentPropSchema
from .input_descriptions import get_property_description

_SOURCES: list[type[InputSchemaSource]] = [
    AnnotationSchema,
    OverrideSchema,
    ComponentPropSchema,
]


def get_input_schema(param: MCPInput) -> dict[str, Any]:
    """Return the complete JSON Schema for a callback input parameter.

    Type sources provide ``type``/``enum`` (first non-None wins).
    Description is assembled by ``input_descriptions``.
    """
    schema: dict[str, Any] = {}
    for source in _SOURCES:
        result = source.get_schema(param)
        if result is not None:
            schema = result
            break

    description = get_property_description(param)
    if description:
        schema = {**schema, "description": description}

    return schema
