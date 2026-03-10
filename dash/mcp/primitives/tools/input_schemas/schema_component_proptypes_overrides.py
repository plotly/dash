"""Static override map for component property schemas.

Covers edge cases where component ``__init__`` annotations are
insufficient:

- Date pickers need ``format`` and ``pattern`` annotations
- Graph figure needs structured ``properties`` (data/layout/frames)
- Slider marks/tooltip need rich nested schemas
- Semantic type refinements (e.g. integer counters)

Nullability is NOT expressed here — it is handled via the
``required`` list based on component annotation introspection.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput
from .schema_component_proptypes import get_component_prop_schema

# (component_type, property) -> JSON Schema override
_OVERRIDES: dict[tuple[str, str], dict[str, Any]] = {
    # Template literals — annotation says "str", we add format/pattern.
    # TODO: encode min_date_allowed/max_date_allowed via component-aware refinement.
    ("DatePickerSingle", "date"): {
        "type": "string",
        "format": "date",
        "pattern": r"^\d{4}-\d{2}-\d{2}$",
    },
    ("DatePickerRange", "start_date"): {
        "type": "string",
        "format": "date",
        "pattern": r"^\d{4}-\d{2}-\d{2}$",
    },
    ("DatePickerRange", "end_date"): {
        "type": "string",
        "format": "date",
        "pattern": r"^\d{4}-\d{2}-\d{2}$",
    },
    # Graph — annotation says "object", we add structured properties.
    ("Graph", "figure"): {
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"type": "object"}},
            "layout": {"type": "object"},
            "frames": {"type": "array", "items": {"type": "object"}},
        },
    },
    ("Graph", "clickData"): {"type": "object"},
    ("Graph", "hoverData"): {"type": "object"},
    ("Graph", "selectedData"): {"type": "object"},
    ("Graph", "relayoutData"): {"type": "object"},
    ("Graph", "restyleData"): {"type": "array"},
    # Semantically an integer counter, annotation says "number"
    ("Interval", "n_intervals"): {"type": "integer"},
    # Slider/RangeSlider marks — annotation says "Any", we add rich schema
    ("Slider", "marks"): {
        "type": "object",
        "additionalProperties": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "style": {"type": "object"},
                    },
                    "required": ["label"],
                },
            ]
        },
    },
    ("RangeSlider", "marks"): {
        "type": "object",
        "additionalProperties": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "style": {"type": "object"},
                    },
                    "required": ["label"],
                },
            ]
        },
    },
    # Slider/RangeSlider tooltip — annotation says "Any", we add rich schema
    ("Slider", "tooltip"): {
        "type": "object",
        "properties": {
            "always_visible": {
                "type": "boolean",
                "description": "If true, tooltips are always visible (default: visible on hover).",
            },
            "placement": {
                "type": "string",
                "enum": [
                    "left",
                    "right",
                    "top",
                    "bottom",
                    "topLeft",
                    "topRight",
                    "bottomLeft",
                    "bottomRight",
                ],
                "description": "Tooltip placement relative to the handle.",
            },
            "template": {
                "type": "string",
                "description": (
                    "Template string for the tooltip. Must contain "
                    "{value} which is replaced with the slider value."
                ),
            },
            "transform": {
                "type": "string",
                "description": (
                    "Name of a function in window.dccFunctions "
                    "to transform the displayed value."
                ),
            },
            "style": {
                "type": "object",
                "description": "CSS style for the tooltip.",
            },
        },
    },
    ("RangeSlider", "tooltip"): {
        "type": "object",
        "properties": {
            "always_visible": {
                "type": "boolean",
                "description": "If true, tooltips are always visible (default: visible on hover).",
            },
            "placement": {
                "type": "string",
                "enum": [
                    "left",
                    "right",
                    "top",
                    "bottom",
                    "topLeft",
                    "topRight",
                    "bottomLeft",
                    "bottomRight",
                ],
                "description": "Tooltip placement relative to the handle.",
            },
            "template": {
                "type": "string",
                "description": (
                    "Template string for the tooltip. Must contain "
                    "{value} which is replaced with the slider value."
                ),
            },
            "transform": {
                "type": "string",
                "description": (
                    "Name of a function in window.dccFunctions "
                    "to transform the displayed value."
                ),
            },
            "style": {
                "type": "object",
                "description": "CSS style for the tooltip.",
            },
        },
    },
}


def get_override_schema(param: MCPInput) -> dict[str, Any] | None:
    """Look up a schema override for a component property.

    Checks the static override map first, then applies instance-aware
    refinements based on runtime props (e.g. Dropdown ``multi``).

    Returns the override schema dict, or ``None`` to fall through to
    the next source (component introspection).
    """
    component_type = param.get("component_type")
    prop = param["property"]
    component = param.get("component")

    override = _OVERRIDES.get((component_type, prop))
    if override is not None:
        schema = dict(override)
        return _refine_by_instance(schema, prop, component)

    if component is not None:
        return _instance_only_override(param)

    return None


def _refine_by_instance(
    schema: dict[str, Any],
    prop: str,
    component: Any | None,
) -> dict[str, Any]:
    """Narrow a static override based on the component instance."""
    if component is None:
        return schema
    return _apply_multi_refinement(schema, prop, component)


def _instance_only_override(param: MCPInput) -> dict[str, Any] | None:
    """Override schemas that exist only when examining the instance."""
    prop = param["property"]
    component = param.get("component")
    if prop == "value" and "multi" in getattr(component, "_prop_names", []):
        schema = get_component_prop_schema(param)
        if schema is not None:
            return _apply_multi_refinement(schema, prop, component)
    return None


def _apply_multi_refinement(
    schema: dict[str, Any],
    prop: str,
    component: Any,
) -> dict[str, Any]:
    """Narrow value type based on the ``multi`` prop."""
    if prop != "value" or "multi" not in getattr(component, "_prop_names", []):
        return schema

    multi = getattr(component, "multi", False)
    t = schema.get("type")
    if not isinstance(t, list):
        return schema

    if multi:
        items_schema = schema.get("items", {})
        return (
            {"type": "array", "items": items_schema}
            if items_schema
            else {"type": "array"}
        )

    scalar_types = [x for x in t if x != "array"]
    refined = dict(schema)
    if len(scalar_types) == 1:
        refined["type"] = scalar_types[0]
    elif scalar_types:
        refined["type"] = scalar_types
    refined.pop("items", None)
    return refined
