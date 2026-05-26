"""Tests for the public configure_mcp_server() API.

Covers:
- include_layout / include_clientside_callbacks / include_pages toggling resources
- include_layout toggling GetDashComponentTool
- include_callbacks toggling CallbackAdapterCollection filter mode
  (opt-out when True, opt-in when False)
- expose_callback_docstrings
- idempotency: re-calling configure_mcp restores providers
- cache invalidation: app.mcp_callback_map is cleared on configure_mcp
"""

import pytest

import dash._get_app as _get_app_module
from dash import Dash, Input, Output, dcc, html
from dash._get_app import app_context
from dash.mcp import configure_mcp_server
from dash.mcp.primitives.resources import _RESOURCE_PROVIDERS
from dash.mcp.primitives.resources.resource_clientside_callbacks import (
    ClientsideCallbacksResource,
)
from dash.mcp.primitives.resources.resource_components import ComponentsResource
from dash.mcp.primitives.resources.resource_layout import LayoutResource
from dash.mcp.primitives.resources.resource_page_layout import PageLayoutResource
from dash.mcp.primitives.resources.resource_pages import PagesResource
from dash.mcp.primitives.tools import _TOOL_PROVIDERS
from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)

from dash.mcp.primitives.tools.tool_get_dash_component import GetDashComponentTool
from dash.mcp.primitives.tools.tools_callbacks import CallbackTools


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_DEFAULT_RESOURCE_PROVIDERS = list(_RESOURCE_PROVIDERS)
_DEFAULT_TOOL_PROVIDERS = list(_TOOL_PROVIDERS)


@pytest.fixture(autouse=True)
def _reset_mcp_module_state():
    """Restore module-level MCP state after every test."""
    yield

    CallbackTools.callbacks_mcp_enabled_by_default = True
    CallbackTools.expose_docstrings_by_default = False
    _RESOURCE_PROVIDERS[:] = list(_DEFAULT_RESOURCE_PROVIDERS)
    _TOOL_PROVIDERS[:] = list(_DEFAULT_TOOL_PROVIDERS)
    _get_app_module.APP = None
    _get_app_module.app_context.set(None)


def _make_app(**cb_kwargs):
    """Minimal app with one callback. cb_kwargs forwarded to @app.callback."""
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "value"), **cb_kwargs)
    def update(val):
        """A callback docstring."""
        return val

    return app


def _collection(app):
    app_context.set(app)
    return CallbackAdapterCollection(app)


# ---------------------------------------------------------------------------
# Resources — include_layout
# ---------------------------------------------------------------------------


def test_mcpc001_include_layout_toggles_resources_and_tool():
    """include_layout=False removes LayoutResource, ComponentsResource, and
    GetDashComponentTool; re-enabling restores all three.  ClientsideCallbacks
    and pages providers are independent."""
    _make_app()

    configure_mcp_server(include_layout=False)

    assert LayoutResource not in _RESOURCE_PROVIDERS
    assert ComponentsResource not in _RESOURCE_PROVIDERS
    assert GetDashComponentTool not in _TOOL_PROVIDERS
    # Independent knobs are unaffected
    assert ClientsideCallbacksResource in _RESOURCE_PROVIDERS
    assert PagesResource in _RESOURCE_PROVIDERS

    configure_mcp_server(include_layout=True)

    assert LayoutResource in _RESOURCE_PROVIDERS
    assert ComponentsResource in _RESOURCE_PROVIDERS
    assert GetDashComponentTool in _TOOL_PROVIDERS


# ---------------------------------------------------------------------------
# Resources — include_clientside_callbacks
# ---------------------------------------------------------------------------


def test_mcpc002_include_clientside_callbacks_is_independent_knob():
    """include_clientside_callbacks=False removes only ClientsideCallbacksResource;
    layout resources are unaffected.  Restoring brings it back."""
    _make_app()

    configure_mcp_server(include_clientside_callbacks=False)

    assert ClientsideCallbacksResource not in _RESOURCE_PROVIDERS
    assert LayoutResource in _RESOURCE_PROVIDERS
    assert ComponentsResource in _RESOURCE_PROVIDERS

    configure_mcp_server(include_clientside_callbacks=True)

    assert ClientsideCallbacksResource in _RESOURCE_PROVIDERS


# ---------------------------------------------------------------------------
# Resources — include_pages
# ---------------------------------------------------------------------------


def test_mcpc003_include_pages_is_independent_knob():
    """include_pages=False removes PagesResource and PageLayoutResource;
    layout is unaffected."""
    _make_app()

    configure_mcp_server(include_pages=False)

    assert PagesResource not in _RESOURCE_PROVIDERS
    assert PageLayoutResource not in _RESOURCE_PROVIDERS
    assert LayoutResource in _RESOURCE_PROVIDERS


# ---------------------------------------------------------------------------
# Tools — include_callbacks filter mode
# ---------------------------------------------------------------------------


def test_mcpc004_include_callbacks_true_opt_out_mode():
    """include_callbacks=True (default): mcp_enabled=None includes;
    mcp_enabled=False excludes."""
    app_none = _make_app()  # mcp_enabled defaults to None
    configure_mcp_server(include_callbacks=True)
    assert len(_collection(app_none)) == 1

    app_false = _make_app(mcp_enabled=False)
    configure_mcp_server(include_callbacks=True)
    assert len(_collection(app_false)) == 0


def test_mcpc005_include_callbacks_false_opt_in_mode():
    """include_callbacks=False: mcp_enabled=True opts in;
    mcp_enabled=None or False both exclude (redundant False is valid)."""
    app_true = _make_app(mcp_enabled=True)
    configure_mcp_server(include_callbacks=False)
    assert len(_collection(app_true)) == 1

    app_none = _make_app()  # mcp_enabled=None
    configure_mcp_server(include_callbacks=False)
    assert len(_collection(app_none)) == 0

    app_false = _make_app(mcp_enabled=False)
    configure_mcp_server(include_callbacks=False)
    assert len(_collection(app_false)) == 0


# ---------------------------------------------------------------------------
# expose_callback_docstrings
# ---------------------------------------------------------------------------


def test_mcpc006_expose_callback_docstrings():
    """expose_callback_docstrings=True exposes docstrings; False hides them."""
    app = _make_app()
    configure_mcp_server(expose_callback_docstrings=True)
    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    with app.server.test_request_context():
        tool = app.mcp_callback_map[0].as_mcp_tool
    assert "A callback docstring." in tool.description

    app2 = _make_app()
    configure_mcp_server(expose_callback_docstrings=False)
    app_context.set(app2)
    app2.mcp_callback_map = CallbackAdapterCollection(app2)
    with app2.server.test_request_context():
        tool2 = app2.mcp_callback_map[0].as_mcp_tool
    assert "A callback docstring." not in tool2.description


def test_mcpc008_per_callback_false_overrides_server_level_docstrings():
    """Per-callback mcp_expose_docstring=False wins over configure_mcp_server opt-in."""
    app = _make_app(mcp_expose_docstring=False)
    configure_mcp_server(expose_callback_docstrings=True)
    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    with app.server.test_request_context():
        tool = app.mcp_callback_map[0].as_mcp_tool
    assert "A callback docstring." not in tool.description


# ---------------------------------------------------------------------------
# Cache invalidation
# ---------------------------------------------------------------------------


def test_mcpc007_configure_mcp_invalidates_mcp_callback_map():
    """configure_mcp clears app.mcp_callback_map so it is rebuilt with new config."""
    app = _make_app()
    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    assert len(app.mcp_callback_map) == 1

    configure_mcp_server(include_callbacks=False)

    assert app.mcp_callback_map is None
