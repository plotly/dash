"""Map callback function type annotations to JSON Schema.

When a callback function has explicit type annotations, those take
priority over all other schema sources (static overrides, component
introspection).

Unlike component annotations (where nullable means "not required"),
callback annotations preserve ``null`` in the schema type when the
user writes ``Optional[X]`` — the user is explicitly saying the
value can be null.

Also provides ``annotation_to_json_schema``, the shared low-level
converter used by both callback and component annotation pipelines.
"""

from __future__ import annotations

import inspect
from typing import Any

from pydantic import TypeAdapter

from dash.development.base_component import Component
from dash.mcp.types import MCPInput, is_nullable

from .base import InputSchemaSource


def annotation_to_json_schema(annotation: type) -> dict[str, Any] | None:
    """Convert a Python type annotation to a JSON Schema dict.

    Returns ``None`` if the annotation cannot be translated.
    """
    if annotation is inspect.Parameter.empty or annotation is type(None):
        return None

    if isinstance(annotation, type) and issubclass(annotation, Component):
        return {"type": "string"}

    try:
        return TypeAdapter(annotation).json_schema()
    except Exception:  # pylint: disable=broad-exception-caught
        return None


class AnnotationSchema(InputSchemaSource):
    """Derive JSON Schema from the callback parameter's type annotation."""

    @classmethod
    def get_schema(cls, param: MCPInput) -> dict[str, Any] | None:
        annotation = param.get("annotation")
        if annotation is None:
            return None
        schema = annotation_to_json_schema(annotation)
        if schema is None:
            return None

        if is_nullable(annotation) and schema:
            t = schema.get("type")
            if isinstance(t, str):
                schema = {**schema, "type": [t, "null"]}
            elif isinstance(t, list) and "null" not in t:
                schema = {**schema, "type": [*t, "null"]}

        return schema
