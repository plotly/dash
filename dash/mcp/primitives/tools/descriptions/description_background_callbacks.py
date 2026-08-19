"""Description for background (long-running) callbacks.

Informs the LLM that the tool returns a taskId immediately
and must be polled via the background task result tool.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..tool_background_tasks import GET_RESULT_TOOL_NAME
from .base import ToolDescriptionSource

if TYPE_CHECKING:
    from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter


class BackgroundCallbackDescription(ToolDescriptionSource):
    """Add async polling instructions for background callbacks."""

    @classmethod
    def describe(cls, callback: CallbackAdapter) -> list[str]:
        # pylint: disable-next=protected-access
        if not callback._cb_info.get("background"):
            return []

        return [
            "",
            "This is a long-running background operation. "
            "It returns a taskId immediately. "
            f"Call tool `{GET_RESULT_TOOL_NAME}` with the taskId to poll for the result.",
        ]
