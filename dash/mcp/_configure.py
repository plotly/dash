"""Public configuration API for the Dash MCP server."""

# pylint: disable=cyclic-import
# dash.dash lazy-imports dash.mcp inside _setup_routes(); pylint's static
# analysis treats it as a module-level import, producing a false cycle.

from __future__ import annotations

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


def configure_mcp_server(
    *,
    include_layout: bool = True,
    include_callbacks: bool = True,
    include_clientside_callbacks: bool = True,
    include_pages: bool = True,
    expose_callback_docstrings: bool = False,
) -> None:
    """
    Configure which content the Dash MCP server exposes.

    Any parameter that is omitted will be reset to its default value. Calling
    with no args will reset all configuration to its default state.

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
        ...

    CallbackTools.callbacks_mcp_enabled_by_default = include_callbacks
    CallbackTools.expose_docstrings_by_default = expose_callback_docstrings

    updated_resources = list(_ALL_MCP_RESOURCE_PROVIDERS)
    if not include_layout:
        updated_resources.remove(LayoutResource)
        updated_resources.remove(ComponentsResource)
    if not include_clientside_callbacks:
        updated_resources.remove(ClientsideCallbacksResource)
    if not include_pages:
        updated_resources.remove(PagesResource)
        updated_resources.remove(PageLayoutResource)
    MCP_RESOURCE_PROVIDERS[:] = updated_resources

    updated_tools = list(_ALL_MCP_TOOL_PROVIDERS)
    if not include_layout:
        updated_tools.remove(GetDashComponentTool)
    MCP_TOOL_PROVIDERS[:] = updated_tools

    get_app().mcp_callback_map = None
