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
        assert tool.model_dump(exclude_none=True) == EXPECTED_TOOL
