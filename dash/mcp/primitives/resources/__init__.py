"""MCP resource listing and read handling."""

from __future__ import annotations

from mcp.types import (
    ListResourcesResult,
    ListResourceTemplatesResult,
    ReadResourceResult,
)

from .base import MCPResourceProvider
from .resource_clientside_callbacks import ClientsideCallbacksResource
from .resource_components import ComponentsResource
from .resource_layout import LayoutResource
from .resource_page_layout import PageLayoutResource
from .resource_pages import PagesResource

_RESOURCE_PROVIDERS: list[type[MCPResourceProvider]] = [
    LayoutResource,
    ComponentsResource,
    PagesResource,
    ClientsideCallbacksResource,
    PageLayoutResource,
]


def list_resources() -> ListResourcesResult:
    """Build the MCP resources/list response."""
    resources = [
        r for p in _RESOURCE_PROVIDERS for r in [p.get_resource()] if r is not None
    ]
    return ListResourcesResult(resources=resources)


def list_resource_templates() -> ListResourceTemplatesResult:
    """Build the MCP resources/templates/list response."""
    templates = [
        t for p in _RESOURCE_PROVIDERS for t in [p.get_template()] if t is not None
    ]
    return ListResourceTemplatesResult(resourceTemplates=templates)


def read_resource(uri: str) -> ReadResourceResult:
    """Route a resources/read request by URI prefix match."""
    for p in _RESOURCE_PROVIDERS:
        if uri.startswith(p.uri):
            return p.read_resource(uri)
    raise ValueError(f"Unknown resource URI: {uri}")
