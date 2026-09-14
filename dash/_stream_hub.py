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

Lifecycle. The pump that drives a callback and the downlink that relays its
frames may live on different workers, so "the browser went away" has to travel
through the store too: each downlink records its state under the connection's
key (open on connect, closed on disconnect), and every pump checks that record
periodically. A downlink that has been closed (or never opened) for longer than
``DOWNLINK_GRACE`` -- comfortably longer than the client's reconnect delay --
means the tab is gone, and the pump cancels its callback rather than running it
to completion for nobody.
"""

import asyncio
import contextlib
import json
import logging
import secrets
import time
from contextvars import copy_context
from typing import Any, AsyncIterator, Callable, Iterator, Optional

from ._shared_storage.base import BaseSharedStorage
from ._streaming import StreamedCallbackResponse, sync_iter_asyncgen, to_json

logger = logging.getLogger(__name__)

_TOPIC_PREFIX = "_dash_stream:"
_CONN_PREFIX = "_dash_stream_conn:"

# How long a downlink may stay closed (a reconnect in progress) before the
# pumps on its connection give up on the client. The renderer reconnects one
# second after a drop, so this is generous.
DOWNLINK_GRACE = 10.0
# How often a pump consults the connection record while a callback runs.
DOWNLINK_CHECK_INTERVAL = 2.0

# The uplink's fast acknowledgement -- the streaming callback's POST returns this
# immediately; its outputs arrive on the downlink, not this response.
STREAM_ACK = {"multi": True, "stream": True}

# Terminal frame a pump publishes when it cancels a callback because the
# downlink went away: a client that reconnects late resolves the request
# instead of waiting forever (and holding its downlink open for it).
_CANCELLED_FRAME = {"done": True}


def stream_topic(connection_id: str) -> str:
    return f"{_TOPIC_PREFIX}{connection_id}"


def connection_key(connection_id: str) -> str:
    return f"{_CONN_PREFIX}{connection_id}"


def publish_frame(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    frame: Any,
) -> None:
    """Publish one streaming frame onto a connection's downlink topic.

    A frame may carry ``dash.Patch`` objects (and components) that only Dash's
    JSON encoder understands; reduce it to a plain JSON structure here, before it
    reaches shared storage, whose wire codec is data-only. This also matches what
    the single-connection NDJSON path emits, so the client applies frames
    identically either way.
    """
    plain = json.loads(to_json(frame))
    storage.publish(stream_topic(connection_id), {"rid": request_id, "frame": plain})


# --- downlink lifecycle record ---------------------------------------------


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
            {"open": True, "at": time.time(), "token": self._token},
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self.subscription.close()
        key = connection_key(self.connection_id)
        with contextlib.suppress(Exception):
            current = self.storage.get(key)
            if isinstance(current, dict) and current.get("token") == self._token:
                self.storage.set(
                    key, {"open": False, "at": time.time(), "token": self._token}
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

    ``since`` is when the asking pump started: a record closed *before* that
    (the client's previous streams finished and it hung up) does not count until
    the new downlink has had ``grace`` to open, and a missing record -- the
    downlink's open racing the uplink -- likewise gets ``grace`` to appear.
    """
    if grace is None:
        grace = DOWNLINK_GRACE  # read at call time so it stays tunable
    record = storage.get(connection_key(connection_id))
    if isinstance(record, dict) and record.get("open"):
        return False
    closed_at = record.get("at", 0.0) if isinstance(record, dict) else 0.0
    return time.time() - max(closed_at, since) > grace


def _gone_check(storage: BaseSharedStorage, connection_id: str) -> Callable[[], bool]:
    started = time.time()

    def gone() -> bool:
        try:
            return downlink_gone(storage, connection_id, started)
        except Exception:  # pylint: disable=broad-exception-caught
            # The store is unreachable; the pump's own publish will surface
            # that. Don't cancel a callback over a transient lookup failure.
            return False

    return gone


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


def sync_downlink_marker(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> StreamedCallbackResponse:
    """A downlink as a ``StreamedCallbackResponse`` for the WSGI NDJSON path.

    The relay is long-lived: it carries frames for every callback on the
    connection and ends when the client hangs up -- which the response layer
    signals through ``cancel``, since the relay generator itself may be blocked
    waiting on the store on another thread at that moment.
    """
    downlink = Downlink(storage, connection_id, replay_from)
    return StreamedCallbackResponse(
        downlink.envelopes(),
        is_async=False,
        ctx=copy_context(),
        cancel=downlink.close,
    )


def async_downlink_marker(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> StreamedCallbackResponse:
    """A downlink as a ``StreamedCallbackResponse`` for the ASGI NDJSON path."""
    downlink = Downlink(storage, connection_id, replay_from)
    return StreamedCallbackResponse(
        downlink.aenvelopes(), is_async=True, cancel=downlink.close
    )


# --- pumps -------------------------------------------------------------------


def _publish_cancelled(storage, connection_id, request_id):
    with contextlib.suppress(Exception):
        publish_frame(storage, connection_id, request_id, _CANCELLED_FRAME)


def pump_to_storage(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    marker: StreamedCallbackResponse,
) -> None:
    """Sync driver for WSGI workers: drive the async frame generator on a
    private event loop (via ``sync_iter_asyncgen``) and publish each frame.
    Runs on a background thread so the callback's POST returns immediately.

    Stops -- cancelling the callback at its current ``await`` -- once the
    connection's downlink has been gone for ``DOWNLINK_GRACE``.
    """
    gone = _gone_check(storage, connection_id)
    frames = sync_iter_asyncgen(
        marker.frames, should_stop=gone, check_interval=DOWNLINK_CHECK_INTERVAL
    )
    completed = False
    try:
        for frame in frames:
            publish_frame(storage, connection_id, request_id, frame)
            completed = bool(frame.get("done"))
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Streaming callback pump failed")
        _publish_cancelled(storage, connection_id, request_id)
        completed = True
    finally:
        frames.close()
        if not completed:
            _publish_cancelled(storage, connection_id, request_id)


async def apump_to_storage(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    marker: StreamedCallbackResponse,
) -> None:
    """Drive an async streaming callback and publish each frame to the topic.

    Runs as a background task on the uplink worker so the callback's POST can
    return immediately. The frame generator already emits the terminal
    ``{"done": True}``; publishing it lets the client resolve that request.

    Like :func:`pump_to_storage`, gives up once the downlink has been gone for
    ``DOWNLINK_GRACE``: the pending step is cancelled, which raises into the
    user generator at its current ``await``.
    """
    gone = _gone_check(storage, connection_id)
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
                if gone():
                    return
            try:
                frame = step.result()
            except StopAsyncIteration:
                return
            finally:
                step = None
            publish_frame(storage, connection_id, request_id, frame)
            completed = bool(frame.get("done"))
            if time.monotonic() >= next_check:
                next_check = time.monotonic() + DOWNLINK_CHECK_INTERVAL
                if gone():
                    return
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Streaming callback pump failed")
        completed = True
        _publish_cancelled(storage, connection_id, request_id)
    finally:
        if step is not None and not step.done():
            step.cancel()
            with contextlib.suppress(BaseException):
                await step
        with contextlib.suppress(Exception):
            await marker.frames.aclose()
        if not completed:
            _publish_cancelled(storage, connection_id, request_id)


# Keep a reference to in-flight pump tasks so the loop doesn't GC them mid-stream.
_pending_pumps: "set[asyncio.Task]" = set()


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
    "STREAM_ACK",
    "apump_to_storage",
    "async_downlink_marker",
    "connection_key",
    "downlink_gone",
    "publish_frame",
    "pump_to_storage",
    "spawn_async_pump",
    "stream_topic",
    "subscribe_envelopes",
    "sync_downlink_marker",
]
