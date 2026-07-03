"""Tool construction: how Dash callbacks become MCP Tool objects.

Covers the CallbackAdapter → Tool pipeline: list building (from_app),
tool name generation, and the resulting Tool object's shape (description,
input schema, param metadata).

Reference: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
"""

import pytest
from dash import Dash, Input, Output, State, dcc, html
from dash._get_app import app_context
from dash.development.base_component import Component
from dash.types import CallbackExecutionResponse
from dash.mcp.types import Tool
from pydantic import TypeAdapter

from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)

from tests.unit.mcp.conftest import (
    _make_app,
    _tools_list,
    _user_tool,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Your Name", htmlFor="inp"),
            dcc.Input(id="inp", type="text"),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val):
        """Update output."""
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def multi_output_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a", "b"], value="a"),
            dcc.Dropdown(id="dd2"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("dd2", "options"),
        Output("out", "children"),
        Input("dd", "value"),
    )
    def update(val):
        return [], val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def state_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            dcc.Input(id="inp"),
            html.Div(id="out"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        State("inp", "value"),
    )
    def update(clicks, val):
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def typed_app():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val: str):
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


@pytest.fixture
def duplicate_names_app():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="in1"),
            html.Div(id="out1"),
            html.Div(id="in2"),
            html.Div(id="out2"),
        ]
    )

    @app.callback(Output("out1", "children"), Input("in1", "children"))
    def cb(v):
        return v

    @app.callback(Output("out2", "children"), Input("in2", "children"))
    def cb(v):  # noqa: F811
        return v

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    return app


# ---------------------------------------------------------------------------
# Tests — building the callback list from an app
# ---------------------------------------------------------------------------


def test_mcpt001_returns_list(simple_app):
    assert len(app_context.get().mcp_callback_map) == 1


def test_mcpt002_excludes_clientside():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(id="btn"),
            html.Div(id="cs-out"),
            html.Div(id="srv-out"),
        ]
    )
    app.clientside_callback(
        "function(n) { return n; }",
        Output("cs-out", "children"),
        Input("btn", "n_clicks"),
    )

    @app.callback(Output("srv-out", "children"), Input("btn", "n_clicks"))
    def server_cb(n):
        return str(n)

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)

    names = [a.tool_name for a in app.mcp_callback_map]
    assert names == ["server_cb"]


def test_mcpt003_excludes_mcp_disabled():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id="inp"),
            html.Div(id="out1"),
            html.Div(id="out2"),
        ]
    )

    @app.callback(Output("out1", "children"), Input("inp", "value"))
    def visible(val):
        return val

    @app.callback(Output("out2", "children"), Input("inp", "value"), mcp_enabled=False)
    def hidden(val):
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)
    names = [a.tool_name for a in app.mcp_callback_map]
    assert "visible" in names
    assert "hidden" not in names


# ---------------------------------------------------------------------------
# Tests — tool name generation
# ---------------------------------------------------------------------------


def test_mcpt004_uses_func_name(simple_app):
    assert app_context.get().mcp_callback_map[0].tool_name == "update"


def test_mcpt005_duplicates_get_unique_names(duplicate_names_app):
    names = [a.tool_name for a in app_context.get().mcp_callback_map]
    assert len(names) == 2
    assert names[0] != names[1]


# ---------------------------------------------------------------------------
# Tests — Tool object shape (description, input schema, params)
# ---------------------------------------------------------------------------


def test_mcpt006_returns_tool_instance(simple_app):
    with simple_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    assert isinstance(tool, Tool)
    assert tool.name == "update"


def test_mcpt007_docstring_hidden_by_default():
    """Callback docstrings are not exposed to MCP by default."""
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("inp", "value"))
    def update(val):
        """sensitive callback docstring text that must not leak to LLMs"""
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)

    with app.server.test_request_context():
        tool = app.mcp_callback_map[0].as_mcp_tool
    assert (
        "sensitive callback docstring text that must not leak to LLMs"
        not in tool.description
    )


def test_mcpt008_docstring_exposed_when_opted_in_per_callback():
    app = Dash(__name__)
    app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

    @app.callback(
        Output("out", "children"),
        Input("inp", "value"),
        mcp_expose_docstring=True,
    )
    def update(val):
        """intentionally-exposed callback docstring text for the LLM"""
        return val

    app_context.set(app)
    app.mcp_callback_map = CallbackAdapterCollection(app)

    with app.server.test_request_context():
        tool = app.mcp_callback_map[0].as_mcp_tool
    assert (
        "intentionally-exposed callback docstring text for the LLM" in tool.description
    )


def test_mcpt009_description_includes_output_target(simple_app):
    with simple_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    assert "out.children" in tool.description


def test_mcpt010_param_name_from_function_signature(simple_app):
    with simple_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    assert "val" in tool.inputSchema["properties"]


def test_mcpt011_param_has_label_description(simple_app):
    with simple_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    desc = tool.inputSchema["properties"]["val"].get("description", "")
    assert "Your Name" in desc


def test_mcpt012_state_params_included(state_app):
    with state_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    props = tool.inputSchema["properties"]
    assert set(props.keys()) == {"clicks", "val"}


def test_mcpt013_multi_output_description(multi_output_app):
    with multi_output_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    assert "dd2.options" in tool.description
    assert "out.children" in tool.description


def test_mcpt014_typed_annotation_narrows_schema(typed_app):
    with typed_app.server.test_request_context():
        tool = app_context.get().mcp_callback_map[0].as_mcp_tool
    assert tool.inputSchema["properties"]["val"]["type"] == "string"


# ---------------------------------------------------------------------------
# Tests — end-to-end Tool shape
# ---------------------------------------------------------------------------


_DASH_COMPONENT_SCHEMA = TypeAdapter(Component).json_schema()

EXPECTED_TOOL = {
    "name": "update_output",
    "description": (
        "my-output.children: Returns content\n" "\n" "Test callback docstring."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "value": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "integer"},
                    {"type": "number"},
                    _DASH_COMPONENT_SCHEMA,
                    {
                        "items": {
                            "anyOf": [
                                {"type": "string"},
                                {"type": "integer"},
                                {"type": "number"},
                                _DASH_COMPONENT_SCHEMA,
                                {"type": "null"},
                            ]
                        },
                        "type": "array",
                    },
                    {"type": "null"},
                ],
                "description": "Input is optional.\nThe children of this component.",
            },
        },
    },
    "outputSchema": TypeAdapter(CallbackExecutionResponse).json_schema(),
}


def test_mcpt015_full_tool():
    """The entire tool dict matches the expected shape end-to-end."""
    tool = _user_tool(_tools_list(_make_app()))
    assert tool.model_dump(exclude_none=True) == EXPECTED_TOOL
