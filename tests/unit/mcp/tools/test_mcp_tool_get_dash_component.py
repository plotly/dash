"""The built-in ``get_dash_component`` tool.

Lets LLMs inspect a component's current properties and their relationships
to callbacks (which tools write/read each prop).
"""

import json

from dash import Dash, Input, Output, dcc, html

from tests.unit.mcp.conftest import _call_tool, _make_app, _tools_list


def test_mcpg001_present_in_tools_list():
    app = _make_app()
    tool_names = [t.name for t in _tools_list(app)]
    assert "get_dash_component" in tool_names


def test_mcpg002_returns_structured_output_with_prop():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="my-dd", options=["a", "b"], value="b"),
        ]
    )

    result = _call_tool(
        app,
        "get_dash_component",
        {
            "component_id": "my-dd",
            "property": "value",
        },
    )
    sc = result.structuredContent
    assert sc["component_id"] == "my-dd"
    assert sc["component_type"] == "Dropdown"
    assert "value" in sc["properties"]
    assert sc["properties"]["value"]["initial_value"] == "b"
    assert "options" not in sc["properties"]


def test_mcpg003_returns_all_props_without_property():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="my-dd", options=["a", "b"], value="b"),
        ]
    )

    result = _call_tool(
        app,
        "get_dash_component",
        {
            "component_id": "my-dd",
        },
    )
    sc = result.structuredContent
    assert "options" in sc["properties"]
    assert "value" in sc["properties"]
    assert sc["properties"]["value"]["initial_value"] == "b"


def test_mcpg004_includes_label():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Pick one", htmlFor="my-dd"),
            dcc.Dropdown(id="my-dd", options=["a", "b"], value="a"),
        ]
    )

    @app.callback(Output("my-dd", "value"), Input("my-dd", "options"))
    def noop(o):
        return "a"

    result = _call_tool(
        app,
        "get_dash_component",
        {
            "component_id": "my-dd",
        },
    )
    sc = result.structuredContent
    assert sc["label"] == ["Pick one"]


def test_mcpg005_includes_tool_references():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dd", options=["a", "b"], value="a"),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input("dd", "value"))
    def update(val):
        return val

    result = _call_tool(
        app,
        "get_dash_component",
        {
            "component_id": "dd",
            "property": "value",
        },
    )
    prop_info = result.structuredContent["properties"]["value"]
    assert "update" in prop_info["input_to_tool"]


def test_mcpg006_missing_id_returns_hint():
    app = _make_app()
    result = _call_tool(
        app,
        "get_dash_component",
        {
            "component_id": "nonexistent",
            "property": "value",
        },
    )
    text = result.content[0].text
    assert "nonexistent" in text
    assert "not found" in text
    assert "dash://components" in text


def test_mcpg007_nested_children_are_serializable_on_mcp_wire():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                id="container",
                children=[
                    html.H1("Heading"),
                    html.Div([html.Span("Nested"), " suffix"]),
                ],
            )
        ]
    )

    result = _call_tool(app, "get_dash_component", {"component_id": "container"})

    # This is the Pydantic JSON-mode conversion used by the MCP dispatcher.
    wire = result.model_dump(exclude_none=True, mode="json")
    structured = wire["structuredContent"]
    children = structured["properties"]["children"]["initial_value"]
    assert children[0]["type"] == "H1"
    assert children[0]["props"]["children"] == "Heading"
    assert children[1]["type"] == "Div"
    assert children[1]["props"]["children"][0]["type"] == "Span"
    assert children[1]["props"]["children"][0]["props"]["children"] == "Nested"
    assert children[1]["props"]["children"][1] == " suffix"
    assert json.loads(result.content[0].text) == structured


def test_mcpg008_single_component_child_and_prop_filter_are_serializable():
    app = Dash(__name__)
    app.layout = html.Div([html.Div(html.H2("Title"), id="container")])

    result = _call_tool(
        app, "get_dash_component", {"component_id": "container", "property": "children"}
    )

    wire = result.model_dump(exclude_none=True, mode="json")
    properties = wire["structuredContent"]["properties"]
    assert list(properties) == ["children"]
    assert properties["children"]["initial_value"]["type"] == "H2"
    assert properties["children"]["initial_value"]["props"]["children"] == "Title"
    assert json.loads(result.content[0].text) == wire["structuredContent"]
