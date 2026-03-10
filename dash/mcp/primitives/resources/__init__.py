"""MCP resource listing and read handling.

Each resource module exports:
- ``URI`` — the URI prefix this module handles
- ``get_resource() -> Resource | None``
- ``get_template() -> ResourceTemplate | None``
- ``read_resource(uri) -> ReadResourceResult``

Dispatch is by prefix match: more specific prefixes must come first.
"""

from __future__ import annotations

from mcp.types import (
    ListResourcesResult,
    ListResourceTemplatesResult,
    ReadResourceResult,
)

from . import (
    resource_clientside_callbacks as _clientside,
    resource_components as _components,
    resource_layout as _layout,
    resource_page_layout as _page_layout,
    resource_pages as _pages,
)

_RESOURCE_MODULES = [_layout, _components, _pages, _clientside, _page_layout]


def list_resources() -> ListResourcesResult:
    """Build the MCP resources/list response."""
    resources = [
        r for mod in _RESOURCE_MODULES for r in [mod.get_resource()] if r is not None
    ]
    return ListResourcesResult(resources=resources)


def list_resource_templates() -> ListResourceTemplatesResult:
    """Build the MCP resources/templates/list response."""
    templates = [
        t for mod in _RESOURCE_MODULES for t in [mod.get_template()] if t is not None
    ]
    return ListResourceTemplatesResult(resourceTemplates=templates)


def read_resource(uri: str) -> ReadResourceResult:
    """Dispatch a resources/read request by URI prefix match."""
    for mod in _RESOURCE_MODULES:
        if uri.startswith(mod.URI):
            return mod.read_resource(uri)
    raise ValueError(f"Unknown resource URI: {uri}")
