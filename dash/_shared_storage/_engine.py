"""In-memory store engine shared by the owner process and the single-process
fast path.

Holds the authoritative key/value map and, per topic, an ordered log with a
bounded replay buffer. Sequence numbers are monotonic per topic starting at 1
(``0`` means "before the first message"), so a subscriber tracks a cursor and a
reconnecting one resumes from its last-seen sequence. A consumer that fell
farther behind than the buffer holds gets an explicit gap signal instead of a
silent hole.

The engine is thread-safe and transport-agnostic; sockets live one layer up.
"""

import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, NamedTuple, Optional, Tuple

# Per-topic replay buffer size. Kept small by default because messages are
# arbitrary user payloads and every topic retains up to this many -- unbounded
# defaults are a memory hazard. It still buffers enough to survive normal
# publish bursts and brief reconnects; a producer that outruns a disconnected
# consumer past this raises a gap rather than dropping messages silently.
# Deployments that need a wider reconnect window set buffer_size explicitly.
DEFAULT_BUFFER = 32


class PollResult(NamedTuple):
    messages: List[Any]
    last_seq: int
    gap: bool


class _Topic:  # pylint: disable=too-few-public-methods
    __slots__ = ("seq", "buf", "cond")

    def __init__(self, maxlen: int):
        self.seq = 0
        self.buf: Deque[Tuple[int, Any]] = deque(maxlen=maxlen)
        self.cond = threading.Condition()


class StoreEngine:
    def __init__(self, buffer_size: int = DEFAULT_BUFFER, persistence: Any = None):
        self._buffer_size = buffer_size
        # key -> (value, expiry). expiry is a monotonic deadline, or None for
        # no TTL. Expired entries are dropped lazily on the next read.
        self._data: Dict[str, Tuple[Any, Optional[float]]] = {}
        self._data_lock = threading.Lock()
        self._topics: Dict[str, _Topic] = {}
        self._topics_lock = threading.Lock()
        self._closed = False
        # Optional _Persistence policy (owner only). Notified on each mutation;
        # file IO happens in it, outside _data_lock.
        self._persistence = persistence

    def attach_persistence(self, persistence: Any) -> None:
        """Wire persistence in after construction (so a recover() run that
        populates the store first does not re-mark every restored key dirty)."""
        self._persistence = persistence

    # --- key/value ---------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        with self._data_lock:
            entry = self._data.get(key)
            if entry is None:
                return default
            value, deadline = entry
            if deadline is not None and deadline <= time.monotonic():
                del self._data[key]
                return default
            return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        deadline = time.monotonic() + ttl if ttl is not None else None
        with self._data_lock:
            self._data[key] = (value, deadline)
        if self._persistence is not None:
            self._persistence.mark(key)

    def delete(self, key: str) -> None:
        with self._data_lock:
            existed = self._data.pop(key, None) is not None
        if existed and self._persistence is not None:
            self._persistence.mark(key)

    def restore(self, items: Dict[str, Tuple[Any, Optional[float]]]) -> None:
        """Bulk-load persisted ``key -> (value, expire_at)`` into the store.

        ``expire_at`` is an absolute wall-clock deadline; convert it to a
        monotonic deadline and drop entries that have already expired.
        """
        now_mono = time.monotonic()
        now_wall = time.time()
        with self._data_lock:
            for key, (value, expire_at) in items.items():
                if expire_at is None:
                    self._data[key] = (value, None)
                    continue
                remaining = expire_at - now_wall
                if remaining <= 0:
                    continue
                self._data[key] = (value, now_mono + remaining)

    def snapshot_keys(self, keys: Any) -> Dict[str, Tuple[Any, Optional[float]]]:
        """Return current ``(value, expire_at)`` for each live key in ``keys``.

        Expiry is emitted as an absolute wall-clock deadline for durable
        storage. Keys that are absent or expired are omitted -- the caller
        treats their absence as a deletion.
        """
        now_mono = time.monotonic()
        now_wall = time.time()
        out: Dict[str, Tuple[Any, Optional[float]]] = {}
        with self._data_lock:
            for key in keys:
                entry = self._data.get(key)
                if entry is None:
                    continue
                value, deadline = entry
                if deadline is None:
                    out[key] = (value, None)
                elif deadline > now_mono:
                    out[key] = (value, now_wall + (deadline - now_mono))
                # else: expired -> omit (treated as deleted)
        return out

    # --- pub/sub -----------------------------------------------------------
    def _topic(self, name: str) -> _Topic:
        with self._topics_lock:
            topic = self._topics.get(name)
            if topic is None:
                topic = self._topics[name] = _Topic(self._buffer_size)
            return topic

    def publish(self, topic: str, message: Any) -> int:
        t = self._topic(topic)
        with t.cond:
            t.seq += 1
            t.buf.append((t.seq, message))
            t.cond.notify_all()
            return t.seq

    def head_seq(self, topic: str) -> int:
        """Current highest sequence -- where a fresh subscription starts."""
        t = self._topic(topic)
        with t.cond:
            return t.seq

    def poll(self, topic: str, after_seq: int, timeout: float) -> PollResult:
        """Return messages with sequence > ``after_seq``, waiting up to
        ``timeout`` seconds for at least one. An empty result means the wait
        elapsed (caller re-polls) or the engine closed. ``gap`` is True when the
        next expected message was already evicted from the buffer.
        """
        t = self._topic(topic)
        deadline = time.monotonic() + timeout
        with t.cond:
            while True:
                if self._closed:
                    return PollResult([], after_seq, False)
                # The next message we want is after_seq + 1; if the buffer's
                # oldest is newer than that, it was evicted -> gap.
                if t.buf and after_seq + 1 < t.buf[0][0]:
                    return PollResult([], after_seq, True)
                fresh = [m for (s, m) in t.buf if s > after_seq]
                if fresh:
                    last = t.buf[-1][0]
                    return PollResult(fresh, last, False)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return PollResult([], after_seq, False)
                t.cond.wait(remaining)

    def close(self) -> None:
        self._closed = True
        if self._persistence is not None:
            # Final flush (save-on-exit for persist-reset) + stop its thread.
            self._persistence.close()
        with self._topics_lock:
            topics = list(self._topics.values())
        for t in topics:
            with t.cond:
                t.cond.notify_all()
