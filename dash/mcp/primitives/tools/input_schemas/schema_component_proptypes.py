"""Derive JSON Schema from a component's ``__init__`` type annotations."""

from __future__ import annotations

import inspect
from typing import Any

from dash.mcp.types import MCPInput

from .base import InputSchemaSource
from .schema_callback_type_annotations import annotation_to_json_schema


class ComponentPropSchema(InputSchemaSource):
    """Derive JSON Schema from a component's ``__init__`` type annotations.

    Inspects the ``__init__`` signature of the component's class.
    Returns ``None`` if the prop has no annotation.
    """

    @classmethod
    def get_schema(cls, param: MCPInput) -> dict[str, Any] | None:
        component = param.get("component")
        prop = param["property"]
        if component is None:
            return None

        try:
            sig = inspect.signature(type(component).__init__)
        except (ValueError, TypeError):
            return None

        sig_param = sig.parameters.get(prop)
        if sig_param is None or sig_param.annotation is inspect.Parameter.empty:
            return None

        return annotation_to_json_schema(sig_param.annotation)
