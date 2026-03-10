"""Convert component ``__init__`` type annotations to JSON Schema.

Uses pydantic's ``TypeAdapter`` for type translation. Dash-specific
types (Component subclasses) are handled as pre-checks. NumberType
is handled natively by pydantic when components are generated with
the pydantic-aware ``NumberType`` from ``dash.types``.

Third-party components with old inline ``NumberType`` (pre-4.3) will
fall through to ``None`` — the schema defaults to ``{}`` (any type).
"""

from __future__ import annotations

import inspect
from typing import Any

from pydantic import TypeAdapter

from dash.development.base_component import Component
from dash.mcp.types import MCPInput


def get_json_schema(annotation: Any) -> dict[str, Any] | None:
    """Convert a Python type annotation to a JSON Schema dict.

    Returns ``None`` if the annotation cannot be translated.
    """
    if annotation is inspect.Parameter.empty or annotation is type(None):
        return None

    if _is_component_type(annotation):
        return {"type": "string"}

    try:
        return TypeAdapter(annotation).json_schema()
    except Exception:
        return None


def _is_component_type(ann: Any) -> bool:
    return isinstance(ann, type) and issubclass(ann, Component)


def get_component_prop_schema(param: MCPInput) -> dict[str, Any] | None:
    """Return the JSON Schema for a component property.

    Inspects the ``__init__`` signature of the component's class.
    Returns ``None`` if the prop has no annotation.
    """
    component = param.get("component")
    prop = param["property"]
    if component is None:
        return None
    cls = type(component)
    try:
        sig = inspect.signature(cls.__init__)
    except (ValueError, TypeError):
        return None

    sig_param = sig.parameters.get(prop)
    if sig_param is None or sig_param.annotation is inspect.Parameter.empty:
        return None

    return get_json_schema(sig_param.annotation)
