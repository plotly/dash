"""Base class for MCP resource providers."""

from __future__ import annotations

from mcp.types import ReadResourceResult, Resource, ResourceTemplate


class MCPResourceProvider:
    """Base class for MCP resource providers.

    Subclasses must set ``uri`` and implement ``read_resource``.
    Override ``get_resource`` and/or ``get_template`` to advertise
    the resource in ``resources/list`` or ``resources/templates/list``.
    """

    uri: str

    @classmethod
    def get_resource(cls) -> Resource | None:
        return None

    @classmethod
    def get_template(cls) -> ResourceTemplate | None:
        return None

    @classmethod
    def read_resource(cls, uri: str) -> ReadResourceResult:
        raise NotImplementedError
