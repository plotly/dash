"""Tests for the callback response formatter."""

from dash.mcp.primitives.tools.results import format_callback_response


class TestFormatCallbackResponse:
    def test_wraps_as_structured_content(self):
        response = {
            "multi": True,
            "response": {"out": {"children": "hello"}},
        }
        result = format_callback_response(response)
        assert result.structuredContent == response

    def test_content_has_json_text_fallback(self):
        """Per MCP spec, structuredContent SHOULD include a TextContent fallback."""
        response = {"multi": True, "response": {}}
        result = format_callback_response(response)
        assert len(result.content) >= 1
        assert result.content[0].type == "text"
        assert '"multi": true' in result.content[0].text

    def test_is_error_defaults_false(self):
        response = {"multi": True, "response": {}}
        result = format_callback_response(response)
        assert result.isError is False

    def test_preserves_side_update(self):
        response = {
            "multi": True,
            "response": {"out": {"children": "x"}},
            "sideUpdate": {"other": {"value": 42}},
        }
        result = format_callback_response(response)
        assert result.structuredContent["sideUpdate"] == {"other": {"value": 42}}
