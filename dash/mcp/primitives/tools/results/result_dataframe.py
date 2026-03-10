"""DataFrame tool result: render as a markdown table."""

from __future__ import annotations

from typing import Any

from mcp.types import CallToolResult, TextContent

MAX_ROWS = 100


def is_dataframe(value: Any) -> bool:
    """Return True if *value* is a dataframe recognised by narwhals."""
    try:
        from narwhals.dependencies import is_into_dataframe

        return is_into_dataframe(value)
    except ImportError:
        return False


def format_dataframe(value: Any) -> CallToolResult:
    """Convert a dataframe to a markdown table CallToolResult."""
    import narwhals as nw

    df = nw.from_native(value, eager_only=True)
    total_rows, num_cols = df.shape
    columns = df.columns

    lines: list[str] = []

    # Metadata summary
    lines.append(f"*{total_rows} rows \u00d7 {num_cols} columns*")
    lines.append("")

    # Header
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines.append(header)
    lines.append(separator)

    # Data rows (capped)
    display_rows = min(total_rows, MAX_ROWS)
    for row in df.head(display_rows).iter_rows(named=True):
        cells = []
        for col in columns:
            cell = str(row[col]).replace("|", "\\|").replace("\n", " ")
            cells.append(cell)
        lines.append("| " + " | ".join(cells) + " |")

    # Truncation note
    if total_rows > MAX_ROWS:
        remaining = total_rows - MAX_ROWS
        lines.append(f"\n(\u2026 {remaining} more rows)")

    return CallToolResult(content=[TextContent(type="text", text="\n".join(lines))])


def dataframe_result(
    component_type: str | None,
    prop: str,
    value: Any,
    component: Any | None = None,
) -> list:
    """Produce rich content for DataFrame output values.

    TODO: detect DataFrame-like values and render as markdown tables.
    """
    return []
