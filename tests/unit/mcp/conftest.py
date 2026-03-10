"""Shared helpers for MCP unit tests."""

import json

from dash import Dash, Input, Output, html
from dash._get_app import app_context
from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)
from dash.mcp._server import _process_mcp_message

BUILTINS = {"get_dash_component"}


# ---------------------------------------------------------------------------
# Helpers moved from test_mcp.py
# ---------------------------------------------------------------------------


def _setup_mcp(app):
    """Set up MCP for an app in tests."""
    app_context.set(app)
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

    @app.callback(Output("my-output", "children"), Input("my-input", "children"))
    def update_output(value):
        """Test callback docstring."""
        return f"echo: {value}"

    return _setup_mcp(app)


def _msg(method, params=None, request_id=1):
    """Build a JSON-RPC message dict."""
    d = {"jsonrpc": "2.0", "method": method, "id": request_id}
    if params is not None:
        d["params"] = params
    else:
        d["params"] = {}
    return d


def _mcp(app, method, params=None, request_id=1):
    """Send an MCP message inside the app's Flask request context."""
    with app.server.test_request_context():
        _setup_mcp(app)
        return _process_mcp_message(_msg(method, params, request_id))


def _tools_list(app):
    """Return the tools list from a tools/list call."""
    return _mcp(app, "tools/list")["result"]["tools"]


def _call_tool(app, tool_name, arguments=None, request_id=1):
    """Call a tool and return the parsed JSON-RPC response."""
    return _mcp(
        app, "tools/call", {"name": tool_name, "arguments": arguments or {}}, request_id
    )


def _call_tool_text(app, tool_name, arguments=None):
    """Call a tool and return its parsed text content."""
    result = _call_tool(app, tool_name, arguments)
    return json.loads(result["result"]["content"][0]["text"])


def _call_tool_structured(app, tool_name, arguments=None):
    """Call a callback tool and return the structuredContent (dispatch response)."""
    result = _call_tool(app, tool_name, arguments)
    return result["result"]["structuredContent"]


def _call_tool_output(
    app, tool_name, arguments=None, component_id=None, prop="children"
):
    """Call a callback tool and return a specific output value.

    If *component_id* is omitted, returns the first component's prop value.
    """
    structured = _call_tool_structured(app, tool_name, arguments)
    response = structured["response"]
    if component_id is None:
        component_id = next(iter(response))
    return response[component_id][prop]


def _make_pages_app(validation_layout=None):
    """Create a Dash app configured for page-layout tests."""
    app = Dash(__name__)
    app.layout = html.Div(id="main-shell")
    app.validation_layout = validation_layout
    app_context.set(app)
    return app


# ---------------------------------------------------------------------------
# New helpers for schema tests
# ---------------------------------------------------------------------------


def _user_tool(tools):
    """Return the first tool that isn't a builtin."""
    return next(t for t in tools if t["name"] not in BUILTINS)


def _app_with_callback(component, input_prop="value", output_id="out"):
    """Create a Dash app with one callback using ``component`` as Input."""
    app = Dash(__name__)
    app.layout = html.Div([component, html.Div(id=output_id)])

    @app.callback(Output(output_id, "children"), Input(component.id, input_prop))
    def update(val):
        return f"got: {val}"

    return _setup_mcp(app)


def _schema_for(tool, param_name=None):
    """Extract the JSON schema dict for a parameter, without description.

    If *param_name* is omitted, returns the schema for the first property.
    """
    props = tool["inputSchema"]["properties"]
    if param_name is None:
        param_name = next(iter(props))
    schema = dict(props[param_name])
    schema.pop("description", None)
    return schema


def _desc_for(tool, param_name=None):
    """Extract the description string for a parameter, or ''.

    If *param_name* is omitted, returns the description for the first property.
    """
    props = tool["inputSchema"]["properties"]
    if param_name is None:
        param_name = next(iter(props))
    return props[param_name].get("description", "")
