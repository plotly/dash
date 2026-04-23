"""Formatted tool-output results: structured content + text/image fallbacks.

Covers:
- ``format_callback_response`` — wraps the callback result as
  ``structuredContent`` and delegates to per-output formatters.
- ``DataFrameResult`` — renders DataTable/AgGrid rows as markdown tables.
- ``PlotlyFigureResult`` — renders ``dcc.Graph.figure`` values as PNG images
  (via kaleido; skipped gracefully when kaleido is unavailable).
"""

import base64
from unittest.mock import Mock, patch

import plotly.graph_objects as go  # type: ignore[import-untyped]

from dash.mcp.primitives.tools.results import format_callback_response
from dash.mcp.primitives.tools.results.result_dataframe import (
    MAX_ROWS,
    DataFrameResult,
)
from dash.mcp.primitives.tools.results.result_plotly_figure import (
    PlotlyFigureResult,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _mock_callback(outputs=None):
    cb = Mock()
    cb.outputs = outputs or []
    return cb


EXPECTED_TABLE = (
    "*2 rows \u00d7 2 columns*\n"
    "\n"
    "| name | age |\n"
    "| --- | --- |\n"
    "| Alice | 30 |\n"
    "| Bob | 25 |"
)

SAMPLE_ROWS = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

DATATABLE_OUTPUT = {
    "component_type": "DataTable",
    "property": "data",
    "component_id": "t",
    "id_and_prop": "t.data",
    "initial_value": None,
    "tool_name": "update",
}

AGGRID_OUTPUT = {
    "component_type": "AgGrid",
    "property": "rowData",
    "component_id": "g",
    "id_and_prop": "g.rowData",
    "initial_value": None,
    "tool_name": "update",
}

FAKE_PNG = b"\x89PNG\r\n\x1a\nfakedata"
FAKE_B64 = base64.b64encode(FAKE_PNG).decode("ascii")

GRAPH_FIGURE_OUTPUT = {
    "component_type": "Graph",
    "property": "figure",
    "component_id": "g",
    "id_and_prop": "g.figure",
    "initial_value": None,
    "tool_name": "update",
}


# ---------------------------------------------------------------------------
# format_callback_response
# ---------------------------------------------------------------------------


def test_mcpr001_wraps_as_structured_content():
    response = {
        "multi": True,
        "response": {"out": {"children": "hello"}},
    }
    result = format_callback_response(response, _mock_callback())
    assert result.structuredContent == response


def test_mcpr002_content_has_json_text_fallback():
    """Per MCP spec, structuredContent SHOULD include a TextContent fallback."""
    response = {"multi": True, "response": {}}
    result = format_callback_response(response, _mock_callback())
    assert len(result.content) >= 1
    assert result.content[0].type == "text"
    assert '"multi": true' in result.content[0].text


def test_mcpr003_is_error_defaults_false():
    response = {"multi": True, "response": {}}
    result = format_callback_response(response, _mock_callback())
    assert result.isError is False


def test_mcpr004_preserves_side_update():
    response = {
        "multi": True,
        "response": {"out": {"children": "x"}},
        "sideUpdate": {"other": {"value": 42}},
    }
    result = format_callback_response(response, _mock_callback())
    assert result.structuredContent["sideUpdate"] == {"other": {"value": 42}}


def test_mcpr005_datatable_result_includes_markdown_table():
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


def test_mcpr006_plotly_figure_includes_image():
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


# ---------------------------------------------------------------------------
# DataFrameResult (DataTable / AgGrid markdown rendering)
# ---------------------------------------------------------------------------


def test_mcpr007_datatable_data_renders_markdown():
    result = DataFrameResult.format(DATATABLE_OUTPUT, SAMPLE_ROWS)
    assert len(result) == 1
    assert result[0].text == EXPECTED_TABLE


def test_mcpr008_aggrid_rowdata_renders_markdown():
    result = DataFrameResult.format(AGGRID_OUTPUT, SAMPLE_ROWS)
    assert len(result) == 1
    assert result[0].text == EXPECTED_TABLE


def test_mcpr009_ignores_non_tabular_props():
    non_tabular = {**DATATABLE_OUTPUT, "property": "columns"}
    assert DataFrameResult.format(non_tabular, SAMPLE_ROWS) == []


def test_mcpr010_ignores_empty_or_non_dict_rows():
    assert DataFrameResult.format(DATATABLE_OUTPUT, []) == []
    assert DataFrameResult.format(DATATABLE_OUTPUT, ["a", "b"]) == []


def test_mcpr011_truncates_large_tables():
    rows = [{"i": n} for n in range(MAX_ROWS + 50)]
    result = DataFrameResult.format(DATATABLE_OUTPUT, rows)
    text = result[0].text
    assert f"| {MAX_ROWS - 1} |" in text
    assert f"| {MAX_ROWS} |" not in text
    assert "50 more rows" in text


# ---------------------------------------------------------------------------
# PlotlyFigureResult (Graph.figure → PNG image)
# ---------------------------------------------------------------------------


def test_mcpr012_returns_image_when_kaleido_available():
    fig_dict = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2])]).to_plotly_json()
    with patch.object(go.Figure, "to_image", return_value=FAKE_PNG):
        result = PlotlyFigureResult.format(GRAPH_FIGURE_OUTPUT, fig_dict)
    assert len(result) == 1
    assert result[0].type == "image"
    assert result[0].data == FAKE_B64


def test_mcpr013_returns_empty_when_kaleido_unavailable():
    fig_dict = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2])]).to_plotly_json()
    with patch.object(go.Figure, "to_image", side_effect=ImportError):
        result = PlotlyFigureResult.format(GRAPH_FIGURE_OUTPUT, fig_dict)
    assert result == []


def test_mcpr014_ignores_non_graph_components():
    output = {
        **GRAPH_FIGURE_OUTPUT,
        "component_type": "Div",
        "property": "children",
    }
    assert PlotlyFigureResult.format(output, {}) == []


def test_mcpr015_ignores_non_figure_props():
    output = {**GRAPH_FIGURE_OUTPUT, "property": "clickData"}
    assert PlotlyFigureResult.format(output, {}) == []


def test_mcpr016_ignores_non_dict_values():
    assert PlotlyFigureResult.format(GRAPH_FIGURE_OUTPUT, "not a dict") == []
