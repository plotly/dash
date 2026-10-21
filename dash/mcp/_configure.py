"""Public configuration API for the Dash MCP server."""

# pylint: disable=cyclic-import
# dash.dash lazy-imports dash.mcp inside _setup_routes(); pylint's static
# analysis treats it as a module-level import, producing a false cycle.

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Union

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

_DEFAULT_CONFIG: Dict[str, Any] = {
    "include_layout": True,
    "include_callbacks": True,
    "include_clientside_callbacks": True,
    "include_pages": True,
    "expose_callback_docstrings": False,
    "cache_by": [],
    "cache_maxsize": 128,
}
_current_config: Dict[str, Any] = dict(_DEFAULT_CONFIG)

# None is a meaningful cache_maxsize (no limit), so "not passed" needs its own value.
_UNSET: Any = object()


def configure_mcp_server(
    *,
    include_layout: Optional[bool] = None,
    include_callbacks: Optional[bool] = None,
    include_clientside_callbacks: Optional[bool] = None,
    include_pages: Optional[bool] = None,
    expose_callback_docstrings: Optional[bool] = None,
    cache_by: Optional[Union[Callable[[], object], List[Callable[[], object]]]] = None,
    cache_maxsize: Optional[int] = _UNSET,
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
    :param cache_by: Zero-argument functions, called during each MCP request,
        whose return values key the server's cache of tool descriptions and
        initial values (computed by walking the layout and running callbacks).
        By default one cache is shared by every MCP client. If your layout or
        callbacks depend on who is asking, pass a function that returns the
        user or session id (a string or int) so each user gets their own
        values, the same way ``cache_by`` works for background callbacks.
    :param cache_maxsize: How many ``cache_by`` keys (for example users) keep
        a cache at once; the least recently used is dropped past that.
        Defaults to ``128``. ``None`` keeps every key for the life of the
        process.

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
        "cache_by": [cache_by] if callable(cache_by) else cache_by,
    }
    _current_config.update(
        {key: value for key, value in passed.items() if value is not None}
    )
    if cache_maxsize is not _UNSET:
        _current_config["cache_maxsize"] = cache_maxsize

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

    # Invalidate the cached callback maps so they are rebuilt with the new config.
    # No app yet (configured before `Dash()`) means there is no cache to clear.
    try:
        app = get_app()
    except AppNotFoundError:
        return
    app.mcp_callback_map = None
    with app._mcp_callback_maps_lock:  # pylint: disable=protected-access
        app._mcp_callback_maps.clear()  # pylint: disable=protected-access
