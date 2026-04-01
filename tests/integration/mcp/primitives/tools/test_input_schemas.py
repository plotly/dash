"""
Integration tests for MCP tool schema generation.

Starts a real Dash server via ``dash_duo`` and verifies that tools
are generated with correct inputSchema, descriptions, and labels.
"""

from dash import Dash, Input, Output, dcc, html

from tests.integration.mcp.conftest import _mcp_tools


def test_mcp_tool_with_label_and_date_picker_schema(dash_duo):
    """Full assertion on a tool with an html.Label and DatePickerSingle constraints."""

    # -- Test data: change these to update the test --
    label_text = "Departure Date"
    component_id = "dp"
    min_date = "2020-01-01"
    max_date = "2025-12-31"
    default_date = "2024-06-15"
    func_name = "select_date"
    param_name = "date"  # function parameter name

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label(label_text, htmlFor=component_id),
            dcc.DatePickerSingle(
                id=component_id,
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                date=default_date,
            ),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), Input(component_id, "date"))
    def select_date(date):
        return f"Selected: {date}"

    dash_duo.start_server(app)
    tools = _mcp_tools(dash_duo.server.url)

    # Find the callback tool
    tool = next(t for t in tools if t["name"] not in ("get_dash_component",))

    # -- Tool-level fields --
    assert func_name in tool["name"]

    # -- inputSchema structure --
    schema = tool["inputSchema"]
    assert schema["type"] == "object"
    assert param_name in schema["required"]
    assert param_name in schema["properties"]

    # -- Property schema: type + format + description --
    prop = schema["properties"][param_name]
    assert prop["type"] == "string"
    assert prop["format"] == "date"

    # description includes all source values (label, constraints, default)
    desc = prop["description"]
    for expected in (label_text, min_date, max_date, default_date):
        assert expected in desc, f"Expected {expected!r} in description: {desc!r}"
