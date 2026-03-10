"""Tool schema tests — what a Dash MCP tool looks like.

The EXPECTED_TOOL dict below is the canonical reference for the shape of
a callback-generated MCP tool. It doubles as human-readable documentation
and as a test fixture.

Reference: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
"""

from tests.unit.mcp.conftest import (
    _make_app,
    _tools_list,
    _user_tool,
)

from pydantic import TypeAdapter
from dash.development.base_component import Component
from dash.types import CallbackDispatchResponse

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
    "outputSchema": TypeAdapter(CallbackDispatchResponse).json_schema(),
}


class TestToolSchema:
    """Verify that the generated tool matches EXPECTED_TOOL exactly."""

    def test_full_tool(self):
        """The entire tool dict matches the expected shape."""
        tool = _user_tool(_tools_list(_make_app()))
        assert tool == EXPECTED_TOOL


class TestCallbackToolShape:
    """Dash callback tools follow specific naming and description conventions."""

    def _callback_tool(self):
        return _user_tool(_tools_list(_make_app()))

    def test_name_matches_function_name(self):
        tool = self._callback_tool()
        assert tool["name"] == "update_output"

    def test_description_present(self):
        tool = self._callback_tool()
        assert isinstance(tool["description"], str)
        assert len(tool["description"]) > 0

    def test_description_has_output_summary(self):
        """First line is a semantic summary of what the callback returns."""
        tool = self._callback_tool()
        first_line = tool["description"].split("\n")[0]
        assert "Returns content" in first_line

    def test_description_has_docstring(self):
        tool = self._callback_tool()
        assert "Test callback docstring" in tool["description"]

    def test_description_has_output_target(self):
        tool = self._callback_tool()
        assert "my-output.children" in tool["description"]

    def test_param_names_match_function_args(self):
        tool = self._callback_tool()
        assert "value" in tool["inputSchema"]["properties"]
