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
"""

import asyncio
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, NamedTuple, Optional, Tuple

# Per-topic replay buffer size. Sized to cover a reconnect window comfortably;
# a producer that outruns a disconnected consumer past this raises a gap rather
# than dropping messages silently.
DEFAULT_BUFFER = 2048


class PollResult(NamedTuple):
    messages: List[Any]
    last_seq: int
    gap: bool


_Waiter = Tuple[asyncio.AbstractEventLoop, "asyncio.Future[None]"]


class _Topic:  # pylint: disable=too-few-public-methods
    __slots__ = ("seq", "buf", "cond", "waiters")

    def __init__(self, maxlen: int):
        self.seq = 0
        self.buf: Deque[Tuple[int, Any]] = deque(maxlen=maxlen)
        self.cond = threading.Condition()
        # asyncio tasks parked in apoll(), woken by the next publish/close.
        self.waiters: List[_Waiter] = []


def _wake(fut: "asyncio.Future[None]") -> None:
    if not fut.done():
        fut.set_result(None)


class StoreEngine:
    def __init__(self, buffer_size: int = DEFAULT_BUFFER):
        self._buffer_size = buffer_size
        self._data: Dict[str, Any] = {}
        self._data_lock = threading.Lock()
        self._topics: Dict[str, _Topic] = {}
        self._topics_lock = threading.Lock()
        self._closed = False

    @property
    def closed(self) -> bool:
        return self._closed

    # --- key/value ---------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        with self._data_lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._data_lock:
            self._data[key] = value

    def delete(self, key: str) -> None:
        with self._data_lock:
            self._data.pop(key, None)

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
            waiters, t.waiters = t.waiters, []
            seq = t.seq
        for loop, fut in waiters:
            loop.call_soon_threadsafe(_wake, fut)
        return seq

    def head_seq(self, topic: str) -> int:
        """Current highest sequence -- where a fresh subscription starts."""
        t = self._topic(topic)
        with t.cond:
            return t.seq

    def _ready(self, t: _Topic, after_seq: int) -> Optional[PollResult]:
        """Under ``t.cond``: the result available right now, or None to wait."""
        if self._closed:
            return PollResult([], after_seq, False)
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
        t = self._topic(topic)
        deadline = time.monotonic() + timeout
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
        t = self._topic(topic)
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
        with self._topics_lock:
            topics = list(self._topics.values())
        for t in topics:
            with t.cond:
                t.cond.notify_all()
                waiters, t.waiters = t.waiters, []
            for loop, fut in waiters:
                loop.call_soon_threadsafe(_wake, fut)
