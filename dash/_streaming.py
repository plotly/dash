"""Transport helpers for streaming callbacks (generator callbacks).

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

The NDJSON transports also emit keepalives: a blank line every
``keepalive`` seconds the callback spends between yields. Every proxy in a
typical deployment enforces an idle timeout on the response (nginx's
``proxy_read_timeout`` defaults to 60s), and a callback that thinks for
longer than that gets its connection closed mid-stream. A blank line resets
those timers; the renderer skips empty lines, so it costs nothing on the
client. The WebSocket transport has its own heartbeat
(``websocket_heartbeat_interval``) and does not use these helpers.
"""

import asyncio
import contextlib
import functools
import logging
import queue
import threading
import time
from typing import cast

from ._utils import to_json as _to_json

logger = logging.getLogger(__name__)

_shutdown = threading.Event()

STREAM_MIMETYPE = "application/x-ndjson"
# Disable proxy/server buffering so frames reach the browser as they are
# produced (X-Accel-Buffering covers nginx).
STREAM_HEADERS = {"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}

# Emitted when the callback is quiet for longer than the keepalive interval.
# The renderer's NDJSON reader skips blank lines.
KEEPALIVE_LINE = "\n"

_SENTINEL = object()
_KEEPALIVE = object()


def keepalive_seconds(interval_ms):
    """Normalize a configured keepalive interval (ms) to seconds, or None."""
    if not interval_ms or interval_ms <= 0:
        return None
    return interval_ms / 1000


def to_json(value) -> str:
    return cast(str, _to_json(value))


class StreamedCallbackResponse:  # pylint: disable=too-few-public-methods
    """Marker returned by streaming callback wrappers.

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


def _keepalive_frames(marker, keepalive):
    """Yield frames from a sync generator, plus keepalives while it is quiet.

    A blocking ``next()`` cannot be interrupted on a timer, so the frame
    generator is driven on a pump thread and this generator waits on a queue
    instead. One consequence: a client disconnect no longer raises
    ``GeneratorExit`` into the user generator at its current yield — the pump
    notices the stop flag once the next frame arrives, and closes it then. The
    async path (``async def`` callbacks) cancels at the yield as before, which
    is one more reason ``dash._callback`` recommends async for streams.
    """
    frames: queue.Queue = queue.Queue(maxsize=1)
    stop = threading.Event()

    def put(item):
        """Hand one item to the consumer; False if it went away."""
        while not stop.is_set():
            try:
                frames.put(item, timeout=0.2)
                return True
            except queue.Full:
                continue
        return False

    def pump():
        try:
            for frame in iter_stream_frames(marker):
                if not put(("item", frame)):
                    return
            put(("end", None))
        except BaseException as err:  # pylint: disable=broad-exception-caught
            put(("error", err))
        finally:
            # Run the user generator's cleanup inside the callback context so
            # dash.ctx still resolves in its GeneratorExit/finally handlers.
            with contextlib.suppress(Exception):
                marker.ctx.run(marker.frames.close)

    thread = threading.Thread(target=pump, daemon=True, name="dash-stream-pump")
    thread.start()
    poll = min(keepalive, 0.5) if keepalive else 0.5
    try:
        last_activity = time.monotonic()
        while not _shutdown.is_set():
            try:
                kind, value = frames.get(timeout=poll)
            except queue.Empty:
                if keepalive and time.monotonic() - last_activity >= keepalive:
                    yield _KEEPALIVE
                    last_activity = time.monotonic()
                continue
            last_activity = time.monotonic()
            if kind == "item":
                yield value
            elif kind == "error":
                raise value
            else:
                return
    finally:
        stop.set()


async def _akeepalive_frames(frames, keepalive):
    """Yield frames from an async iterator, plus keepalives while it is quiet.

    The pending ``__anext__`` is held across timeouts rather than awaited with
    ``asyncio.wait_for``, which would cancel the user generator mid-step every
    time a keepalive was due.
    """
    iterator = frames.__aiter__()
    pending = None
    try:
        while True:
            pending = asyncio.ensure_future(iterator.__anext__())
            while True:
                done, _ = await asyncio.wait({pending}, timeout=keepalive)
                if done:
                    break
                yield _KEEPALIVE
            try:
                frame = pending.result()
            except StopAsyncIteration:
                return
            finally:
                pending = None
            yield frame
    finally:
        # Reached on client disconnect too: cancel the in-flight step so the
        # user generator sees CancelledError at its current await.
        if pending is not None and not pending.done():
            pending.cancel()


def _line(frame):
    """Serialize one frame or keepalive; ``(line, fatal)`` as _serialize_frame."""
    if frame is _KEEPALIVE:
        return KEEPALIVE_LINE, False
    return _serialize_frame(frame)


def ndjson_lines(marker, keepalive=None):
    """Sync NDJSON body for a sync frame generator (Flask/WSGI)."""
    if keepalive:
        frames = _keepalive_frames(marker, keepalive)
    else:
        frames = iter_stream_frames(marker)
    for frame in frames:
        line, fatal = _line(frame)
        yield line
        if fatal:
            return


async def andjson_lines(frames, keepalive=None):
    """Async NDJSON body over an async iterator of frames."""
    if keepalive:
        frames = _akeepalive_frames(frames, keepalive)
    async for frame in frames:
        line, fatal = _line(frame)
        yield line
        if fatal:
            return


def marker_ndjson_aiter(marker, keepalive=None):
    """Async NDJSON body for either flavor of frame generator."""
    if marker.is_async:
        return andjson_lines(marker.frames, keepalive)
    return andjson_lines(aiter_stream_frames(marker), keepalive)


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
