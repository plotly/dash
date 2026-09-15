"""Multiplexed streaming over shared storage.

A browser holds a single downlink NDJSON connection identified by a
``connection_id``. Every streaming callback publishes its frames -- each tagged
with the callback's ``request_id`` -- to that connection's shared-storage topic;
the downlink subscribes to the topic and relays the frames to the client, which
routes them back to the right callback by ``request_id`` and closes the downlink
once no streams remain running.

Because the frames travel through the shared store (not the HTTP response of the
callback that produced them), the worker that runs a callback and the worker
that holds the downlink do not have to be the same process -- the store is the
broker. Reconnecting a dropped downlink resumes from its cursor, so the store's
replay buffer covers the gap without losing frames.

Downlink line shape (one JSON object per NDJSON line)::

    {"rid": "<request_id>", "frame": {<the usual streaming frame>}}

where ``frame`` is a ``CallbackExecutionResponse`` frame or a ``{"done": true}``
terminal, exactly as the single-callback NDJSON transport emits today.

Two downlink shapes. On ASGI the downlink is one long-lived response per
browser: it costs no thread, so it simply stays open (``async_downlink_marker``).
On WSGI a response holds a worker thread for its whole life, so a long-lived
downlink per browser would exhaust any thread pool at a few dozen browsers;
there the browser *polls* instead (``poll_downlink``): each request returns
whatever frames are queued since its cursor and ends at once, taking a thread
for milliseconds. The client re-polls at its poll interval while frames flow and
backs off while quiet, so latency stays near the interval and a small pool
serves many browsers. The pumps themselves are tasks on one event-loop thread
per WSGI process (``pump_to_storage``), not a thread per stream.

Lifecycle. The pump that drives a callback and the downlink that relays its
frames may live on different workers, so "the browser went away" has to travel
through the store too: each downlink records its state under the connection's
key -- open/closed for a long-lived downlink, a heartbeat per poll otherwise --
and every pump checks that record periodically. A downlink closed, silent, or
never opened for longer than ``DOWNLINK_GRACE`` means the browser is gone, and
the pump cancels its callback rather than running it to completion for nobody.
When the downlink is shared by several tabs (the renderer's SharedWorker
transport), a closing tab instead sends an explicit ``streamCancel`` for each
of its requests, recorded under a per-request key the same pump check picks up.

Shutdown. An ASGI server drains in-flight responses before it stops, and a
downlink is an in-flight response that never ends on its own, so Ctrl+C would
wait forever (uvicorn: "Waiting for connections to close"). The ASGI backends
therefore install a SIGINT/SIGTERM hook that ends every live downlink and
cancels every pump, then hands the signal on to the server's own handler.
"""

import asyncio
import atexit
import contextlib
import json
import logging
import os
import secrets
import signal
import threading
import time
from typing import Any, AsyncIterator, Callable, Iterator, List, Optional

from ._shared_storage.base import BaseSharedStorage
from ._streaming import StreamedCallbackResponse, to_json

logger = logging.getLogger(__name__)

_TOPIC_PREFIX = "_dash_stream:"
_CONN_PREFIX = "_dash_stream_conn:"
_CANCEL_PREFIX = "_dash_stream_cancel:"

# How long a downlink may stay closed (a reconnect in progress) before the
# pumps on its connection give up on the client. The renderer reconnects one
# second after a drop, so this is generous.
DOWNLINK_GRACE = 10.0
# How long a polling browser may go without a poll reaching the server before
# it counts as gone. It polls at least once a second while it has streams, but
# on an overloaded WSGI pool its polls can queue for many seconds -- and an
# overload must cost latency, never the stream itself.
POLL_GRACE = 30.0
# How often a pump consults the connection record while a callback runs.
DOWNLINK_CHECK_INTERVAL = 2.0

# The uplink's fast acknowledgement -- the streaming callback's POST returns this
# immediately; its outputs arrive on the downlink, not this response.
STREAM_ACK = {"multi": True, "stream": True}
# Acknowledgement of a ``streamCancel`` request.
STREAM_CANCEL_ACK = {"multi": True, "stream": True, "cancelled": True}

# Terminal frame a pump publishes when it cancels a callback because the
# downlink went away: a client that reconnects late resolves the request
# instead of waiting forever (and holding its downlink open for it).
_CANCELLED_FRAME = {"done": True}


def stream_topic(connection_id: str) -> str:
    return f"{_TOPIC_PREFIX}{connection_id}"


def connection_key(connection_id: str) -> str:
    return f"{_CONN_PREFIX}{connection_id}"


def cancel_key(connection_id: str, request_id: str) -> str:
    return f"{_CANCEL_PREFIX}{connection_id}:{request_id}"


def _envelope(request_id: str, frame: Any) -> Any:
    """Reduce a frame to plain JSON inside its downlink envelope.

    A frame may carry ``dash.Patch`` objects (and components) that only Dash's
    JSON encoder understands; reduce it to a plain JSON structure here, before it
    reaches shared storage, whose wire codec is data-only. This also matches what
    the single-connection NDJSON path emits, so the client applies frames
    identically either way.
    """
    return {"rid": request_id, "frame": json.loads(to_json(frame))}


def publish_frame(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    frame: Any,
) -> None:
    """Publish one streaming frame onto a connection's downlink topic."""
    storage.publish(stream_topic(connection_id), _envelope(request_id, frame))


async def apublish_frame(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    frame: Any,
) -> None:
    """:func:`publish_frame` for the pumps: never blocks their event loop."""
    await storage.apublish(stream_topic(connection_id), _envelope(request_id, frame))


# --- downlink lifecycle record ---------------------------------------------


# Every downlink currently being served by this process, so shutdown can end
# them (the responses they feed never end on their own).
_live_downlinks: "set[Downlink]" = set()
_live_lock = threading.Lock()


class Downlink:
    """One served downlink: its topic subscription plus its lifecycle record.

    ``close`` is thread-safe and idempotent, so the response consumer can call it
    the moment the client hangs up (``StreamedCallbackResponse.cancel``) even
    while the relay generator is blocked in a poll on another thread; the relay
    then ends within one poll cycle. Closing only rewrites the connection record
    if it still carries this downlink's token, so a downlink that was replaced by
    a reconnect cannot mark the new one closed when it finally winds down.
    """

    def __init__(
        self,
        storage: BaseSharedStorage,
        connection_id: str,
        replay_from: Optional[int] = None,
    ):
        self.storage = storage
        self.connection_id = connection_id
        self.subscription = storage.subscribe(stream_topic(connection_id), replay_from)
        self._token = secrets.token_hex(8)
        self._closed = False
        storage.set(
            connection_key(connection_id),
            {
                "mode": "stream",
                "open": True,
                "at": time.time(),
                "token": self._token,
            },
        )
        with _live_lock:
            _live_downlinks.add(self)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        with _live_lock:
            _live_downlinks.discard(self)
        self.subscription.close()
        key = connection_key(self.connection_id)
        with contextlib.suppress(Exception):
            current = self.storage.get(key)
            if isinstance(current, dict) and current.get("token") == self._token:
                self.storage.set(
                    key,
                    {
                        "mode": "stream",
                        "open": False,
                        "at": time.time(),
                        "token": self._token,
                    },
                )

    def envelopes(self) -> Iterator[Any]:
        """Sync relay: yield envelopes until the subscription ends or is closed."""
        try:
            for seq, message in self.subscription.iter_with_seq():
                yield {**message, "seq": seq}
        finally:
            self.close()

    async def aenvelopes(self) -> AsyncIterator[Any]:
        """Async counterpart of :meth:`envelopes` for ASGI backends."""
        try:
            async for seq, message in self.subscription.aiter_with_seq():
                yield {**message, "seq": seq}
        finally:
            self.close()


def downlink_gone(
    storage: BaseSharedStorage,
    connection_id: str,
    since: float,
    grace: Optional[float] = None,
) -> bool:
    """Whether a connection's downlink has been away for longer than ``grace``.

    A long-lived downlink is away once it recorded itself closed; a polling
    browser is away once its last poll is older than ``grace``. ``since`` is
    when the asking pump started: a record closed or last polled *before* that
    (the client's previous streams finished and it went quiet) does not count
    until the new downlink has had ``grace`` to show up, and a missing record --
    the downlink racing the uplink -- likewise gets ``grace`` to appear.
    """
    return _judge_gone(storage.get(connection_key(connection_id)), since, grace)


def _judge_gone(record: Any, since: float, grace: Optional[float]) -> bool:
    if not isinstance(record, dict):
        last_alive = 0.0
    elif record.get("mode") == "poll":
        last_alive = record.get("at", 0.0)  # every poll is a heartbeat
        if grace is None:
            grace = POLL_GRACE
    elif record.get("open"):
        return False
    else:
        last_alive = record.get("at", 0.0)  # when it closed
    if grace is None:
        grace = DOWNLINK_GRACE  # read at call time so it stays tunable
    return time.time() - max(last_alive, since) > grace


def cancel_stream(
    storage: BaseSharedStorage, connection_id: str, request_id: str
) -> None:
    """Ask the pump driving one callback to stop.

    The client sends this when a request's consumer is gone while the shared
    downlink stays open for other tabs -- a browser tab closed -- so the
    callback does not run to completion for nobody. The pump on whichever
    worker runs it notices within ``DOWNLINK_CHECK_INTERVAL``.
    """
    storage.set(cancel_key(connection_id, request_id), time.time())


def stream_cancelled(
    storage: BaseSharedStorage, connection_id: str, request_id: str
) -> bool:
    return storage.get(cancel_key(connection_id, request_id)) is not None


def _stop_check(
    storage: BaseSharedStorage, connection_id: str, request_id: str
) -> Callable[[], Any]:
    """Whether a pump should give up: its request was cancelled, or the
    connection's downlink has been gone for longer than the grace period.
    Async, and through the store's loop-native operations: pumps share one
    event loop, which a blocking round trip would stall for every stream."""
    started = time.time()

    async def stop() -> bool:
        try:
            if await storage.aget(cancel_key(connection_id, request_id)) is not None:
                return True
            record = await storage.aget(connection_key(connection_id))
            return _judge_gone(record, started, None)
        except Exception:  # pylint: disable=broad-exception-caught
            # The store is unreachable; the pump's own publish will surface
            # that. Don't cancel a callback over a transient lookup failure.
            return False

    return stop


# --- downlink markers --------------------------------------------------------


def subscribe_envelopes(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> Iterator[Any]:
    """Yield a connection's downlink envelopes until the subscription ends.

    Convenience over :class:`Downlink` for consumers that drive the relay
    themselves (tests, tooling). Each envelope carries its ``seq`` so the client
    can resume from it after a reconnect without losing frames.
    """
    return Downlink(storage, connection_id, replay_from).envelopes()


# Last heartbeat written per connection by this process: a browser polls many
# times a second, the pumps only need to hear from it every DOWNLINK_GRACE.
_HEARTBEAT_INTERVAL = 1.0
_last_heartbeat: "dict[str, float]" = {}
_HEARTBEAT_CACHE_LIMIT = 50_000


def _heartbeat(storage: BaseSharedStorage, connection_id: str) -> None:
    now = time.time()
    if now - _last_heartbeat.get(connection_id, 0.0) < _HEARTBEAT_INTERVAL:
        return
    if len(_last_heartbeat) > _HEARTBEAT_CACHE_LIMIT:
        _last_heartbeat.clear()  # bounded; a miss only costs one extra write
    _last_heartbeat[connection_id] = now
    storage.set(
        connection_key(connection_id), {"mode": "poll", "open": True, "at": now}
    )


def poll_downlink(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> List[Any]:
    """One poll of a connection's downlink for the WSGI path: the envelopes
    published since ``replay_from``, without waiting, and (at most once a
    second) a heartbeat on the connection record so the pumps know the
    browser is still there.

    Costs a worker thread for milliseconds rather than for the browser's
    whole visit, which is what lets a WSGI pool serve many browsers.
    """
    sub = storage.subscribe(stream_topic(connection_id), replay_from or 0)
    try:
        pairs = sub.poll(0.0)
    finally:
        sub.close()
    _heartbeat(storage, connection_id)
    return [{**message, "seq": seq} for seq, message in pairs]


def async_downlink_marker(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> StreamedCallbackResponse:
    """A downlink as a ``StreamedCallbackResponse`` for the ASGI NDJSON path."""
    install_shutdown_hook()
    downlink = Downlink(storage, connection_id, replay_from)
    return StreamedCallbackResponse(downlink.aenvelopes(), is_async=True)


# --- pumps -------------------------------------------------------------------


async def _publish_cancelled(storage, connection_id, request_id):
    with contextlib.suppress(Exception):
        await apublish_frame(storage, connection_id, request_id, _CANCELLED_FRAME)


async def _forget_cancel(storage, connection_id, request_id):
    with contextlib.suppress(Exception):
        await storage.adelete(cancel_key(connection_id, request_id))


# In-flight pump tasks (ASGI server loop or the WSGI pump loop): keeps them
# referenced so their loop doesn't GC them mid-stream, and lets shutdown cancel
# them.
_pending_pumps: "set[asyncio.Task]" = set()


# --- WSGI pumps: one event-loop thread per process ---------------------------
#
# A pump drives an async generator, so it is naturally a task. Under WSGI there
# is no server loop to put it on, so the process runs one of its own: every
# pump in the worker is a task on that loop, and a worker can drive thousands
# of streams without a thread (let alone a thread pair and a private loop) per
# stream.

_pump_loop: Optional[asyncio.AbstractEventLoop] = None
_pump_thread: Optional[threading.Thread] = None
_pump_loop_lock = threading.Lock()
_pump_exit_hook_installed = False
_pump_loop_stopping = False


def _run_pump_loop(loop: asyncio.AbstractEventLoop, ready: threading.Event) -> None:
    asyncio.set_event_loop(loop)
    ready.set()
    while not loop.is_closed():
        try:
            loop.run_forever()
            return  # stopped on purpose
        except BaseException:  # pylint: disable=broad-exception-caught
            # Something was raised *into* this thread (a test harness that
            # stops "every thread the app started", a stray async exception).
            # This thread carries every stream in the process; it does not
            # exit on anyone's behalf but its own shutdown.
            if _pump_loop_stopping:
                return
            logger.warning("Stream pump loop interrupted; resuming", exc_info=True)


def _shared_pump_loop() -> asyncio.AbstractEventLoop:
    global _pump_loop, _pump_thread  # pylint: disable=global-statement
    global _pump_exit_hook_installed  # pylint: disable=global-statement
    with _pump_loop_lock:
        thread_alive = _pump_thread is not None and _pump_thread.is_alive()
        if _pump_loop is None or _pump_loop.is_closed() or not thread_alive:
            if _pump_loop is not None and not _pump_loop.is_closed():
                # The thread died under the loop (something raised into it,
                # e.g. a test harness stopping "all new threads"): its pumps
                # are lost, but streaming must not stay dead for the process.
                logger.warning("Stream pump loop thread died; starting a new one")
                with contextlib.suppress(Exception):
                    _pump_loop.close()
            loop = asyncio.new_event_loop()
            ready = threading.Event()
            thread = threading.Thread(
                target=_run_pump_loop,
                args=(loop, ready),
                daemon=True,
                name="dash-stream-pumps",
            )
            thread.start()
            ready.wait()
            _pump_loop, _pump_thread = loop, thread
            if not _pump_exit_hook_installed:
                # End the pumps before interpreter teardown finalizes their
                # loop and generators half-way (which logs spurious errors).
                _pump_exit_hook_installed = True
                atexit.register(_stop_pump_loop)
        return _pump_loop


def _stop_pump_loop() -> None:
    global _pump_loop_stopping  # pylint: disable=global-statement
    loop, thread = _pump_loop, _pump_thread
    if loop is None or loop.is_closed() or thread is None or not thread.is_alive():
        return
    _pump_loop_stopping = True
    shutdown_streams()

    async def drain():
        pending = [t for t in _pending_pumps if not t.done()]
        if pending:
            await asyncio.wait(pending, timeout=2.0)

    with contextlib.suppress(Exception):
        asyncio.run_coroutine_threadsafe(drain(), loop).result(timeout=3.0)
    loop.call_soon_threadsafe(loop.stop)
    thread.join(timeout=2.0)


async def _tracked_pump(storage, connection_id, request_id, marker):
    task = asyncio.current_task()
    _pending_pumps.add(task)
    try:
        await apump_to_storage(storage, connection_id, request_id, marker)
    finally:
        _pending_pumps.discard(task)


def pump_to_storage(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    marker: StreamedCallbackResponse,
):
    """WSGI entry point: schedule the pump for one streaming callback on the
    process's shared pump loop and return at once, so the callback's POST acks
    immediately. Returns a ``concurrent.futures.Future`` that resolves when
    the pump ends (useful to wait on in tests).

    The pump stops -- cancelling the callback at its current ``await`` -- once
    the request is cancelled or the connection's downlink has been gone for
    ``DOWNLINK_GRACE``.
    """
    return asyncio.run_coroutine_threadsafe(
        _tracked_pump(storage, connection_id, request_id, marker),
        _shared_pump_loop(),
    )


async def apump_to_storage(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    marker: StreamedCallbackResponse,
) -> None:
    """Drive an async streaming callback and publish each frame to the topic.

    Runs as a task -- on the server's loop under ASGI, on the process's shared
    pump loop under WSGI (:func:`pump_to_storage`) -- so the callback's POST
    can return immediately. The frame generator already emits the terminal
    ``{"done": True}``; publishing it lets the client resolve that request.

    Gives up once the request is cancelled or the downlink has been gone for
    ``DOWNLINK_GRACE``: the pending step is cancelled, which raises into the
    user generator at its current ``await``.
    """
    stop = _stop_check(storage, connection_id, request_id)
    iterator = marker.frames.__aiter__()
    next_check = time.monotonic() + DOWNLINK_CHECK_INTERVAL
    completed = False
    step = None
    try:
        while True:
            step = asyncio.ensure_future(iterator.__anext__())
            while True:
                done, _ = await asyncio.wait(
                    {step}, timeout=max(0.0, next_check - time.monotonic())
                )
                if done:
                    break
                next_check = time.monotonic() + DOWNLINK_CHECK_INTERVAL
                if await stop():
                    return
            try:
                frame = step.result()
            except StopAsyncIteration:
                return
            finally:
                step = None
            await apublish_frame(storage, connection_id, request_id, frame)
            completed = bool(frame.get("done"))
            if time.monotonic() >= next_check:
                next_check = time.monotonic() + DOWNLINK_CHECK_INTERVAL
                if await stop():
                    return
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Streaming callback pump failed")
        completed = True
        await _publish_cancelled(storage, connection_id, request_id)
    finally:
        if step is not None and not step.done():
            step.cancel()
            with contextlib.suppress(BaseException):
                await step
        with contextlib.suppress(Exception):
            await marker.frames.aclose()
        if not completed:
            await _publish_cancelled(storage, connection_id, request_id)
        await _forget_cancel(storage, connection_id, request_id)


# --- process shutdown --------------------------------------------------------


def shutdown_streams() -> None:
    """End every live downlink and cancel every pump in this process.

    Safe to call from a signal handler: subscriptions close with a flag and a
    socket close, and task cancellation is scheduled onto each task's loop.
    """
    with _live_lock:
        downlinks = list(_live_downlinks)
    for downlink in downlinks:
        with contextlib.suppress(Exception):
            downlink.close()
    for task in list(_pending_pumps):
        with contextlib.suppress(Exception):
            task.get_loop().call_soon_threadsafe(task.cancel)


_shutdown_hook_installed = False


def install_shutdown_hook() -> None:
    """Chain :func:`shutdown_streams` in front of the process's SIGINT/SIGTERM
    handlers, once, from the main thread (the only place signal handlers can
    be set -- which under an ASGI server is also the event-loop thread).

    ASGI servers stop accepting and then wait for in-flight responses before
    they shut the app down; a downlink never ends by itself, so without this
    Ctrl+C hangs until forced. Whatever handler the server installed still
    runs afterwards, unchanged.
    """
    global _shutdown_hook_installed  # pylint: disable=global-statement
    if (
        _shutdown_hook_installed
        or threading.current_thread() is not threading.main_thread()
    ):
        return
    _shutdown_hook_installed = True
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            previous = signal.getsignal(sig)
        except (ValueError, OSError):  # pragma: no cover - platform quirks
            continue

        def handler(signum, frame, previous=previous):
            shutdown_streams()
            if callable(previous):
                previous(signum, frame)
            elif previous == signal.SIG_DFL:
                # Restore the default disposition and re-deliver the signal
                # so the process still dies the way it would have.
                signal.signal(signum, signal.SIG_DFL)
                os.kill(os.getpid(), signum)

        with contextlib.suppress(ValueError, OSError):
            signal.signal(sig, handler)


def spawn_async_pump(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    marker: StreamedCallbackResponse,
) -> None:
    """Run the pump as a fire-and-forget task on the ASGI event loop, so the
    callback's request returns immediately while frames keep flowing.
    """
    task = asyncio.ensure_future(
        apump_to_storage(storage, connection_id, request_id, marker)
    )
    _pending_pumps.add(task)
    task.add_done_callback(_pending_pumps.discard)


__all__ = [
    "DOWNLINK_CHECK_INTERVAL",
    "DOWNLINK_GRACE",
    "Downlink",
    "POLL_GRACE",
    "STREAM_ACK",
    "STREAM_CANCEL_ACK",
    "apublish_frame",
    "apump_to_storage",
    "async_downlink_marker",
    "cancel_key",
    "cancel_stream",
    "connection_key",
    "downlink_gone",
    "install_shutdown_hook",
    "poll_downlink",
    "publish_frame",
    "pump_to_storage",
    "shutdown_streams",
    "spawn_async_pump",
    "stream_cancelled",
    "stream_topic",
    "subscribe_envelopes",
]
