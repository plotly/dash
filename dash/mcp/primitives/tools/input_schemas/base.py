"""Base class for input schema sources."""

from __future__ import annotations

from typing import Any

from dash.mcp.types import MCPInput


class InputSchemaSource:
    """A source of JSON Schema that can type an MCP tool input parameter.

    Subclasses implement ``get_schema`` to return a JSON Schema dict
    for the parameter, or ``None`` if this source cannot determine the
    type. Sources are tried in priority order — first non-None wins.
    """

    @classmethod
    def get_schema(cls, param: MCPInput) -> dict[str, Any] | None:
        raise NotImplementedError
