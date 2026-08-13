"""Base class for tool-level description sources."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter


class ToolDescriptionSource:
    """A source of text that can describe an MCP tool.

    Subclasses implement ``describe`` to return strings that will be
    joined into the tool's ``description`` field. All sources are
    accumulated — every source can add text to the overall description.
    """

    @classmethod
    def describe(cls, callback: CallbackAdapter) -> list[str]:
        raise NotImplementedError
