"""Tests for the callback response formatter."""

from unittest.mock import Mock

from dash.mcp.primitives.tools.results import format_callback_response


def _mock_callback(outputs=None):
    cb = Mock()
    cb.outputs = outputs or []
    return cb


class TestFormatCallbackResponse:
    def test_wraps_as_structured_content(self):
        response = {
            "multi": True,
            "response": {"out": {"children": "hello"}},
        }
        result = format_callback_response(response, _mock_callback())
        assert result.structuredContent == response

    def test_content_has_json_text_fallback(self):
        """Per MCP spec, structuredContent SHOULD include a TextContent fallback."""
        response = {"multi": True, "response": {}}
        result = format_callback_response(response, _mock_callback())
        assert len(result.content) >= 1
        assert result.content[0].type == "text"
        assert '"multi": true' in result.content[0].text

    def test_is_error_defaults_false(self):
        response = {"multi": True, "response": {}}
        result = format_callback_response(response, _mock_callback())
        assert result.isError is False

    def test_preserves_side_update(self):
        response = {
            "multi": True,
            "response": {"out": {"children": "x"}},
            "sideUpdate": {"other": {"value": 42}},
        }
        result = format_callback_response(response, _mock_callback())
        assert result.structuredContent["sideUpdate"] == {"other": {"value": 42}}

    def test_datatable_result_includes_markdown_table(self):
        response = {
            "multi": True,
            "response": {
                "my-table": {"data": [{"name": "Alice", "age": 30}]},
            },
        }
        outputs = [
            {
                "component_id": "my-table",
                "component_type": "DataTable",
                "property": "data",
                "id_and_prop": "my-table.data",
                "initial_value": None,
                "tool_name": "update",
            }
        ]
        result = format_callback_response(response, _mock_callback(outputs))
        texts = [c.text for c in result.content if c.type == "text"]
        assert any("| name | age |" in t for t in texts)

    def test_plotly_figure_includes_image(self):
        from unittest.mock import patch

        try:
            import plotly.graph_objects as go
        except ImportError:
            return

        response = {
            "multi": True,
            "response": {
                "my-graph": {
                    "figure": {
                        "data": [{"type": "bar", "x": ["A"], "y": [1]}],
                        "layout": {},
                    }
                }
            },
        }
        outputs = [
            {
                "component_id": "my-graph",
                "component_type": "Graph",
                "property": "figure",
                "id_and_prop": "my-graph.figure",
                "initial_value": None,
                "tool_name": "update",
            }
        ]
        with patch.object(go.Figure, "to_image", return_value=b"\x89PNGfake"):
            result = format_callback_response(response, _mock_callback(outputs))
        images = [c for c in result.content if c.type == "image"]
        assert len(images) == 1
