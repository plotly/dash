"""Tool definition tests — MCP spec compliance and Dash conventions.

Verifies that generated tools conform to the MCP specification (2025-11-25)
and Dash-specific conventions. Focuses on shape/structure, not inputSchema
values (those are covered by input_schemas/).

Reference: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
"""

import re

from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)
from dash.mcp.primitives.tools.descriptions import build_tool_description

from tests.unit.mcp.conftest import (
    _make_app,
    _tools_list,
)

_TOOL_NAME_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")


class TestToolSpecCompliance:
    """Every tool must conform to the MCP 2025-11-25 specification."""

    def test_all_tools_conform_to_mcp_spec(self):
        tools = _tools_list(_make_app())
        names = [t.name for t in tools]

        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

        for tool in tools:
            assert tool.name
            assert tool.inputSchema
            assert 1 <= len(tool.name) <= 128
            assert _TOOL_NAME_RE.match(tool.name), f"Invalid tool name: {tool.name}"

            schema = tool.inputSchema
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            assert isinstance(schema.get("properties", {}), dict)

            required = set(schema.get("required", []))
            props = set(schema.get("properties", {}).keys())
            assert (
                required <= props
            ), f"{tool.name}: required {required - props} not in properties"


class TestBuiltinToolDefinitions:
    def _tools(self):
        return _tools_list(_make_app())

    def _builtin(self, name):
        return next(t for t in self._tools() if t.name == name)

    def test_query_component_always_present(self):
        names = {t.name for t in self._tools()}
        assert "get_dash_component" in names

    def test_query_component_has_required_params(self):
        tool = self._builtin("get_dash_component")
        assert "component_id" in tool.inputSchema["properties"]
        assert "property" in tool.inputSchema["properties"]
        assert set(tool.inputSchema.get("required", [])) == {"component_id"}


class TestSanitizeToolName:
    def test_simple_name(self):
        assert (
            CallbackAdapterCollection._sanitize_name("update_output") == "update_output"
        )

    def test_special_characters_replaced(self):
        assert (
            CallbackAdapterCollection._sanitize_name("my-func.name") == "my_func_name"
        )

    def test_leading_digit(self):
        assert CallbackAdapterCollection._sanitize_name("123func") == "cb_123func"

    def test_empty_name(self):
        assert CallbackAdapterCollection._sanitize_name("") == "unnamed_callback"

    def test_consecutive_underscores_collapsed(self):
        assert CallbackAdapterCollection._sanitize_name("a---b___c") == "a_b_c"

    def test_long_name_truncated_to_64_chars(self):
        result = CallbackAdapterCollection._sanitize_name("a" * 200)
        assert len(result) <= 64
        assert result[-8:].isalnum()

    def test_long_name_uniqueness(self):
        result_a = CallbackAdapterCollection._sanitize_name("a" * 200)
        result_b = CallbackAdapterCollection._sanitize_name("b" * 200)
        assert result_a != result_b

    def test_short_name_not_truncated(self):
        assert CallbackAdapterCollection._sanitize_name("short_name") == "short_name"


class TestOutputSemanticSummary:
    """Test the _OUTPUT_SEMANTICS mapping in description_outputs.py.

    Other description tests (docstring, output target, multi-output) are
    covered by TestTool in test_callback_adapter.py using real adapters.
    """

    @staticmethod
    def _adapter_with_outputs(outputs, docstring=None):
        from unittest.mock import Mock

        adapter = Mock()
        adapter.outputs = outputs
        adapter._docstring = docstring
        return adapter

    @staticmethod
    def _out(comp_id, prop, comp_type=None):
        return {
            "id_and_prop": f"{comp_id}.{prop}",
            "component_id": comp_id,
            "property": prop,
            "component_type": comp_type,
            "initial_value": None,
        }

    def test_semantic_summary_with_component_type(self):
        adapter = self._adapter_with_outputs([self._out("my-graph", "figure", "Graph")])
        desc = build_tool_description(adapter)
        assert "Returns chart/visualization data" in desc

    def test_semantic_summary_fallback_by_property(self):
        adapter = self._adapter_with_outputs([self._out("unknown-id", "figure")])
        desc = build_tool_description(adapter)
        assert "Returns chart/visualization data" in desc
