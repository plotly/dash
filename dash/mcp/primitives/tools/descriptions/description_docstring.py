"""Callback docstring for tool descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ToolDescriptionSource

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter


class DocstringDescription(ToolDescriptionSource):
    """Return the callback's docstring as description lines."""

    @classmethod
    def describe(cls, callback: CallbackAdapter) -> list[str]:
        docstring = callback._docstring
        if docstring:
            return ["", docstring.strip()]
        return []
