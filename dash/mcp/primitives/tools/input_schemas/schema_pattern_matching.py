"""Schema for pattern-matching callback inputs (ALL, MATCH, ALLSMALLER).

When a callback input uses a wildcard ID, the callback receives a
list of values — one per matching component. This source detects
wildcard IDs and produces an array schema. If matching components
exist in the layout, the item type is inferred from a concrete match.
"""

from __future__ import annotations

from typing import Any

from dash._layout_utils import (
    _WILDCARD_VALUES,
    find_matching_components,
    parse_wildcard_id,
)
from dash.mcp.types import MCPInput

from .base import InputSchemaSource


class PatternMatchingSchema(InputSchemaSource):
    """Return a schema for pattern-matching inputs.

    For ALL/ALLSMALLER: array of ``{id, property, value}`` objects.
    For MATCH: a single ``{id, property, value}`` object.
    """

    @classmethod
    def get_schema(cls, param: MCPInput) -> dict[str, Any] | None:
        dep_id = parse_wildcard_id(param["component_id"])
        if dep_id is None:
            return None

        wildcard_type = _get_wildcard_type(dep_id)
        if wildcard_type is None:
            return None

        value_schema = _infer_value_schema(param)

        item_schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "id": {"type": "object"},
                "property": {"type": "string"},
                "value": value_schema or {},
            },
            "required": ["id", "property", "value"],
        }

        if wildcard_type == "MATCH":
            return item_schema

        return {"type": "array", "items": item_schema}


def _get_wildcard_type(dep_id: dict) -> str | None:
    """Return the wildcard type (ALL, MATCH, ALLSMALLER) or None."""
    for value in dep_id.values():
        if isinstance(value, list) and len(value) == 1:
            if value[0] in _WILDCARD_VALUES:
                return value[0]
    return None


def _infer_value_schema(param: MCPInput) -> dict[str, Any] | None:
    """Infer the JSON Schema for the ``value`` field from a matching component."""
    pattern = parse_wildcard_id(param["component_id"])
    if pattern is None:
        return None
    matches = find_matching_components(pattern)
    if not matches:
        return None

    # pylint: disable-next=cyclic-import,import-outside-toplevel
    from . import get_input_schema

    concrete_param: MCPInput = {
        **param,
        "component": matches[0],
        "component_id": str(getattr(matches[0], "id", "")),
        "component_type": getattr(matches[0], "_type", None),
    }
    schema = get_input_schema(concrete_param)
    schema.pop("description", None)
    return schema or None
