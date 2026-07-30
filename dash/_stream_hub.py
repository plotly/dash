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

from typing import Any, AsyncIterator, Iterator, Optional

from ._shared_storage.base import BaseSharedStorage
from ._streaming import StreamedCallbackResponse, sync_iter_asyncgen

_TOPIC_PREFIX = "_dash_stream:"


def stream_topic(connection_id: str) -> str:
    return f"{_TOPIC_PREFIX}{connection_id}"


def publish_frame(
    storage: BaseSharedStorage,
    connection_id: str,
    request_id: str,
    frame: Any,
) -> None:
    """Publish one streaming frame onto a connection's downlink topic."""
    storage.publish(stream_topic(connection_id), {"rid": request_id, "frame": frame})


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
    reconnecting downlink from its last cursor.
    """
    with storage.subscribe(stream_topic(connection_id), replay_from) as sub:
        yield from sub


async def asubscribe_envelopes(
    storage: BaseSharedStorage,
    connection_id: str,
    replay_from: Optional[int] = None,
) -> AsyncIterator[Any]:
    """Async counterpart of :func:`subscribe_envelopes` for ASGI backends."""
    sub = storage.subscribe(stream_topic(connection_id), replay_from)
    try:
        async for envelope in sub:
            yield envelope
    finally:
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
