"""Transport helpers for streaming callbacks (``@callback(..., stream=True)``).

A streaming callback is a generator (or async generator) whose yields are
converted to "frames" — dicts with the same shape as a regular callback
response (see ``CallbackExecutionResponse``) — followed by a terminal
``{"done": True}`` frame. Frames are delivered to the renderer either as
NDJSON lines on the HTTP response or as individual messages over the
WebSocket callback transport.

The frame generators are built in ``dash._callback``; this module owns the
marker object the backends dispatch on and the transport-side iteration
helpers. Iteration helpers exist because Dash's callback context lives in a
``contextvars.ContextVar`` and a sync generator runs in whatever context its
consumer drives it from — which, for a streaming HTTP response, is not the
request context the callback started in.
"""

import asyncio
import contextlib
import functools
import logging
import queue
import threading
from typing import cast

from ._utils import to_json as _to_json

logger = logging.getLogger(__name__)

STREAM_MIMETYPE = "application/x-ndjson"
# Disable proxy/server buffering so frames reach the browser as they are
# produced (X-Accel-Buffering covers nginx).
STREAM_HEADERS = {"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}

_SENTINEL = object()


def to_json(value) -> str:
    return cast(str, _to_json(value))


class StreamedCallbackResponse:  # pylint: disable=too-few-public-methods
    """Marker returned by ``stream=True`` callback wrappers.

    Backends detect this instead of a JSON string and return a streaming
    response. ``frames`` is a generator (async generator when ``is_async``)
    of frame dicts. ``ctx`` is the ``contextvars`` snapshot captured when the
    callback was invoked; sync frame generators must be driven through it
    (``iter_stream_frames``) so ``dash.ctx``/``set_props`` keep working after
    the dispatch function has returned.
    """

    def __init__(self, frames, is_async, ctx=None):
        self.frames = frames
        self.is_async = is_async
        self.ctx = ctx


def iter_stream_frames(marker):
    """Drive a sync frame generator inside its captured context snapshot."""
    while True:
        try:
            yield marker.ctx.run(next, marker.frames)
        except StopIteration:
            return


async def aiter_stream_frames(marker):
    """Async wrapper for a sync frame generator (ASGI backends).

    Each step runs on an executor thread through ``marker.ctx`` — Starlette's
    own threadpool iteration would use a fresh context copy per chunk and
    lose the callback context.
    """
    loop = asyncio.get_running_loop()
    while True:
        frame = await loop.run_in_executor(
            None, marker.ctx.run, functools.partial(next, marker.frames, _SENTINEL)
        )
        if frame is _SENTINEL:
            return
        yield frame


def _serialize_frame(frame):
    """Serialize one frame to an NDJSON line.

    Returns ``(line, fatal)``; a serialization failure produces a terminal
    error frame so the client is not left waiting on a silently dead stream.
    """
    try:
        return to_json(frame) + "\n", False
    except TypeError as err:
        logger.exception("Failed to serialize streamed callback frame")
        return (
            to_json(
                {
                    "done": True,
                    "error": {
                        "message": "Non-serializable value in streamed "
                        f"callback output: {err}"
                    },
                }
            )
            + "\n",
            True,
        )


def ndjson_lines(marker):
    """Sync NDJSON body for a sync frame generator (Flask/WSGI)."""
    for frame in iter_stream_frames(marker):
        line, fatal = _serialize_frame(frame)
        yield line
        if fatal:
            return


async def andjson_lines(frames):
    """Async NDJSON body over an async iterator of frames."""
    async for frame in frames:
        line, fatal = _serialize_frame(frame)
        yield line
        if fatal:
            return


def marker_ndjson_aiter(marker):
    """Async NDJSON body for either flavor of frame generator."""
    if marker.is_async:
        return andjson_lines(marker.frames)
    return andjson_lines(aiter_stream_frames(marker))


def sync_iter_asyncgen(agen):
    """Iterate an async generator from sync code (Flask + async gen).

    Runs the whole consumption on one task on a private event-loop thread so
    contextvars set inside the generator persist across steps. Closing this
    generator (client disconnect) cancels the task, which raises into the
    user generator at its current yield.
    """
    frame_queue: queue.Queue = queue.Queue()
    loop = asyncio.new_event_loop()
    task = None
    task_ready = threading.Event()

    async def consume():
        try:
            async for item in agen:
                frame_queue.put(("item", item))
            frame_queue.put(("end", None))
        except BaseException as err:  # pylint: disable=broad-exception-caught
            frame_queue.put(("error", err))
        finally:
            with contextlib.suppress(Exception):
                await agen.aclose()

    def run():
        nonlocal task
        asyncio.set_event_loop(loop)
        task = loop.create_task(consume())
        task_ready.set()
        try:
            loop.run_until_complete(task)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

    thread = threading.Thread(target=run, daemon=True, name="dash-stream-bridge")
    thread.start()
    try:
        while True:
            kind, value = frame_queue.get()
            if kind == "item":
                yield value
            elif kind == "error":
                if isinstance(value, asyncio.CancelledError):
                    return
                raise value
            else:
                return
    finally:
        task_ready.wait(timeout=5)
        if task is not None and not task.done():
            with contextlib.suppress(RuntimeError):
                loop.call_soon_threadsafe(task.cancel)
