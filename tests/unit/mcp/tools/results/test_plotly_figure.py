"""Tests for the Plotly figure tool result formatter."""

import base64

import pytest

from dash.mcp.primitives.tools.results import result_plotly_figure as plotly_figure
from dash.mcp.primitives.tools.results.result_plotly_figure import (
    format_plotly_figure,
)

go = pytest.importorskip("plotly.graph_objects")

FAKE_PNG = b"\x89PNG\r\n\x1a\nfakedata"
FAKE_B64 = base64.b64encode(FAKE_PNG).decode("ascii")


@pytest.fixture(autouse=True)
def _mock_kaleido(monkeypatch):
    """Mock image rendering to avoid slow kaleido startup in unit tests."""
    from mcp.types import ImageContent

    monkeypatch.setattr(
        plotly_figure,
        "_render_image",
        lambda _: ImageContent(type="image", data=FAKE_B64, mimeType="image/png"),
    )


class TestFormatPlotlyFigure:
    def test_has_text_content(self):
        fig = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2])])
        result = format_plotly_figure(fig)
        text_items = [c for c in result.content if c.type == "text"]
        assert len(text_items) == 1

    def test_text_includes_trace_info(self):
        fig = go.Figure(data=[go.Bar(x=["A", "B"], y=[1, 2], name="Sales")])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "bar" in text.lower()
        assert "Sales" in text

    def test_text_includes_title(self):
        fig = go.Figure(
            data=[go.Scatter(x=[1], y=[2])],
            layout=go.Layout(title="My Chart"),
        )
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "My Chart" in text

    def test_text_includes_axis_labels(self):
        fig = go.Figure(
            data=[go.Scatter(x=[1], y=[2])],
            layout=go.Layout(xaxis_title="Time", yaxis_title="Value"),
        )
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "Time" in text
        assert "Value" in text

    def test_text_includes_data_as_csv(self):
        fig = go.Figure(data=[go.Bar(x=["A", "B", "C"], y=[10, 20, 30])])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "3 data points" in text
        assert "x,y" in text
        assert "A,10" in text
        assert "B,20" in text
        assert "C,30" in text

    def test_multiple_traces(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2], y=[3, 4], name="Line"))
        fig.add_trace(go.Bar(x=[1, 2], y=[5, 6], name="Bars"))
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "Trace 0" in text
        assert "Trace 1" in text
        assert "Line" in text
        assert "Bars" in text

    def test_pie_chart(self):
        fig = go.Figure(data=[go.Pie(labels=["A", "B"], values=[30, 70])])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "pie" in text.lower()
        assert "A" in text
        assert "30" in text

    def test_heatmap(self):
        fig = go.Figure(
            data=[
                go.Heatmap(
                    z=[[1, 2], [3, 4]],
                    x=["a", "b"],
                    y=["c", "d"],
                )
            ]
        )
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "heatmap" in text.lower()
        assert "2 \u00d7 2" in text

    def test_large_dataset_sampled(self):
        x = list(range(1000))
        y = [v * 2 for v in x]
        fig = go.Figure(data=[go.Scatter(x=x, y=y)])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "1000 data points (sampled to 500):" in text
        assert "0,0" in text
        assert "999,1998" in text

    def test_csv_float_formatting(self):
        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3.0, 4.12345678])])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "\n1,3\n" in text
        assert "2,4.12346" in text

    def test_is_error_defaults_false(self):
        fig = go.Figure(data=[go.Bar(x=["A"], y=[1])])
        result = format_plotly_figure(fig)
        assert result.isError is False


class TestImageContent:
    def test_image_before_text(self):
        fig = go.Figure(data=[go.Bar(x=["A"], y=[1])])
        result = format_plotly_figure(fig)
        assert result.content[0].type == "image"
        assert result.content[1].type == "text"

    def test_image_is_png(self):
        fig = go.Figure(data=[go.Bar(x=["A"], y=[1])])
        result = format_plotly_figure(fig)
        image = next(c for c in result.content if c.type == "image")
        assert image.mimeType == "image/png"

    def test_no_kaleido_hint_when_image_present(self):
        fig = go.Figure(data=[go.Bar(x=["A"], y=[1])])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "kaleido" not in text


class TestKaleidoHint:
    def test_kaleido_hint_when_no_image(self, monkeypatch):
        monkeypatch.setattr(plotly_figure, "_render_image", lambda _: None)
        fig = go.Figure(data=[go.Bar(x=["A"], y=[1])])
        result = format_plotly_figure(fig)
        text = next(c.text for c in result.content if c.type == "text")
        assert "kaleido" in text
        assert "pip install" in text
