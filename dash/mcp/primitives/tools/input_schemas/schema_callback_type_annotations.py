"""Map callback function type annotations to JSON Schema.

When a callback function has explicit type annotations, those take
priority over all other schema sources (static overrides, component
introspection).

Unlike component annotations (where nullable means "not required"),
callback annotations preserve ``null`` in the schema type when the
user writes ``Optional[X]`` — the user is explicitly saying the
value can be null.

Delegates to :func:`schema_component_proptypes.get_json_schema` for type
translation, then re-adds ``"null"`` for nullable annotations.
"""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput
from dash.mcp.types import is_nullable

from .schema_component_proptypes import get_json_schema


def annotation_to_schema(param: MCPInput) -> dict[str, Any] | None:
    """Convert a callback parameter's type annotation to a JSON Schema dict.

    Returns ``None`` if the annotation is not recognised, meaning the
    caller should fall through to the next schema source.

    ``Optional[X]`` produces ``{"type": ["X", "null"]}`` — the user
    explicitly chose a nullable type.
    """
    annotation = param.get("annotation")
    if annotation is None:
        return None
    schema = get_json_schema(annotation)
    if schema is None:
        return None

    if is_nullable(annotation) and schema:
        t = schema.get("type")
        if isinstance(t, str):
            schema = {**schema, "type": [t, "null"]}
        elif isinstance(t, list) and "null" not in t:
            schema = {**schema, "type": [*t, "null"]}

    return schema
