"""Backend-agnostic shared state + pub/sub for Dash.

A ``BaseSharedStorage`` gives every worker process a common key/value store and
an ordered publish/subscribe channel. Dash uses it internally (e.g. to route
streaming-callback frames between the worker that runs a callback and the
worker holding the client's streaming connection), and apps can use it directly
for cross-callback or session state without reaching for an external service.

Semantics every backend must honor:

- **Values are picklable.** They may cross a process boundary.
- **Pub/sub is ordered and replayable.** Each ``publish`` to a topic gets a
  monotonically increasing sequence number; a subscriber receives every message
  published after it subscribed, in order. A consumer that drops and resubscribes
  replays what it missed from a bounded buffer, so no message is silently lost
  within that window -- a buffer overrun surfaces as an explicit gap error rather
  than a missing frame.
"""

import abc
from typing import Any, AsyncIterator, Iterator, Optional


class SharedStorageError(Exception):
    """An operation failed on the shared-storage backend."""


class SharedStorageGap(SharedStorageError):
    """Raised by a subscription when messages were evicted before delivery.

    Signals that the replay buffer overran (the consumer fell too far behind),
    or that the owner was re-elected and its buffer was lost; the caller must
    treat it as lost data rather than a clean end of stream.
    """


class Subscription(abc.ABC):
    """A live, ordered view of a topic.

    Iterate it synchronously (``for msg in sub``) or asynchronously
    (``async for msg in sub``) to receive messages as they are published;
    messages buffered since the subscription's cursor replay first. Iteration
    ends when the subscription is closed. Raises ``SharedStorageGap`` if the
    buffer overran while the consumer was behind.

    ``iter_with_seq`` / ``aiter_with_seq`` yield ``(sequence, message)`` pairs so
    a consumer can record its position and resume a later subscription from it
    (via ``replay_from``) -- how the streaming downlink survives a reconnect
    without losing frames. The plain message iterators are built on these.
    """

    @abc.abstractmethod
    def iter_with_seq(self) -> Iterator[Any]:
        ...

    @abc.abstractmethod
    def aiter_with_seq(self) -> AsyncIterator[Any]:
        ...

    @abc.abstractmethod
    def close(self) -> None:
        ...

    def __iter__(self) -> Iterator[Any]:
        for _seq, message in self.iter_with_seq():
            yield message

    def __aiter__(self) -> AsyncIterator[Any]:
        return self._messages()

    async def _messages(self) -> AsyncIterator[Any]:
        async for _seq, message in self.aiter_with_seq():
            yield message

    def __enter__(self) -> "Subscription":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    async def __aenter__(self) -> "Subscription":
        return self

    async def __aexit__(self, *exc) -> None:
        self.close()


class BaseSharedStorage(abc.ABC):
    """Shared key/value store + ordered pub/sub, usable across worker processes.

    A backend must be safe to construct in every worker. However the authoritative
    state is held (a single elected owner, an external service, ...), all workers
    that share a backend see the same keys and topics.
    """

    def start(self) -> None:
        """Prepare the backend for use (elect/attach to the owner, connect, ...).

        Called once per worker before first use. Idempotent.
        """

    def close(self) -> None:
        """Release this worker's handle on the backend. Idempotent."""

    @abc.abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        ...

    @abc.abstractmethod
    def set(self, key: str, value: Any) -> None:
        ...

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        ...

    @abc.abstractmethod
    def publish(self, topic: str, message: Any) -> None:
        """Append ``message`` to ``topic``; delivered to every current subscriber."""

    @abc.abstractmethod
    def subscribe(self, topic: str, replay_from: Optional[int] = None) -> Subscription:
        """Subscribe to ``topic``.

        By default the subscription starts at the topic's current head, so it
        only receives messages published from now on. ``replay_from`` (a sequence
        number a previous subscription last saw) resumes after that point,
        replaying buffered messages -- this is how a reconnecting consumer avoids
        losing frames.
        """
