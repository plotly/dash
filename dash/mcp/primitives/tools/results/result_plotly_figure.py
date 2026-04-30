"""Plotly figure tool result: rendered image."""

from __future__ import annotations

import base64
import logging
from typing import Any

import plotly.graph_objects as go  # type: ignore[import-untyped]
from mcp.types import ImageContent, TextContent

from dash.mcp.types import MCPOutput

from ..prop_roles import PLOTLY_FIGURE
from .base import ResultFormatter

logger = logging.getLogger(__name__)

IMAGE_WIDTH = 700
IMAGE_HEIGHT = 450


def _render_image(figure: Any) -> ImageContent | None:
    """Render the figure as a base64 PNG ImageContent.

    Returns None if kaleido is not installed.
    """
    try:
        img_bytes = figure.to_image(
            format="png",
            width=IMAGE_WIDTH,
            height=IMAGE_HEIGHT,
        )
    except (ValueError, ImportError):
        logger.debug("MCP: kaleido not available, skipping image render")
        return None

    b64 = base64.b64encode(img_bytes).decode("ascii")
    return ImageContent(type="image", data=b64, mimeType="image/png")


class PlotlyFigureResult(ResultFormatter):
    """Produce a rendered PNG for Graph.figure output values."""

    @classmethod
    def format(
        cls, output: MCPOutput, returned_output_value: Any
    ) -> list[TextContent | ImageContent]:
        if not PLOTLY_FIGURE.matches(output.get("component_type"), output["property"]):
            return []
        if not isinstance(returned_output_value, dict):
            return []

        fig = go.Figure(returned_output_value)
        image = _render_image(fig)
        return [image] if image is not None else []
