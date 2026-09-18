"""Disk-backed shared storage (diskcache), for single-machine multi-process use.

Key/value and ordered pub/sub on a ``diskcache.Cache`` -- the same store the
``DiskcacheManager`` background-callback backend uses. Every process on one host
that opens the same cache directory shares state, so it gives multi-worker
parity with ``LocalSharedStorage`` without a socket owner.

It is NOT for multi-container / multi-pod deployments: each pod has its own
ephemeral disk, so pods would not see each other's state. Use
``RedisSharedStorage`` there.

Pub/sub is an append log: an atomic per-topic counter assigns monotonic
sequence numbers, each message is stored under its sequence and old sequences
are trimmed to a bounded window, and subscribers poll for sequences past their
cursor. A consumer that falls farther behind than the window gets a
``SharedStorageGap``.
"""
import time
from typing import Any, Optional

from ._codec import decode, encode
from ._engine import DEFAULT_BUFFER, PollResult
from ._polling import PollingSubscription
from .base import BaseSharedStorage, Subscription

# Poll cycle: short so a subscription's close() stays responsive; diskcache has
# no server-side blocking wait, so this is a sleep-poll loop.
_POLL_TIMEOUT = 1.0
_POLL_INTERVAL = 0.05


def _require_diskcache():
    try:
        import diskcache  # type: ignore[import-not-found,import-untyped] # pylint: disable=import-outside-toplevel

        return diskcache
    except ImportError as exc:
        raise ImportError(
            "DiskcacheSharedStorage requires the diskcache extra:\n\n"
            '    $ pip install "dash[diskcache]"\n'
        ) from exc


class DiskcacheSharedStorage(BaseSharedStorage):
    """Shared storage backed by a ``diskcache.Cache``. Single machine, not pods.

    Pass an existing ``cache`` (e.g. the one a ``DiskcacheManager`` already
    holds) to share one store, or a ``directory`` to open/create one. Values and
    published messages must be JSON-compatible.
    """

    def __init__(
        self,
        cache: Any = None,
        directory: Optional[str] = None,
        buffer_size: int = DEFAULT_BUFFER,
    ):
        diskcache = _require_diskcache()
        if cache is not None:
            if not isinstance(cache, (diskcache.Cache, diskcache.FanoutCache)):
                raise ValueError(
                    "cache must be a diskcache.Cache or diskcache.FanoutCache"
                )
            self._cache = cache
            self._owns_cache = False
        else:
            self._cache = diskcache.Cache(directory)
            self._owns_cache = True
        self._buffer_size = buffer_size

    def close(self) -> None:
        if self._owns_cache:
            self._cache.close()

    # --- key layout --------------------------------------------------------
    @staticmethod
    def _kv(key: str) -> str:
        return f"ss:kv:{key}"

    @staticmethod
    def _seq(topic: str) -> str:
        return f"ss:seq:{topic}"

    @staticmethod
    def _msg(topic: str, seq: int) -> str:
        return f"ss:msg:{topic}:{seq}"

    # --- key/value ---------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        raw = self._cache.get(self._kv(key))
        return default if raw is None else decode(raw)

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        self._cache.set(self._kv(key), encode(value), expire=ttl)

    def delete(self, key: str) -> None:
        self._cache.delete(self._kv(key))

    # --- pub/sub -----------------------------------------------------------
    def publish(self, topic: str, message: Any) -> None:
        payload = encode(message)
        with self._cache.transact():
            seq = int(self._cache.incr(self._seq(topic)))
            self._cache.set(self._msg(topic, seq), payload)
            evicted = seq - self._buffer_size
            if evicted >= 1:
                self._cache.delete(self._msg(topic, evicted))

    def _head(self, topic: str) -> int:
        return int(self._cache.get(self._seq(topic), 0))

    def _poll(self, topic: str, after_seq: int, timeout: float) -> PollResult:
        deadline = time.monotonic() + timeout
        while True:
            head = self._head(topic)
            # Cursor past the head: it was minted before the store was reset
            # (the cache was cleared, or the counter evicted under the cache's
            # size limit). Gap so the consumer resets rather than blocking until
            # the sequence climbs back past the cursor.
            if after_seq > head:
                return PollResult([], after_seq, True)
            if head > after_seq:
                floor = max(1, head - self._buffer_size + 1)
                if after_seq + 1 < floor:
                    return PollResult([], after_seq, True)
                messages = []
                for seq in range(after_seq + 1, head + 1):
                    raw = self._cache.get(self._msg(topic, seq))
                    if raw is None:
                        # Trimmed between the head read and this fetch -> gap.
                        return PollResult([], after_seq, True)
                    messages.append(decode(raw))
                return PollResult(messages, head, False)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return PollResult([], after_seq, False)
            time.sleep(min(_POLL_INTERVAL, remaining))

    def subscribe(self, topic: str, replay_from: Optional[int] = None) -> Subscription:
        start = replay_from if replay_from is not None else self._head(topic)
        return PollingSubscription(topic, start, self._poll, _POLL_TIMEOUT)
