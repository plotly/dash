"""Output summary for tool descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter

_OUTPUT_SEMANTICS: dict[tuple[str | None, str], str] = {
    ("Graph", "figure"): "Returns chart/visualization data",
    ("DataTable", "data"): "Returns tabular data",
    ("DataTable", "columns"): "Returns table column definitions",
    ("Dropdown", "options"): "Returns selection options",
    ("Dropdown", "value"): "Updates a selection value",
    ("RadioItems", "options"): "Returns selection options",
    ("Checklist", "options"): "Returns selection options",
    ("Store", "data"): "Returns stored data",
    ("Download", "data"): "Returns downloadable content",
    ("Markdown", "children"): "Returns formatted text",
    (None, "figure"): "Returns chart/visualization data",
    (None, "data"): "Returns data",
    (None, "options"): "Returns selection options",
    (None, "columns"): "Returns column definitions",
    (None, "children"): "Returns content",
    (None, "value"): "Returns a value",
    (None, "style"): "Updates styling",
    (None, "disabled"): "Updates enabled/disabled state",
}


def output_summary(adapter: CallbackAdapter) -> list[str]:
    """Produce a short summary of what the callback outputs represent."""
    outputs = adapter.outputs
    if not outputs:
        return ["Dash callback"]

    lines: list[str] = []
    for out in outputs:
        comp_id = out["component_id"]
        prop = out["property"]
        comp_type = out.get("component_type")

        semantic = _OUTPUT_SEMANTICS.get((comp_type, prop))
        if semantic is None:
            semantic = _OUTPUT_SEMANTICS.get((None, prop))

        if semantic is not None:
            lines.append(f"- {comp_id}.{prop}: {semantic}")
        else:
            lines.append(f"- {comp_id}.{prop}")

    n = len(outputs)
    if n == 1:
        return [lines[0].lstrip("- ")]
    header = f"Returns {n} output{'s' if n > 1 else ''}:"
    return [header] + lines
