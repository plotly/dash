"""Tabular data result: render as a markdown table.

Detects tabular output by component type and prop name:
- DataTable.data
- AgGrid.rowData
"""

from __future__ import annotations

from typing import Any

from mcp.types import ImageContent, TextContent

from dash.mcp.types import MCPOutput

from .base import ResultFormatter

MAX_ROWS = 50

_TABULAR_PROPS = {
    ("DataTable", "data"),
    ("AgGrid", "rowData"),
}


def _to_markdown_table(rows: list[dict], max_rows: int = MAX_ROWS) -> str:
    """Render a list of row dicts as a markdown table."""
    columns = list(rows[0].keys())
    total = len(rows)

    lines: list[str] = []
    lines.append(f"*{total} rows \u00d7 {len(columns)} columns*")
    lines.append("")
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("| " + " | ".join("---" for _ in columns) + " |")

    for row in rows[:max_rows]:
        cells = [
            str(row.get(col, "")).replace("|", "\\|").replace("\n", " ")
            for col in columns
        ]
        lines.append("| " + " | ".join(cells) + " |")

    if total > max_rows:
        lines.append(f"\n(\u2026 {total - max_rows} more rows)")

    return "\n".join(lines)


class DataFrameResult(ResultFormatter):
    """Produce a markdown table for tabular component output values."""

    @classmethod
    def format(
        cls, output: MCPOutput, returned_output_value: Any
    ) -> list[TextContent | ImageContent]:
        key = (output.get("component_type"), output.get("property"))
        if key not in _TABULAR_PROPS:
            return []
        if (
            not isinstance(returned_output_value, list)
            or not returned_output_value
            or not isinstance(returned_output_value[0], dict)
        ):
            return []
        return [
            TextContent(type="text", text=_to_markdown_table(returned_output_value))
        ]
