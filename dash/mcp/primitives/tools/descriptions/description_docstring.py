"""Callback docstring for tool descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter


def callback_docstring(adapter: CallbackAdapter) -> list[str]:
    """Return the callback's docstring as description lines."""
    docstring = adapter._docstring
    if docstring:
        return ["", docstring.strip()]
    return []
