"""Canonical registry of semantic roles for Dash component props.

A ``PropRole`` bundles the set of ``(component_type, property)`` pairs
that play the same role with the metadata attached to that role:
an LLM-facing description, an input JSON Schema, etc. Tool descriptions,
input-schema overrides, and result formatters all consume this registry
so they can't drift.

Use ``ANY_COMPONENT`` as the component_type sentinel to match any component with
the given property name.

Declaration order matters: ``iter_prop_roles()`` yields roles in the
order they're defined in this module, and the first match wins. List
concrete-match roles before wildcard-match roles that share a prop
name (e.g. ``MARKDOWN`` before ``CONTENT`` for ``children``).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, NamedTuple, Union

from typing_extensions import TypeAlias

from dash.mcp.types import MCPInput

PropSchema = Union[
    Dict[str, Any],
    Callable[[MCPInput], Dict[str, Any]],
]

COMPONENT: TypeAlias = Union[str, None]
ANY_COMPONENT: None = None
PROP: TypeAlias = str


class PropRole(NamedTuple):
    identifiers: set[tuple[COMPONENT, PROP]]
    description: str | None = None
    input_schema: PropSchema | None = None

    def matches(self, component_type: COMPONENT, prop: PROP) -> bool:
        """True if this role applies to the given ``(component_type, prop)``.

        Matches either a concrete entry or an ``ANY_COMPONENT`` wildcard
        entry in ``identifiers``. Shared by every consumer so all metadata
        fields apply uniformly to every identifier in the role.
        """
        return (component_type, prop) in self.identifiers or (
            ANY_COMPONENT,
            prop,
        ) in self.identifiers


def _compute_dropdown_value_schema(param: MCPInput) -> dict[str, Any]:
    """Dropdown values are an array if ``multi=True``; scalar otherwise."""
    _DROPDOWN_SCALAR_TYPE = {
        "anyOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}]
    }
    component = param.get("component")
    if getattr(component, "multi", False):
        return {"type": "array", "items": _DROPDOWN_SCALAR_TYPE}
    return _DROPDOWN_SCALAR_TYPE


TABULAR = PropRole(
    identifiers={("DataTable", "data"), ("AgGrid", "rowData")},
    description="Returns tabular data",
)

DATE = PropRole(
    identifiers={
        ("DatePickerSingle", "date"),
        ("DatePickerRange", "start_date"),
        ("DatePickerRange", "end_date"),
    },
    input_schema={
        "type": "string",
        "format": "date",
        "pattern": r"^\d{4}-\d{2}-\d{2}$",
    },
)

DROPDOWN_VALUE = PropRole(
    identifiers={("Dropdown", "value")},
    input_schema=_compute_dropdown_value_schema,
)

STORE_DATA = PropRole(
    identifiers={("Store", "data")},
    description="Returns data to be remembered client-side",
)

DOWNLOAD = PropRole(
    identifiers={("Download", "data")},
    description="Returns downloadable content",
)

MARKDOWN = PropRole(
    identifiers={("Markdown", "children")},
    description="Returns formatted text",
)

GENERIC_FIGURE = PropRole(
    identifiers={(ANY_COMPONENT, "figure")},
    description="Returns chart/visualization data",
    input_schema={
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": {"type": "object"}},
            "layout": {"type": "object"},
            "frames": {"type": "array", "items": {"type": "object"}},
        },
    },
)

GENERIC_CONTENT = PropRole(
    identifiers={(ANY_COMPONENT, "children")},
    description="Returns content",
)

GENERIC_VALUE = PropRole(
    identifiers={(ANY_COMPONENT, "value")},
    description="Returns the current value",
)

GENERIC_OPTIONS = PropRole(
    identifiers={(ANY_COMPONENT, "options")},
    description="Returns available options",
)

GENERIC_COLUMNS = PropRole(
    identifiers={(ANY_COMPONENT, "columns")},
    description="Returns column definitions",
)

GENERIC_STYLE = PropRole(
    identifiers={(ANY_COMPONENT, "style")},
    description="Updates styling",
)

GENERIC_DISABLED = PropRole(
    identifiers={(ANY_COMPONENT, "disabled")},
    description="Updates enabled/disabled state",
)


def iter_prop_roles() -> Iterator[PropRole]:
    """Yield every PropRole defined in this module in declaration order."""
    for value in globals().values():
        if isinstance(value, PropRole):
            yield value
