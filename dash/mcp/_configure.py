"""Public configuration API for the Dash MCP server."""

# pylint: disable=cyclic-import
# dash.dash lazy-imports dash.mcp inside _setup_routes(); pylint's static
# analysis treats it as a module-level import, producing a false cycle.

from __future__ import annotations

from typing import Optional

from dash import get_app
from dash.exceptions import AppNotFoundError
from dash.mcp.primitives.resources import _RESOURCE_PROVIDERS as MCP_RESOURCE_PROVIDERS
from dash.mcp.primitives.resources.resource_clientside_callbacks import (
    ClientsideCallbacksResource,
)
from dash.mcp.primitives.resources.resource_components import ComponentsResource
from dash.mcp.primitives.resources.resource_layout import LayoutResource
from dash.mcp.primitives.resources.resource_page_layout import PageLayoutResource
from dash.mcp.primitives.resources.resource_pages import PagesResource
from dash.mcp.primitives.tools import _TOOL_PROVIDERS as MCP_TOOL_PROVIDERS
from dash.mcp.primitives.tools.tool_get_dash_component import GetDashComponentTool
from dash.mcp.primitives.tools.tools_callbacks import CallbackTools

_ALL_MCP_RESOURCE_PROVIDERS = list(MCP_RESOURCE_PROVIDERS)
_ALL_MCP_TOOL_PROVIDERS = list(MCP_TOOL_PROVIDERS)

# Membership groupings (order-independent): which providers each toggle
# controls. The exposed order is owned solely by the registry lists.
_LAYOUT_RESOURCES = {LayoutResource, ComponentsResource}
_CLIENTSIDE_CALLBACK_RESOURCES = {ClientsideCallbacksResource}
_PAGE_RESOURCES = {PagesResource, PageLayoutResource}
_LAYOUT_TOOLS = {GetDashComponentTool}

_DEFAULT_CONFIG = {
    "include_layout": True,
    "include_callbacks": True,
    "include_clientside_callbacks": True,
    "include_pages": True,
    "expose_callback_docstrings": False,
}
_current_config = dict(_DEFAULT_CONFIG)


def configure_mcp_server(
    *,
    include_layout: Optional[bool] = None,
    include_callbacks: Optional[bool] = None,
    include_clientside_callbacks: Optional[bool] = None,
    include_pages: Optional[bool] = None,
    expose_callback_docstrings: Optional[bool] = None,
) -> None:
    """
    Configure which content the Dash MCP server exposes.

    Only the parameters that are explicitly passed are updated; any parameter
    that is omitted keeps its current value. On the first call, unset values
    take their defaults (all content included except callback docstrings).

    :param include_layout: Expose ``dash://layout``, ``dash://components``,
        and the ``get_dash_component`` tool.  Defaults to ``True``.
    :param include_callbacks: When ``True`` (default), all callbacks are
        included; ``mcp_enabled=False`` on a ``@callback`` opts it out.
        When ``False``, no callbacks are included by default;
        ``mcp_enabled=True`` opts a specific callback in.
    :param include_clientside_callbacks: Expose the
        ``dash://clientside-callbacks`` resource.  Defaults to ``True``.
    :param include_pages: Expose ``dash://pages`` and
        ``dash://page-layout/{path}``.  Defaults to ``True``.
    :param expose_callback_docstrings: Include callback docstrings in
        tool descriptions.  Defaults to ``False``.

    Example — expose only ``@mcp_enabled``-decorated functions::

        from dash.mcp import configure_mcp_server

        configure_mcp_server(
            include_layout=False,
            include_callbacks=False,
            include_clientside_callbacks=False,
            include_pages=False,
        )
    """
    try:
        if get_app().backend.has_request_context():
            raise RuntimeError("MCP server can't be configured within a callback")
    except AppNotFoundError:
        pass

    passed = {
        "include_layout": include_layout,
        "include_callbacks": include_callbacks,
        "include_clientside_callbacks": include_clientside_callbacks,
        "include_pages": include_pages,
        "expose_callback_docstrings": expose_callback_docstrings,
    }
    _current_config.update(
        {key: value for key, value in passed.items() if value is not None}
    )

    CallbackTools.callbacks_mcp_enabled_by_default = _current_config[
        "include_callbacks"
    ]
    CallbackTools.expose_docstrings_by_default = _current_config[
        "expose_callback_docstrings"
    ]

    excluded_resources: set = set()
    if not _current_config["include_layout"]:
        excluded_resources |= _LAYOUT_RESOURCES
    if not _current_config["include_clientside_callbacks"]:
        excluded_resources |= _CLIENTSIDE_CALLBACK_RESOURCES
    if not _current_config["include_pages"]:
        excluded_resources |= _PAGE_RESOURCES
    MCP_RESOURCE_PROVIDERS[:] = [
        resource
        for resource in _ALL_MCP_RESOURCE_PROVIDERS
        if resource not in excluded_resources
    ]

    excluded_tools: set = set()
    if not _current_config["include_layout"]:
        excluded_tools |= _LAYOUT_TOOLS
    MCP_TOOL_PROVIDERS[:] = [
        tool for tool in _ALL_MCP_TOOL_PROVIDERS if tool not in excluded_tools
    ]

    # Invalidate the cached callback map so it is rebuilt with the new config.
    # No app yet (configured before `Dash()`) means there is no cache to clear.
    try:
        get_app().mcp_callback_map = None
    except AppNotFoundError:
        pass
