"""A place to manually define Schemas that override component-defined prop types
where type generation produces insufficient results.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput

from .base import InputSchemaSource
from .schema_component_proptypes import ComponentPropSchema

_DATE_SCHEMA = {
    "type": "string",
    "format": "date",
    "pattern": r"^\d{4}-\d{2}-\d{2}$",
}


def _compute_dropdown_value_schema(param: MCPInput) -> dict[str, Any] | None:
    """Dropdown values are an array if `multi=True`; scalar values otherwise."""
    schema = ComponentPropSchema.get_schema(param)
    if schema is None:
        return None

    component = param.get("component")
    t = schema.get("type")
    if not isinstance(t, list):
        return schema

    if getattr(component, "multi", False):
        items_schema = schema.get("items", {})
        return (
            {"type": "array", "items": items_schema}
            if items_schema
            else {"type": "array"}
        )

    scalar_types = [x for x in t if x != "array"]
    refined = dict(schema)
    refined["type"] = scalar_types[0] if len(scalar_types) == 1 else scalar_types
    refined.pop("items", None)
    return refined


_OVERRIDES: dict[tuple[str, str], dict[str, Any] | callable] = {
    ("DatePickerSingle", "date"): _DATE_SCHEMA,
    ("DatePickerRange", "start_date"): _DATE_SCHEMA,
    ("DatePickerRange", "end_date"): _DATE_SCHEMA,
    ("Graph", "figure"): {
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"type": "object"}},
            "layout": {"type": "object"},
            "frames": {"type": "array", "items": {"type": "object"}},
        },
    },
    ("Dropdown", "value"): _compute_dropdown_value_schema,
}


class OverrideSchema(InputSchemaSource):
    """Return a schema override, or None to fall through to introspection."""

    @classmethod
    def get_schema(cls, param: MCPInput) -> dict[str, Any] | None:
        key = (param.get("component_type"), param["property"])
        override = _OVERRIDES.get(key)
        if override is None:
            return None
        if callable(override):
            return override(param)
        return dict(override)
