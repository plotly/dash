"""Plotly figure tool result: rendered image."""

from __future__ import annotations

import base64
import logging
from typing import Any

from mcp.types import ImageContent

from dash.mcp.types import MCPOutput

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


def plotly_figure_result(callback_output: MCPOutput, callback_output_value: Any) -> list:
    """Produce a rendered PNG for Graph.figure output values."""
    if callback_output.get("component_type") != "Graph" or callback_output.get("property") != "figure":
        return []
    if not isinstance(callback_output_value, dict):
        return []

    try:
        import plotly.graph_objects as go
    except ImportError:
        return []

    fig = go.Figure(callback_output_value)
    image = _render_image(fig)
    return [image] if image is not None else []
