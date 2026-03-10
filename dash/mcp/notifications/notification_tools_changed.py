"""Tool list change notifications."""

from __future__ import annotations

import json
import queue
from typing import Any


def broadcast_tools_changed(
    sessions: dict[str, dict[str, Any]],
) -> None:
    """Push a tools/list_changed notification to all active SSE streams.

    Not called automatically yet — available for future hot-reload
    or dynamic callback registration.
    """
    notification = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "notifications/tools/list_changed",
        }
    )
    for data in sessions.values():
        sse_queue = data.get("sse_queue")
        if sse_queue is not None:
            try:
                sse_queue.put_nowait(notification)
            except queue.Full:
                pass
