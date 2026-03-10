"""Plotly figure tool result: rendered image + structured text summary."""

from __future__ import annotations

import base64
import logging
from datetime import datetime, timezone
from typing import Any

from mcp.types import CallToolResult, ImageContent, TextContent

logger = logging.getLogger(__name__)

MAX_DATA_POINTS = 500
IMAGE_WIDTH = 700
IMAGE_HEIGHT = 450


def is_plotly_figure(value: Any) -> bool:
    """Return True if *value* is a Plotly figure."""
    return hasattr(value, "to_plotly_json")


def format_plotly_figure(value: Any) -> CallToolResult:
    """Convert a Plotly figure to a CallToolResult with image and text.

    Returns up to two content items:
    1. ImageContent — PNG rendering (if kaleido is installed)
    2. TextContent — structured summary of the figure
    """
    fig_json = value.to_plotly_json()
    if not isinstance(fig_json, dict) or "data" not in fig_json:
        return CallToolResult(content=[TextContent(type="text", text=str(value))])

    content: list[TextContent | ImageContent] = []

    # 1. Try to render as PNG image
    image_content = _render_image(value)
    has_image = image_content is not None
    if has_image:
        content.append(image_content)

    # 2. Always include text summary
    data = fig_json.get("data", [])
    layout = fig_json.get("layout", {})
    summary = _build_summary(data, layout, include_image_hint=not has_image)
    content.append(TextContent(type="text", text=summary))

    return CallToolResult(content=content)


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


def _build_summary(
    data: list[dict],
    layout: dict,
    *,
    include_image_hint: bool = False,
) -> str:
    """Build a structured text summary of the figure."""
    lines: list[str] = []

    if include_image_hint:
        lines.append(
            "Note: Install kaleido (`pip install kaleido`) to include "
            "a rendered image of this figure."
        )
        lines.append("")

    # Title
    title = _extract_title(layout)
    if title:
        lines.append(f"# {title}")
        lines.append("")

    # Axes
    axes = _format_axes(layout)
    if axes:
        lines.append(axes)
        lines.append("")

    # Traces
    for i, trace in enumerate(data):
        lines.extend(_format_trace(trace, i))
        lines.append("")

    return "\n".join(lines).rstrip()


def _extract_title(layout: dict) -> str | None:
    """Extract the figure title from the layout."""
    title = layout.get("title")
    if isinstance(title, dict):
        return title.get("text")
    return title


def _format_axes(layout: dict) -> str | None:
    """Format axis labels into a single line."""
    parts: list[str] = []
    for key, label in [("xaxis", "X"), ("yaxis", "Y"), ("zaxis", "Z")]:
        axis = layout.get(key, {})
        if not isinstance(axis, dict):
            continue
        title = axis.get("title")
        if isinstance(title, dict):
            title = title.get("text")
        if title:
            parts.append(f"{label}: {title}")
    return " | ".join(parts) if parts else None


def _format_trace(trace: dict, index: int) -> list[str]:
    """Format a single trace as structured text lines."""
    trace_type = trace.get("type", "unknown")
    name = trace.get("name")

    header = f"## Trace {index}: {trace_type}"
    if name:
        header += f" ({name})"
    lines = [header]

    mode = trace.get("mode")
    if mode:
        lines.append(f"Mode: {mode}")

    if trace_type in ("pie", "sunburst", "treemap", "funnel", "funnelarea"):
        _format_categorical(trace, lines)
    elif trace_type in ("heatmap", "contour", "surface"):
        _format_matrix(trace, lines)
    else:
        _format_xy(trace, lines)

    return lines


def _format_xy(trace: dict, lines: list[str]) -> None:
    """Format traces with x/y data as CSV.

    When there are more than ``MAX_DATA_POINTS``, the data is evenly
    sampled (always including the first and last points) so the LLM
    sees the full range.
    """
    x = _to_list(trace.get("x"))
    y = _to_list(trace.get("y"))

    if x is not None and y is not None:
        n = min(len(x), len(y))
        indices = _sample_indices(n, MAX_DATA_POINTS)
        sampled = len(indices) < n
        if sampled:
            lines.append(f"{n} data points (sampled to {len(indices)}):")
        else:
            lines.append(f"{n} data points:")
        lines.append("x,y")
        for j in indices:
            lines.append(f"{_fmt_val(x[j])},{_fmt_val(y[j])}")
    elif x is not None:
        lines.append(f"x ({len(x)} pts): {_summarize(x)}")
    elif y is not None:
        lines.append(f"y ({len(y)} pts): {_summarize(y)}")


def _format_categorical(trace: dict, lines: list[str]) -> None:
    """Format traces with labels/values data."""
    labels = _to_list(trace.get("labels"))
    values = _to_list(trace.get("values"))

    if labels is not None and values is not None:
        pairs = list(zip(labels, values))
        n = len(pairs)
        indices = _sample_indices(n, MAX_DATA_POINTS)
        for j in indices:
            lines.append(f"  {pairs[j][0]}: {pairs[j][1]}")
        if len(indices) < n:
            lines.append(f"  ... (sampled {len(indices)} of {n})")
    elif labels is not None:
        lines.append(f"Labels ({len(labels)}): {_summarize(labels)}")
    elif values is not None:
        lines.append(f"Values ({len(values)}): {_summarize(values)}")


def _format_matrix(trace: dict, lines: list[str]) -> None:
    """Format traces with z-matrix data."""
    x = _to_list(trace.get("x"))
    y = _to_list(trace.get("y"))
    z = trace.get("z")

    if x is not None:
        lines.append(f"x ({len(x)}): {_summarize(x)}")
    if y is not None:
        lines.append(f"y ({len(y)}): {_summarize(y)}")
    if isinstance(z, (list, tuple)) and z:
        rows = len(z)
        cols = len(z[0]) if isinstance(z[0], (list, tuple)) else 1
        lines.append(f"z: {rows} \u00d7 {cols} matrix")


def _sample_indices(n: int, cap: int) -> list[int]:
    """Return evenly spaced indices, always including first and last."""
    if n <= cap:
        return list(range(n))
    # Evenly space *cap* samples across [0, n-1]
    step = (n - 1) / (cap - 1)
    return sorted(set(round(step * i) for i in range(cap)))


def _fmt_datetime64(v: Any) -> str:
    """Format a numpy datetime64 as YYYY-MM-DD or with time if non-midnight."""
    import numpy as np

    ts = (v - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(1, "s")
    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
    if dt.hour == 0 and dt.minute == 0 and dt.second == 0:
        return dt.strftime("%Y-%m-%d")
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _to_list(value: Any) -> list | None:
    """Convert array-like values to a list, or return None."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return list(value)
    # Plotly binary-encoded arrays: {"dtype": "f8", "bdata": "..."}
    if isinstance(value, dict) and "bdata" in value and "dtype" in value:
        return _decode_bdata(value)
    if hasattr(value, "tolist"):
        try:
            import numpy as np

            if isinstance(value, np.ndarray) and np.issubdtype(
                value.dtype, np.datetime64
            ):
                # numpy .tolist() converts datetime64 to nanosecond ints;
                # convert to compact date/datetime strings instead.
                return [_fmt_datetime64(v) for v in value]
        except ImportError:
            pass
        return value.tolist()
    return None


def _decode_bdata(value: dict) -> list | None:
    """Decode a Plotly binary-encoded array to a Python list."""
    try:
        import numpy as np

        raw = base64.b64decode(value["bdata"])
        arr = np.frombuffer(raw, dtype=value["dtype"])
        return arr.tolist()
    except Exception:
        return None


def _fmt_val(v: Any) -> str:
    """Format a single value for CSV output."""
    if v is None:
        return ""
    if isinstance(v, float):
        # Avoid unnecessary decimal places
        if v == int(v):
            return str(int(v))
        return f"{v:.6g}"
    # pandas Timestamps that slip through _to_list (e.g. inside a plain list)
    try:
        import pandas as pd

        if isinstance(v, pd.Timestamp):
            if v.hour == 0 and v.minute == 0 and v.second == 0:
                return v.strftime("%Y-%m-%d")
            return v.strftime("%Y-%m-%d %H:%M:%S")
    except ImportError:
        pass
    return str(v)


def _summarize(values: list) -> str:
    """Summarize a list of values for display."""
    if not values:
        return "[]"
    if len(values) <= MAX_DATA_POINTS:
        return repr(values)
    return f"{values[:MAX_DATA_POINTS]!r} ... ({len(values)} total)"


def plotly_figure_result(
    component_type: str | None,
    prop: str,
    value: Any,
    component: Any | None = None,
) -> list:
    """Produce rich content for Graph.figure output values.

    Reconstructs a ``plotly.graph_objects.Figure`` from the serialized
    dict in the dispatch response and renders it as PNG + text summary.
    """
    if component_type != "Graph" or prop != "figure":
        return []
    if not isinstance(value, dict):
        return []

    try:
        import plotly.graph_objects as go
    except ImportError:
        return []

    fig = go.Figure(value)

    image = _render_image(fig)
    if image is not None:
        return [image]
    return []
