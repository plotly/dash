"""Output summary for tool descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..prop_roles import iter_prop_roles
from .base import ToolDescriptionSource

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter


def _describe_output(comp_type: str | None, prop: str) -> str | None:
    for role in iter_prop_roles():
        if role.description is not None and role.matches(comp_type, prop):
            return role.description
    return None


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
            description = _describe_output(out.get("component_type"), prop)

            if description is not None:
                lines.append(f"- {comp_id}.{prop}: {description}")
            else:
                lines.append(f"- {comp_id}.{prop}")

        n = len(outputs)
        if n == 1:
            return [lines[0].lstrip("- ")]
        header = f"Returns {n} output{'s' if n > 1 else ''}:"
        return [header] + lines
