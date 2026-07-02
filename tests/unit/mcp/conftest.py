"""Shared helpers for MCP unit tests."""

import sys

from dash import Dash, Input, Output, html
from dash._get_app import app_context

collect_ignore_glob = []
if sys.version_info < (3, 10):
    collect_ignore_glob.append("*")
else:
    from dash.mcp._decorator import (  # pylint: disable=wrong-import-position
        MCP_DECORATED_FUNCTIONS,
    )
    from dash.mcp.primitives.tools import (  # pylint: disable=wrong-import-position
        call_tool,
        list_tools,
    )
    from dash.mcp.primitives.tools.callback_adapter_collection import (  # pylint: disable=wrong-import-position
        CallbackAdapterCollection,
    )

BUILTINS = {"get_dash_component"}


def _setup_mcp(app):
    """Set up MCP for an app in tests."""
    app_context.set(app)
    if MCP_DECORATED_FUNCTIONS:
        app.mcp_decorated_functions = dict(MCP_DECORATED_FUNCTIONS)
        MCP_DECORATED_FUNCTIONS.clear()
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


def _make_app(**kwargs):
    """Create a minimal Dash app with a layout and one callback."""
    app = Dash(__name__, **kwargs)
    app.layout = html.Div(
        [
            html.Div(id="my-input"),
            html.Div(id="my-output"),
        ]
    )

    @app.callback(
        Output("my-output", "children"),
        Input("my-input", "children"),
        mcp_expose_docstring=True,
    )
    def update_output(value):
        """Test callback docstring."""
        return f"echo: {value}"

    return _setup_mcp(app)


def _tools_list(app):
    """Return all tools (callbacks + builtins) as Tool objects."""
    _setup_mcp(app)
    with app.server.test_request_context():
        return list_tools().tools


def _user_tool(tools):
    """Return the first tool that isn't a builtin."""
    return next(t for t in tools if t.name not in BUILTINS)


def _app_with_callback(component, input_prop="value", output_id="out"):
    """Create a Dash app with one callback using ``component`` as Input."""
    app = Dash(__name__)
    app.layout = html.Div([component, html.Div(id=output_id)])

    @app.callback(Output(output_id, "children"), Input(component.id, input_prop))
    def update(val):
        return f"got: {val}"

    return _setup_mcp(app)


def _schema_for(tool, param_name=None):
    """Extract the JSON schema dict for a parameter, without description."""
    props = tool.inputSchema["properties"]
    if param_name is None:
        param_name = next(iter(props))
    schema = dict(props[param_name])
    schema.pop("description", None)
    return schema


def _desc_for(tool, param_name=None):
    """Extract the description string for a parameter, or ''."""
    props = tool.inputSchema["properties"]
    if param_name is None:
        param_name = next(iter(props))
    return props[param_name].get("description", "")


def _call_tool(app, tool_name, arguments=None):
    """Call a tool via the dispatch pipeline and return the CallToolResult."""
    _setup_mcp(app)
    with app.server.test_request_context():
        return call_tool(tool_name, arguments or {})
