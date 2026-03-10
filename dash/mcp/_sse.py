"""SSE stream generation and queue management."""

from __future__ import annotations

import queue
from typing import Any

from flask import Response


def create_sse_stream(sessions: dict[str, dict[str, Any]], session_id: str) -> Response:
    """Create a Server-Sent Events stream for the given session.

    Stores a :class:`queue.Queue` in ``sessions[session_id]["sse_queue"]``
    and returns a Flask streaming ``Response``.  The generator yields
    events pushed to the queue, with keepalive comments every 30 seconds.
    """
    event_queue: queue.Queue[str | None] = queue.Queue()
    # Replace any prior SSE queue for this session (client reconnect).
    sessions[session_id]["sse_queue"] = event_queue

    def _generate():
        try:
            while True:
                try:
                    event = event_queue.get(timeout=30)
                    if event is None:
                        return  # Sentinel: server closing stream
                    yield f"event: message\ndata: {event}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        except GeneratorExit:
            pass
        finally:
            # Clean up queue reference if it's still ours.
            if sessions.get(session_id, {}).get("sse_queue") is event_queue:
                sessions[session_id].pop("sse_queue", None)

    return Response(
        _generate(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "mcp-session-id": session_id,
        },
    )


def close_sse_stream(session_data: dict[str, Any]) -> None:
    """Send a sentinel to shut down the session's SSE stream cleanly."""
    sse_queue = session_data.get("sse_queue")
    if sse_queue is not None:
        try:
            sse_queue.put_nowait(None)
        except queue.Full:
            pass


def shutdown_all_streams(sessions: dict[str, dict[str, Any]]) -> None:
    """Close all active SSE streams.

    Called during server shutdown (via ``atexit``) so that connected
    MCP clients see a clean stream end and can reconnect promptly.
    """
    for session_data in list(sessions.values()):
        close_sse_stream(session_data)
