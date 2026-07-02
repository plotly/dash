"""Dynamic callback tools: MCP spec compliance, tool naming, output summaries.

Verifies that generated tools conform to the MCP 2025-11-25 specification
and Dash-specific conventions. Focuses on shape/structure, tool-name
sanitization, and ``_OUTPUT_SEMANTICS`` fallback summaries; input-schema
values are covered by ``test_mcp_input_schemas``.

Reference: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
"""

import re
from unittest.mock import Mock

from dash.mcp.primitives.tools.callback_adapter_collection import (
    CallbackAdapterCollection,
)
from dash.mcp.primitives.tools.descriptions import build_tool_description

from tests.unit.mcp.conftest import (
    _make_app,
    _tools_list,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TOOL_NAME_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")


def _adapter_with_outputs(outputs, docstring=None):
    adapter = Mock()
    adapter.outputs = outputs
    adapter._docstring = docstring
    return adapter


def _out(comp_id, prop, comp_type=None):
    return {
        "id_and_prop": f"{comp_id}.{prop}",
        "component_id": comp_id,
        "property": prop,
        "component_type": comp_type,
        "initial_value": None,
    }


# ---------------------------------------------------------------------------
# MCP spec compliance — every generated tool must satisfy the spec
# ---------------------------------------------------------------------------


def test_mcptc001_all_tools_conform_to_mcp_spec():
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


# ---------------------------------------------------------------------------
# Built-in tools
# ---------------------------------------------------------------------------


def test_mcptc002_query_component_always_present():
    names = {t.name for t in _tools_list(_make_app())}
    assert "get_dash_component" in names


def test_mcptc003_query_component_has_required_params():
    tool = next(t for t in _tools_list(_make_app()) if t.name == "get_dash_component")
    assert "component_id" in tool.inputSchema["properties"]
    assert "property" in tool.inputSchema["properties"]
    assert set(tool.inputSchema.get("required", [])) == {"component_id"}


# ---------------------------------------------------------------------------
# Tool-name sanitization (CallbackAdapterCollection._sanitize_name)
# ---------------------------------------------------------------------------


def test_mcptc004_sanitize_simple_name():
    assert CallbackAdapterCollection._sanitize_name("update_output") == "update_output"


def test_mcptc005_sanitize_special_characters_replaced():
    assert CallbackAdapterCollection._sanitize_name("my-func.name") == "my_func_name"


def test_mcptc006_sanitize_leading_digit():
    assert CallbackAdapterCollection._sanitize_name("123func") == "cb_123func"


def test_mcptc007_sanitize_empty_name():
    assert CallbackAdapterCollection._sanitize_name("") == "unnamed_callback"


def test_mcptc008_sanitize_consecutive_underscores_collapsed():
    assert CallbackAdapterCollection._sanitize_name("a---b___c") == "a_b_c"


def test_mcptc009_sanitize_long_name_truncated_to_64_chars():
    result = CallbackAdapterCollection._sanitize_name("a" * 200)
    assert len(result) <= 64
    assert result[-8:].isalnum()


def test_mcptc010_sanitize_long_name_uniqueness():
    result_a = CallbackAdapterCollection._sanitize_name("a" * 200)
    result_b = CallbackAdapterCollection._sanitize_name("b" * 200)
    assert result_a != result_b


def test_mcptc011_sanitize_short_name_not_truncated():
    assert CallbackAdapterCollection._sanitize_name("short_name") == "short_name"


# ---------------------------------------------------------------------------
# Output semantic summary (``_OUTPUT_SEMANTICS`` in description_outputs.py).
# Other description tests (docstring, output target, multi-output) are
# covered by test_mcp_tools using real adapters.
# ---------------------------------------------------------------------------


def test_mcptc012_semantic_summary_with_component_type():
    adapter = _adapter_with_outputs([_out("my-graph", "figure", "Graph")])
    desc = build_tool_description(adapter)
    assert "Returns chart/visualization data" in desc


def test_mcptc013_semantic_summary_fallback_by_property():
    adapter = _adapter_with_outputs([_out("unknown-id", "figure")])
    desc = build_tool_description(adapter)
    assert "Returns chart/visualization data" in desc
