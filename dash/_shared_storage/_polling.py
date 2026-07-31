"""Subscription for poll-based backends.

A backend that can answer ``poll(topic, after_seq, timeout) -> PollResult``
builds its live subscriptions from this: it drives the poll loop, tracks the
cursor, resumes from it on every call, and turns a buffer overrun into
``SharedStorageGap``. ``LocalSharedStorage`` has its own reconnecting
subscription (it also handles owner re-election); this serves the diskcache and
Redis backends, whose store is always reachable.
"""
import asyncio
import threading
from typing import Callable

from ._engine import PollResult
from .base import SharedStorageGap, Subscription

PollFn = Callable[[str, int, float], PollResult]


class PollingSubscription(Subscription):
    """Iterate a topic by repeatedly polling ``poll_fn`` from a moving cursor."""

    def __init__(
        self, topic: str, start_seq: int, poll_fn: PollFn, poll_timeout: float
    ):
        self._topic = topic
        self._cursor = start_seq
        self._poll_fn = poll_fn
        self._poll_timeout = poll_timeout
        self._closed = threading.Event()

    def close(self) -> None:
        self._closed.set()

    def _gap(self) -> SharedStorageGap:
        return SharedStorageGap(f"replay buffer overran on topic {self._topic!r}")

    @staticmethod
    def _with_seq(res: PollResult):
        # Poll batches are contiguous, ending at last_seq, so each message's
        # sequence follows from its position.
        first = res.last_seq - len(res.messages) + 1
        for offset, message in enumerate(res.messages):
            yield first + offset, message

    def iter_with_seq(self):
        try:
            while not self._closed.is_set():
                res = self._poll_fn(self._topic, self._cursor, self._poll_timeout)
                if res.gap:
                    raise self._gap()
                yield from self._with_seq(res)
                self._cursor = res.last_seq
        finally:
            self.close()

    def aiter_with_seq(self):
        return self._aiter_with_seq()

    async def _aiter_with_seq(self):
        loop = asyncio.get_running_loop()
        try:
            while not self._closed.is_set():
                try:
                    res = await loop.run_in_executor(
                        None,
                        self._poll_fn,
                        self._topic,
                        self._cursor,
                        self._poll_timeout,
                    )
                except RuntimeError:
                    # The loop/executor is shutting down -- end cleanly.
                    break
                if res.gap:
                    raise self._gap()
                for pair in self._with_seq(res):
                    yield pair
                self._cursor = res.last_seq
        finally:
            self.close()
