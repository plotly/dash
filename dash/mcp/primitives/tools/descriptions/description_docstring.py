"""Callback docstring for tool descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..tools_callbacks import CallbackTools
from .base import ToolDescriptionSource

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter


class DocstringDescription(ToolDescriptionSource):
    """Return the callback's docstring as description lines.

    Gated behind an opt-in flag: docstrings may contain sensitive
    implementation details that the browser never surfaces to users,
    so we don't expose them to MCP clients unless the author opts in
    — either per-callback or app-wide.
    """

    @classmethod
    def describe(cls, callback: CallbackAdapter) -> list[str]:
        if not cls._is_exposed(callback):
            return []
        docstring = callback._docstring  # pylint: disable=protected-access
        if docstring:
            return ["", docstring.strip()]
        return []

    @classmethod
    def _is_exposed(cls, callback: CallbackAdapter) -> bool:
        # pylint: disable-next=protected-access
        per_callback = callback._cb_info.get("mcp_expose_docstring")
        if per_callback is not None:
            return per_callback
        return CallbackTools.expose_docstrings_by_default
