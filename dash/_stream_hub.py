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
"""

import asyncio
import json
import threading
from typing import Any, AsyncIterator, Iterator, Optional

from ._shared_storage.base import BaseSharedStorage, SharedStorageGap, Subscription
from ._streaming import StreamedCallbackResponse, sync_iter_asyncgen, to_json

_TOPIC_PREFIX = "_dash_stream:"

# The uplink's fast acknowledgement -- the streaming callback's POST returns this
# immediately; its outputs arrive on the downlink, not this response.
STREAM_ACK = {"multi": True, "stream": True}

# Control envelope telling the client its cursor is stale (its frames were lost
# to an owner re-election or a server restart) and it must reset to the head and
# resubscribe, rather than stall waiting for the fresh sequence to pass it.
RESET_ENVELOPE = {"reset": True}


def stream_topic(connection_id: str) -> str:
    return f"{_TOPIC_PREFIX}{connection_id}"


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


# Open downlink subscriptions, so a server shutdown can close them (each one
# otherwise blocks its worker in a long poll, stalling a graceful shutdown).
# Guarded by a lock: subscriptions open/close on worker threads while a shutdown
# hook iterates the set, and a plain set is not safe against that.
_active_subscriptions: "set[Subscription]" = set()
_registry_lock = threading.Lock()


def subscribe_envelopes(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> Iterator[Any]:
    """Yield a connection's downlink envelopes until the subscription ends.

    These frames feed a ``StreamedCallbackResponse`` so the existing NDJSON
    response path serializes and keep-alives them -- no bespoke endpoint. It is
    long-lived: it carries frames for every callback on the connection, not one
    stream, and ends when the client hangs up. ``replay_from`` resumes a
    reconnecting downlink from its last cursor. Each envelope carries its ``seq``
    so the client can resume from it after a reconnect without losing frames. A
    lost buffer (owner re-election, server restart) surfaces as a single reset
    envelope so the client resets its cursor instead of stalling.
    """
    sub = storage.subscribe(stream_topic(connection_id), replay_from)
    with _registry_lock:
        _active_subscriptions.add(sub)
    try:
        for seq, message in sub.iter_with_seq():
            yield {**message, "seq": seq}
    except SharedStorageGap:
        yield dict(RESET_ENVELOPE)
    finally:
        with _registry_lock:
            _active_subscriptions.discard(sub)
        sub.close()


async def asubscribe_envelopes(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> AsyncIterator[Any]:
    """Async counterpart of :func:`subscribe_envelopes` for ASGI backends."""
    sub = storage.subscribe(stream_topic(connection_id), replay_from)
    with _registry_lock:
        _active_subscriptions.add(sub)
    try:
        async for seq, message in sub.aiter_with_seq():
            yield {**message, "seq": seq}
    except SharedStorageGap:
        yield dict(RESET_ENVELOPE)
    finally:
        with _registry_lock:
            _active_subscriptions.discard(sub)
        sub.close()


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
    """
    async for frame in marker.frames:
        publish_frame(storage, connection_id, request_id, frame)


def pump_to_storage(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    marker: StreamedCallbackResponse,
) -> None:
    """Sync driver for WSGI workers: drive the async frame generator on a
    private event loop (via ``sync_iter_asyncgen``) and publish each frame.
    Runs on a background thread so the callback's POST returns immediately.
    """
    for frame in sync_iter_asyncgen(marker.frames):
        publish_frame(storage, connection_id, request_id, frame)


def async_downlink_marker(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> StreamedCallbackResponse:
    """A downlink as a ``StreamedCallbackResponse`` for the ASGI NDJSON path."""
    return StreamedCallbackResponse(
        asubscribe_envelopes(storage, connection_id, replay_from), is_async=True
    )


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


def shutdown_active_streams() -> None:
    """Stop every in-flight stream so the server can shut down.

    Sets the module-level shutdown flag so keepalive generators exit on their
    next timeout, cancels background pump tasks, and closes open downlink
    subscriptions. Each downlink otherwise sits in a long poll that a graceful
    shutdown would wait on forever. Backends call this from their shutdown
    hook. Idempotent and safe to call when nothing is streaming.
    """
    from ._streaming import _shutdown  # pylint: disable=import-outside-toplevel

    _shutdown.set()
    for task in list(_pending_pumps):
        task.cancel()
    with _registry_lock:
        subscriptions = list(_active_subscriptions)
    for sub in subscriptions:
        sub.close()
