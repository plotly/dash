"""In-memory store engine shared by the owner process and the single-process
fast path.

Holds the authoritative key/value map and, per topic, an ordered log with a
bounded replay buffer. Sequence numbers are monotonic per topic starting at 1
(``0`` means "before the first message"), so a subscriber tracks a cursor and a
reconnecting one resumes from its last-seen sequence. A consumer that fell
farther behind than the buffer holds gets an explicit gap signal instead of a
silent hole.

The engine is thread-safe and transport-agnostic; sockets live one layer up.
``poll`` blocks a thread; ``apoll`` parks an asyncio task on a future that
``publish`` resolves from whichever thread it runs on, so an ASGI server can
hold thousands of subscriptions without an executor thread each.

A topic nobody publishes to, polls or subscribes to for ``topic_ttl`` seconds
is dropped, buffer and sequence both, so per-session topics do not pile up for
the life of the process. A later publish starts it over at sequence 1.
"""

import asyncio
import contextlib
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, Iterator, List, NamedTuple, Optional, Tuple

# Per-topic replay buffer size. Kept small by default because messages are
# arbitrary user payloads and every topic retains up to this many -- unbounded
# defaults are a memory hazard. It still buffers enough to survive normal
# publish bursts and brief reconnects; a producer that outruns a disconnected
# consumer past this raises a gap rather than dropping messages silently.
# Deployments that need a wider reconnect window set buffer_size explicitly.
DEFAULT_BUFFER = 32

# How long an untouched topic is kept. Long enough to outlast a streaming
# downlink's reconnect and poll grace windows many times over, short enough that
# a busy app does not hold every finished session's frames for hours.
DEFAULT_TOPIC_TTL = 300.0


class PollResult(NamedTuple):
    messages: List[Any]
    last_seq: int
    gap: bool


_Waiter = Tuple[asyncio.AbstractEventLoop, "asyncio.Future[None]"]


class _Topic:  # pylint: disable=too-few-public-methods
    __slots__ = ("seq", "buf", "cond", "waiters", "users", "touched")

    def __init__(self, maxlen: int, now: float):
        self.seq = 0
        self.buf: Deque[Tuple[int, Any]] = deque(maxlen=maxlen)
        self.cond = threading.Condition()
        # asyncio tasks parked in apoll(), woken by the next publish/close.
        self.waiters: List[_Waiter] = []
        # Calls currently holding this topic (a blocked poll among them), and
        # when the last one let go. Both guarded by the engine's _topics_lock.
        self.users = 0
        self.touched = now


def _wake(fut: "asyncio.Future[None]") -> None:
    if not fut.done():
        fut.set_result(None)


class StoreEngine:
    def __init__(
        self,
        buffer_size: int = DEFAULT_BUFFER,
        persistence: Any = None,
        topic_ttl: Optional[float] = DEFAULT_TOPIC_TTL,
    ):
        self._buffer_size = buffer_size
        self._topic_ttl = topic_ttl
        self._next_sweep = 0.0
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

    @property
    def closed(self) -> bool:
        return self._closed

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
    @contextlib.contextmanager
    def _use(self, name: str) -> Iterator[_Topic]:
        """Hold a topic for one call. A held topic is never swept, so a
        publish cannot land in a topic that was just dropped from the map."""
        now = time.monotonic()
        with self._topics_lock:
            self._sweep(now)
            topic = self._topics.get(name)
            if topic is None:
                topic = self._topics[name] = _Topic(self._buffer_size, now)
            topic.users += 1
        try:
            yield topic
        finally:
            with self._topics_lock:
                topic.users -= 1
                topic.touched = time.monotonic()

    def _sweep(self, now: float) -> None:
        """Under ``_topics_lock``: drop topics idle past the ttl. Runs at most
        every quarter ttl, so a topic lives between 1 and 1.25 ttl idle."""
        if self._topic_ttl is None or now < self._next_sweep:
            return
        self._next_sweep = now + self._topic_ttl / 4
        cutoff = now - self._topic_ttl
        idle = [
            name
            for name, t in self._topics.items()
            if t.users == 0 and t.touched < cutoff
        ]
        for name in idle:
            del self._topics[name]

    def publish(self, topic: str, message: Any) -> int:
        with self._use(topic) as t:
            with t.cond:
                t.seq += 1
                t.buf.append((t.seq, message))
                t.cond.notify_all()
                waiters, t.waiters = t.waiters, []
                seq = t.seq
        for loop, fut in waiters:
            loop.call_soon_threadsafe(_wake, fut)
        return seq

    def head_seq(self, topic: str) -> int:
        """Current highest sequence -- where a fresh subscription starts."""
        with self._use(topic) as t:
            with t.cond:
                return t.seq

    def _ready(self, t: _Topic, after_seq: int) -> Optional[PollResult]:
        """Under ``t.cond``: the result available right now, or None to wait."""
        if self._closed:
            return PollResult([], after_seq, False)
        # The cursor points past every sequence this topic has ever produced.
        # That can only happen when the cursor was minted by a previous
        # incarnation of the topic (the owner was re-elected, or the server
        # restarted with an empty store) -- treat it as a gap so the consumer
        # resets instead of stalling until the fresh sequence climbs back past
        # the stale cursor.
        if after_seq > t.seq:
            return PollResult([], after_seq, True)
        # The next message we want is after_seq + 1; if the buffer's oldest is
        # newer than that, it was evicted -> gap.
        if t.buf and after_seq + 1 < t.buf[0][0]:
            return PollResult([], after_seq, True)
        fresh = [m for (s, m) in t.buf if s > after_seq]
        if fresh:
            return PollResult(fresh, t.buf[-1][0], False)
        return None

    def poll(self, topic: str, after_seq: int, timeout: float) -> PollResult:
        """Return messages with sequence > ``after_seq``, waiting up to
        ``timeout`` seconds for at least one. An empty result means the wait
        elapsed (caller re-polls) or the engine closed. ``gap`` is True when the
        next expected message was already evicted from the buffer.
        """
        deadline = time.monotonic() + timeout
        with self._use(topic) as t:
            with t.cond:
                while True:
                    res = self._ready(t, after_seq)
                    if res is not None:
                        return res
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return PollResult([], after_seq, False)
                    t.cond.wait(remaining)

    async def apoll(self, topic: str, after_seq: int, timeout: float) -> PollResult:
        """:meth:`poll` for asyncio: parks the task on a future instead of
        blocking a thread; ``publish`` (from any thread) or ``close`` wakes it."""
        with self._use(topic) as t:
            return await self._apoll(t, after_seq, timeout)

    async def _apoll(self, t: _Topic, after_seq: int, timeout: float) -> PollResult:
        loop = asyncio.get_running_loop()
        deadline = time.monotonic() + timeout
        while True:
            with t.cond:
                res = self._ready(t, after_seq)
                if res is not None:
                    return res
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return PollResult([], after_seq, False)
                fut: "asyncio.Future[None]" = loop.create_future()
                waiter = (loop, fut)
                t.waiters.append(waiter)
            try:
                await asyncio.wait_for(asyncio.shield(fut), remaining)
            except asyncio.TimeoutError:
                return PollResult([], after_seq, False)
            finally:
                if not fut.done():
                    with t.cond:
                        if waiter in t.waiters:
                            t.waiters.remove(waiter)

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
                waiters, t.waiters = t.waiters, []
            for loop, fut in waiters:
                loop.call_soon_threadsafe(_wake, fut)
