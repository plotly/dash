"""Tests for the Plotly figure tool result formatter."""

import base64
from unittest.mock import patch

import pytest

from dash.mcp.primitives.tools.results.result_plotly_figure import (
    plotly_figure_result,
)

go = pytest.importorskip("plotly.graph_objects")

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


class TestPlotlyFigureResult:
    def test_returns_image_when_kaleido_available(self):
        fig_dict = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2])]).to_plotly_json()
        with patch.object(go.Figure, "to_image", return_value=FAKE_PNG):
            result = plotly_figure_result(GRAPH_FIGURE_OUTPUT, fig_dict)
        assert len(result) == 1
        assert result[0].type == "image"
        assert result[0].data == FAKE_B64

    def test_returns_empty_when_kaleido_unavailable(self):
        fig_dict = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2])]).to_plotly_json()
        with patch.object(go.Figure, "to_image", side_effect=ImportError):
            result = plotly_figure_result(GRAPH_FIGURE_OUTPUT, fig_dict)
        assert result == []

    def test_ignores_non_graph_components(self):
        output = {
            **GRAPH_FIGURE_OUTPUT,
            "component_type": "Div",
            "property": "children",
        }
        assert plotly_figure_result(output, {}) == []

    def test_ignores_non_figure_props(self):
        output = {**GRAPH_FIGURE_OUTPUT, "property": "clickData"}
        assert plotly_figure_result(output, {}) == []

    def test_ignores_non_dict_values(self):
        assert plotly_figure_result(GRAPH_FIGURE_OUTPUT, "not a dict") == []
