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

# MCP spec: allowed characters in tool names
_TOOL_NAME_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")


# ---------------------------------------------------------------------------
# MCP spec compliance (applies to ALL tools, including builtins)
# ---------------------------------------------------------------------------


class TestToolSpecCompliance:
    """Every tool must conform to the MCP 2025-11-25 specification.

    Reference: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
    """

    def test_all_tools_conform_to_mcp_spec(self):
        """Each tool has required fields, valid name, and well-formed inputSchema."""
        tools = _tools_list(_make_app())
        names = [t["name"] for t in tools]

        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

        for tool in tools:
            name = tool["name"]
            assert "name" in tool
            assert "inputSchema" in tool
            assert 1 <= len(name) <= 128
            assert _TOOL_NAME_RE.match(name), f"Invalid tool name: {name}"

            schema = tool["inputSchema"]
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            assert isinstance(schema.get("properties", {}), dict)

            required = set(schema.get("required", []))
            props = set(schema.get("properties", {}).keys())
            assert (
                required <= props
            ), f"{name}: required {required - props} not in properties"


# ---------------------------------------------------------------------------
# Builtin tool definitions
# ---------------------------------------------------------------------------


class TestBuiltinToolDefinitions:
    def _tools(self):
        return _tools_list(_make_app())

    def _builtin(self, name):
        return next(t for t in self._tools() if t["name"] == name)

    def test_query_component_always_present(self):
        names = {t["name"] for t in self._tools()}
        assert "get_dash_component" in names

    def test_query_component_has_required_params(self):
        tool = self._builtin("get_dash_component")
        schema = tool["inputSchema"]
        assert "component_id" in schema["properties"]
        assert "property" in schema["properties"]
        assert set(schema.get("required", [])) == {"component_id"}


# ---------------------------------------------------------------------------
# Tool name sanitization
# ---------------------------------------------------------------------------


class TestSanitizeToolName:
    def test_simple_name(self):
        assert (
            CallbackAdapterCollection._sanitize_name("update_output") == "update_output"
        )

    def test_special_characters_replaced(self):
        result = CallbackAdapterCollection._sanitize_name("my-func.name")
        assert result == "my_func_name"

    def test_leading_digit(self):
        result = CallbackAdapterCollection._sanitize_name("123func")
        assert result == "cb_123func"

    def test_empty_name(self):
        result = CallbackAdapterCollection._sanitize_name("")
        assert result == "unnamed_callback"

    def test_consecutive_underscores_collapsed(self):
        result = CallbackAdapterCollection._sanitize_name("a---b___c")
        assert result == "a_b_c"

    def test_long_name_truncated_to_64_chars(self):
        long_name = "a" * 200
        result = CallbackAdapterCollection._sanitize_name(long_name)
        assert len(result) <= 64
        assert result[-8:].isalnum()

    def test_long_name_uniqueness(self):
        result_a = CallbackAdapterCollection._sanitize_name("a" * 200)
        result_b = CallbackAdapterCollection._sanitize_name("b" * 200)
        assert result_a != result_b
        assert len(result_a) <= 64
        assert len(result_b) <= 64

    def test_short_name_not_truncated(self):
        result = CallbackAdapterCollection._sanitize_name("short_name")
        assert result == "short_name"


# ---------------------------------------------------------------------------
# Description building
# ---------------------------------------------------------------------------


class TestBuildCallbackDescription:
    def _out(self, comp_id, prop, comp_type=None):
        return {
            "id_and_prop": f"{comp_id}.{prop}",
            "component_id": comp_id,
            "property": prop,
            "component_type": comp_type,
            "initial_value": None,
        }

    def test_includes_docstring(self):
        outputs = [self._out("out", "children")]
        desc = build_tool_description(outputs, docstring="Does something useful.")
        assert "Does something useful." in desc

    def test_semantic_summary_with_component_type(self):
        outputs = [self._out("my-graph", "figure", "Graph")]
        desc = build_tool_description(outputs)
        assert "Returns chart/visualization data" in desc

    def test_semantic_summary_fallback_by_property(self):
        outputs = [self._out("unknown-id", "figure")]
        desc = build_tool_description(outputs)
        assert "Returns chart/visualization data" in desc

    def test_no_docstring(self):
        outputs = [self._out("out", "children")]
        desc = build_tool_description(outputs)
        assert "out.children: Returns content" in desc

    def test_multiple_outputs_lists_each_target(self):
        outputs = [self._out("a", "children"), self._out("b", "children")]
        desc = build_tool_description(outputs)
        assert "a.children" in desc
        assert "b.children" in desc
