"""Integration tests for the get_dash_component tool."""

from dash import Dash, dcc, html

from tests.integration.mcp.conftest import _mcp_call_tool

EXPECTED_DROPDOWN_OPTIONS = {
    "component_id": "my-dropdown",
    "component_type": "Dropdown",
    "label": None,
    "properties": {
        "options": {
            "initial_value": [
                {"label": "New York", "value": "NYC"},
                {"label": "Montreal", "value": "MTL"},
            ],
            "modified_by_tool": [],
            "input_to_tool": [],
        },
    },
}


def test_query_component_returns_structured_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="my-dropdown",
                options=[
                    {"label": "New York", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                ],
                value="NYC",
            ),
        ]
    )

    dash_duo.start_server(app)

    result = _mcp_call_tool(
        dash_duo.server.url,
        "get_dash_component",
        {"component_id": "my-dropdown", "property": "options"},
    )

    assert "result" in result, f"Expected result in response: {result}"
    structured = result["result"]["structuredContent"]
    assert structured["component_id"] == EXPECTED_DROPDOWN_OPTIONS["component_id"]
    assert structured["component_type"] == EXPECTED_DROPDOWN_OPTIONS["component_type"]
    assert (
        structured["properties"]["options"]
        == EXPECTED_DROPDOWN_OPTIONS["properties"]["options"]
    )
