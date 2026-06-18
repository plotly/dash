"""Input schema overrides drawn from the ``PropRole`` registry.

Looks up the parameter's ``(component_type, property)`` in the shared
registry and returns any attached ``input_schema``. Used when default
type introspection produces insufficient results.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput

from ..prop_roles import iter_prop_roles
from .base import InputSchemaSource


class OverrideSchema(InputSchemaSource):
    """Return a schema override, or None to fall through to introspection."""

    @classmethod
    def get_schema(cls, param: MCPInput) -> dict[str, Any] | None:
        component_type = param.get("component_type")
        prop = param["property"]
        for role in iter_prop_roles():
            if role.input_schema is None or not role.matches(component_type, prop):
                continue
            if callable(role.input_schema):
                return role.input_schema(param)
            return dict(role.input_schema)
        return None
