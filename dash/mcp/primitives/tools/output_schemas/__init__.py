"""Output schema generation for MCP tool outputSchema fields.

Mirrors ``input_schemas/`` which generates ``inputSchema``.

Each source shares the same signature: ``() -> dict | None``.
"""

from __future__ import annotations

from typing import Any

from .schema_callback_response import callback_response_schema

_SOURCES = [
    callback_response_schema,
]


def get_output_schema() -> dict[str, Any]:
    """Return the JSON Schema for a callback tool's output.

    Tries each source in order, returning the first non-None result.
    Falls back to ``{}`` (any type).
    """
    for source in _SOURCES:
        schema = source()
        if schema is not None:
            return schema
    return {}
