"""Output summary for tool descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ToolDescriptionSource

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter

_OUTPUT_SEMANTICS: dict[tuple[str | None, str], str] = {
    ("DataTable", "data"): "Returns tabular data",
    ("DataTable", "columns"): "Returns table column definitions",
    ("Store", "data"): "Returns data to be remembered client-side",
    ("Download", "data"): "Returns downloadable content",
    ("Markdown", "children"): "Returns formatted text",
    (None, "figure"): "Returns chart/visualization data",
    (None, "options"): "Returns available options",
    (None, "columns"): "Returns column definitions",
    (None, "children"): "Returns content",
    (None, "value"): "Returns the current value",
    (None, "style"): "Updates styling",
    (None, "disabled"): "Updates enabled/disabled state",
}


class OutputSummaryDescription(ToolDescriptionSource):
    """Produce a short summary of what the callback outputs represent."""

    @classmethod
    def describe(cls, callback: CallbackAdapter) -> list[str]:
        outputs = callback.outputs
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
