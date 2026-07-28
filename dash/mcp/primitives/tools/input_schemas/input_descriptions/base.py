"""Base class for per-parameter description sources."""

from __future__ import annotations

from dash.mcp.types import MCPInput


class InputDescriptionSource:
    """A source of text that can describe an MCP tool input parameter.

    Subclasses implement ``describe`` to return strings that will be
    added to the callback parameter's description. All sources
    are accumulated — every source can add text to the overall description.
    """

    @classmethod
    def describe(cls, param: MCPInput) -> list[str]:
        raise NotImplementedError
