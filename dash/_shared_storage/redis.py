"""Redis-backed shared storage, for multi-process AND multi-container use.

Key/value on Redis strings; ordered, replayable pub/sub on a Redis Stream per
topic. This is the backend for horizontally-scaled deployments -- e.g. Dash
Enterprise apps scaled across pods behind a load balancer -- where the
single-machine ``LocalSharedStorage`` / ``DiskcacheSharedStorage`` backends
cannot share state across containers. Redis is the single source of truth, so
there is no owner election.

Sequence numbers are assigned by an atomic server-side script (``INCR`` +
``XADD``) so concurrent publishers stay strictly ordered; the stream is capped
to a bounded window (``MAXLEN``), and a subscriber that falls past the trimmed
floor gets a ``SharedStorageGap``. A topic published with a ``ttl`` keeps it
in a third key, and all three expire that long after the last publish or poll,
so abandoned topics leave Redis.

On an event loop everything goes through ``redis.asyncio``, never the executor:
a blocking XREAD per subscription would hold one executor thread each, and at a
dozen open downlinks every other store call in the worker queues behind them.
Instead each loop gets one reader task that serves all of its subscriptions with
a single multi-stream XREAD, and renews the lifetime of every topic it reads.
"""
import asyncio
import os
import secrets
import threading
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from ._codec import decode, encode, require_msgspec
from ._engine import DEFAULT_BUFFER, PollResult
from ._polling import PollingSubscription
from .base import (
    BaseSharedStorage,
    SharedStorageError,
    Subscription,
    check_topic_ttl,
)

# Redis Stream XREAD blocks server-side, so a longer cycle than the diskcache
# sleep-poll is fine; close() latency is bounded by this.
_POLL_TIMEOUT = 5.0
# The async reader's XREAD block. A new subscription wakes it at once through
# its wake stream; this only bounds how long it lingers once all are gone.
_READER_BLOCK_MS = 5000
_WAKE_TTL_MS = 60_000
_DEFAULT_URL = "redis://localhost:6379"

# A topic's keys live this many ttls past its last publish or poll. A poll on a
# topic with a ttl blocks for at most a third of that lifetime, so a waiting
# reader renews the keys long before they expire.
_TTL_SLACK = 1.25

# Allocate the next sequence and append atomically, so concurrent publishers
# never produce out-of-order stream IDs. Exact MAXLEN (not '~') keeps the replay
# window at exactly buffer_size, so the gap boundary is deterministic.
# Each entry also carries the topic's lifetime, so an async reader learns of a
# changed ttl from the entries it reads.
# KEYS: seq counter, stream, ttl. ARGV: encoded payload, maxlen, lifetime in ms
# (0 for none).
_PUBLISH_LUA = """
local seq = redis.call('INCR', KEYS[1])
local id = seq .. '-0'
if tonumber(ARGV[3]) > 0 then
    redis.call('XADD', KEYS[2], 'MAXLEN', ARGV[2], id, 'm', ARGV[1], 'l', ARGV[3])
    redis.call('SET', KEYS[3], ARGV[3], 'PX', ARGV[3])
    redis.call('PEXPIRE', KEYS[1], ARGV[3])
    redis.call('PEXPIRE', KEYS[2], ARGV[3])
else
    redis.call('XADD', KEYS[2], 'MAXLEN', ARGV[2], id, 'm', ARGV[1])
    redis.call('DEL', KEYS[3])
    redis.call('PERSIST', KEYS[1])
    redis.call('PERSIST', KEYS[2])
end
return seq
"""

# A poll renews the topic's lifetime, if it has one, and reads the head, the
# oldest buffered entry and the lifetime in ms. KEYS: seq counter, stream, ttl.
_POLL_HEAD_LUA = """
local ttl = redis.call('GET', KEYS[3])
if ttl then
    redis.call('PEXPIRE', KEYS[1], ttl)
    redis.call('PEXPIRE', KEYS[2], ttl)
    redis.call('PEXPIRE', KEYS[3], ttl)
end
return {
    redis.call('GET', KEYS[1]),
    redis.call('XRANGE', KEYS[2], '-', '+', 'COUNT', 1),
    ttl,
}
"""


def _require_redis():
    require_msgspec("RedisSharedStorage", "redis")
    try:
        import redis  # type: ignore[import-not-found,import-untyped] # pylint: disable=import-outside-toplevel

        return redis
    except ImportError as exc:
        raise ImportError(
            "RedisSharedStorage requires the redis extra:\n\n"
            '    $ pip install "dash[redis]"\n'
        ) from exc


def _seq_of(stream_id: Any) -> int:
    """Integer sequence from a Redis stream id (``b"7-0"`` / ``"7-0"``)."""
    if isinstance(stream_id, bytes):
        stream_id = stream_id.decode()
    return int(stream_id.split("-")[0])


def _payload_of(fields: dict) -> bytes:
    return fields[b"m"] if b"m" in fields else fields["m"]


def _lifetime_of(fields: dict) -> Optional[int]:
    raw = fields.get(b"l", fields.get("l"))
    return int(raw) if raw else None


def _block_cap_ms(client: Any) -> Optional[int]:
    """The longest XREAD block that returns before the client's socket timeout
    fires: half of it. redis-py 8 defaults the timeout to 5 s, which a 5 s block
    on a quiet stream would hit."""
    try:
        pool = client.connection_pool
        # Read off a connection (never opened): the effective value, defaults
        # included, which the pool's kwargs leave out.
        timeout = pool.connection_class(**pool.connection_kwargs).socket_timeout
    except Exception:  # pylint: disable=broad-except
        return None
    return None if timeout is None else max(1, int(timeout * 1000) // 2)


def _key_of(key: Any) -> str:
    return key.decode() if isinstance(key, bytes) else key


class RedisSubscription(PollingSubscription):
    """A Redis topic subscription. Sync iteration long-polls with XREAD on the
    calling thread; async iteration is fed by the loop's :class:`_StreamReader`.
    """

    # pylint: disable=protected-access

    def __init__(self, storage: "RedisSharedStorage", topic: str, start_seq: int):
        super().__init__(topic, start_seq, storage._poll, _POLL_TIMEOUT, 0.0)
        self._storage = storage
        self._stream_key = storage._stream(topic)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._ready: Optional[asyncio.Event] = None
        self._pending: List[Tuple[int, Any]] = []
        self._error: Optional[BaseException] = None

    @property
    def cursor(self) -> int:
        return self._cursor

    @property
    def failed(self) -> bool:
        return self._error is not None

    def close(self) -> None:
        super().close()
        loop, ready = self._loop, self._ready
        if loop is not None and ready is not None:
            try:
                loop.call_soon_threadsafe(ready.set)
            except RuntimeError:
                pass  # the loop already closed

    def deliver(self, entries: List[Tuple[int, Any]]) -> None:
        """Called by the reader, on the loop, with entries in stream order."""
        for seq, message in entries:
            if seq <= self._cursor:
                continue
            if (
                seq != self._cursor + 1
                or len(self._pending) >= self._storage._buffer_size
            ):
                # Trimmed before the reader got to it, or the consumer fell a
                # whole buffer behind: either way messages are lost.
                self.fail(self._gap())
                return
            self._pending.append((seq, message))
            self._cursor = seq
        self._wake()

    def fail(self, error: BaseException) -> None:
        if self._error is None:
            self._error = error
        self._wake()

    def _wake(self) -> None:
        if self._ready is not None:
            self._ready.set()

    async def _aiter_with_seq(self):
        self._loop = asyncio.get_running_loop()
        self._ready = asyncio.Event()
        if self._closed.is_set():
            return
        reader = self._storage._loop_state().reader
        try:
            head, lifetime_ms = await self._storage._arenew(self._topic)
            if self._cursor > head:
                raise self._gap()
            await reader.add(self, lifetime_ms)
            while not self._closed.is_set():
                if self._pending:
                    pairs, self._pending = self._pending, []
                    for pair in pairs:
                        yield pair
                    continue
                if self._error is not None:
                    raise self._error
                self._ready.clear()
                await self._ready.wait()
        finally:
            reader.remove(self)
            self.close()


class _StreamReader:
    """Serves every async subscription of one storage on one event loop.

    One task XREADs all subscribed streams at once, each from the lowest cursor
    among its subscribers, and hands the entries to each subscription. A new
    subscription interrupts a blocked XREAD through a private wake stream, so it
    is never stuck behind the block timeout.
    """

    # pylint: disable=protected-access

    def __init__(self, storage: "RedisSharedStorage", client: Any):
        self._storage = storage
        self._client = client
        self._subs: Dict[str, Set[RedisSubscription]] = {}
        self._topics: Dict[str, str] = {}
        # Each stream's topic lifetime in ms, None for a topic without a ttl.
        self._lifetimes: Dict[str, Optional[int]] = {}
        self._renewed_at = time.monotonic()
        self._wake_key = f"{storage._prefix}:wake:{secrets.token_hex(8)}"
        self._wake_id = "0-0"
        self._block_cap = _block_cap_ms(client)
        self._task: Optional["asyncio.Task[None]"] = None

    async def add(self, sub: RedisSubscription, lifetime_ms: Optional[int]) -> None:
        self._subs.setdefault(sub._stream_key, set()).add(sub)
        self._topics[sub._stream_key] = sub._topic
        self._lifetimes[sub._stream_key] = lifetime_ms
        if self._task is None:
            self._task = asyncio.ensure_future(self._run())
            return
        async with self._client.pipeline(transaction=False) as pipe:
            pipe.xadd(self._wake_key, {"w": 1}, maxlen=1, approximate=False)
            pipe.pexpire(self._wake_key, _WAKE_TTL_MS)
            await pipe.execute()

    def remove(self, sub: RedisSubscription) -> None:
        subs = self._subs.get(sub._stream_key)
        if subs is not None:
            subs.discard(sub)
            if not subs:
                del self._subs[sub._stream_key]
                del self._topics[sub._stream_key]
                del self._lifetimes[sub._stream_key]

    def _starts(self) -> Dict[str, int]:
        """Where to read each stream from: the lowest cursor among its live
        subscribers. A failed one waits for its consumer to drop it, and must
        not hold the read back meanwhile."""
        starts = {}
        for key, subs in self._subs.items():
            cursors = [sub.cursor for sub in subs if not sub.failed]
            if cursors:
                starts[key] = min(cursors)
        return starts

    def _renew_due(self) -> float:
        """When the topics are next due a renewal, on the monotonic clock: a
        third of the shortest lifetime, as a sync poll would block."""
        lifetimes = [ms for ms in self._lifetimes.values() if ms]
        interval = min(lifetimes) / 3000 if lifetimes else _READER_BLOCK_MS / 1000
        return self._renewed_at + min(interval, _READER_BLOCK_MS / 1000)

    async def _renew(self, keys: List[str]) -> None:
        """Renew the topics' lifetimes, as each sync poll does, and catch a
        stream whose sequence was reset under its subscribers (the keys flushed,
        expired or evicted): XREAD from their cursor would wait until the new
        sequence climbs back past it."""
        script = self._storage._loop_state().poll_head_script
        topics = [self._topics[key] for key in keys]
        async with self._client.pipeline(transaction=False) as pipe:
            for topic in topics:
                await script(keys=self._storage._topic_keys(topic), client=pipe)
            results = await pipe.execute()
        for key, (raw_head, _first, lifetime_ms) in zip(keys, results):
            if key not in self._lifetimes:
                continue  # dropped while the renewal was in flight
            self._lifetimes[key] = int(lifetime_ms) if lifetime_ms else None
            head = int(raw_head) if raw_head is not None else 0
            for sub in self._subs.get(key, ()):
                if sub.cursor > head:
                    sub.fail(sub._gap())

    def _dispatch(self, result: Any, starts: Dict[str, int]) -> None:
        for key, items in result:
            key = _key_of(key)
            if key == self._wake_key:
                self._wake_id = items[-1][0]
                continue
            entries = [
                (_seq_of(entry_id), decode(_payload_of(fields)))
                for entry_id, fields in items
            ]
            if key in self._lifetimes:
                self._lifetimes[key] = _lifetime_of(items[-1][1])
            for sub in self._subs.get(key, ()):
                # Joined behind this read's start while it was in flight: the
                # next read starts from its cursor.
                if sub.cursor >= starts[key]:
                    sub.deliver(entries)

    def _fail_all(self, error: BaseException) -> None:
        for subs in self._subs.values():
            for sub in subs:
                sub.fail(error)
        self._subs.clear()
        self._topics.clear()
        self._lifetimes.clear()

    async def _run(self) -> None:
        error: Optional[BaseException] = None
        try:
            while True:
                starts = self._starts()
                if not starts:
                    return
                if time.monotonic() >= self._renew_due():
                    self._renewed_at = time.monotonic()
                    await self._renew(list(starts))
                    starts = self._starts()
                    if not starts:
                        return
                streams = {key: f"{start}-0" for key, start in starts.items()}
                streams[self._wake_key] = self._wake_id
                block_ms = int((self._renew_due() - time.monotonic()) * 1000)
                if self._block_cap is not None:
                    block_ms = min(block_ms, self._block_cap)
                result = await self._client.xread(streams, block=max(1, block_ms))
                if result:
                    self._dispatch(result, starts)
        except asyncio.CancelledError:
            error = SharedStorageError("the subscription reader stopped")
            raise
        except Exception as exc:  # pylint: disable=broad-except
            # The store is unreachable: end every subscription with the error,
            # as a sync XREAD would, so each consumer can reconnect.
            error = exc
        finally:
            # No await from here on: an add() that lands after this sees no
            # reader and starts a fresh one.
            self._task = None
            if error is not None:
                self._fail_all(error)


class RedisSharedStorage(BaseSharedStorage):
    """Shared storage backed by Redis. Works across processes and containers.

    Pass a ``client`` (an existing ``redis.Redis``, e.g. a Celery result
    backend's) to reuse one connection pool, or a ``url`` (defaults to
    ``$REDIS_URL`` then ``redis://localhost:6379``). Values and published
    messages must be JSON-compatible. A passed client must return bytes
    (``decode_responses=False``, the default).
    """

    def __init__(
        self,
        url: Optional[str] = None,
        client: Any = None,
        key_prefix: str = "dash:ss",
        buffer_size: int = DEFAULT_BUFFER,
    ):
        redis = _require_redis()
        if client is not None:
            self._redis = client
            self._owns_client = False
        else:
            url = url or os.environ.get("REDIS_URL") or _DEFAULT_URL
            self._redis = redis.Redis.from_url(url)
            self._owns_client = True
        self._url = url if client is None else None
        self._block_cap = _block_cap_ms(self._redis)
        self._prefix = key_prefix
        self._buffer_size = buffer_size
        self._publish_script: Any = None
        self._poll_head_script: Any = None
        # One redis.asyncio client (and reader) per event loop: their
        # connections belong to the loop that opened them.
        self._loops: Dict[asyncio.AbstractEventLoop, _LoopState] = {}
        self._loops_lock = threading.Lock()

    def start(self) -> None:
        if self._publish_script is None:
            self._publish_script = self._redis.register_script(_PUBLISH_LUA)
            self._poll_head_script = self._redis.register_script(_POLL_HEAD_LUA)

    def close(self) -> None:
        if self._owns_client:
            try:
                self._redis.close()
            except Exception:  # pylint: disable=broad-except
                pass
        with self._loops_lock:
            states = list(self._loops.items())
            self._loops.clear()
        for loop, state in states:
            # A closed loop's connections can no longer be closed politely.
            if not loop.is_closed():
                try:
                    asyncio.run_coroutine_threadsafe(state.aclose(), loop)
                except RuntimeError:
                    pass  # it closed just now

    def _new_async_client(self) -> Any:
        _require_redis()
        from redis import asyncio as aredis  # type: ignore[import-not-found,import-untyped] # pylint: disable=import-outside-toplevel,import-error

        if self._url is not None:
            return aredis.Redis.from_url(self._url)
        # Same server and options as the client we were handed.
        pool = self._redis.connection_pool
        connection_class = getattr(
            aredis.connection, pool.connection_class.__name__, aredis.Connection
        )
        return aredis.Redis(
            connection_pool=aredis.ConnectionPool(
                connection_class=connection_class, **pool.connection_kwargs
            )
        )

    def _loop_state(self) -> "_LoopState":
        loop = asyncio.get_running_loop()
        with self._loops_lock:
            state = self._loops.get(loop)
            if state is None:
                for old in [old for old in self._loops if old.is_closed()]:
                    del self._loops[old]
                state = self._loops[loop] = _LoopState(self, self._new_async_client())
            return state

    # --- key layout --------------------------------------------------------
    def _kv(self, key: str) -> str:
        return f"{self._prefix}:kv:{key}"

    def _seq(self, topic: str) -> str:
        return f"{self._prefix}:seq:{topic}"

    def _stream(self, topic: str) -> str:
        return f"{self._prefix}:stream:{topic}"

    def _ttl(self, topic: str) -> str:
        return f"{self._prefix}:ttl:{topic}"

    def _topic_keys(self, topic: str):
        return [self._seq(topic), self._stream(topic), self._ttl(topic)]

    # --- key/value ---------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        raw = self._redis.get(self._kv(key))
        return default if raw is None else decode(raw)

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        # px (milliseconds) preserves sub-second ttl; ex only takes whole
        # seconds. Floor at 1ms so a tiny positive ttl still sets an expiry.
        px = max(1, round(ttl * 1000)) if ttl is not None else None
        self._redis.set(self._kv(key), encode(value), px=px)

    def delete(self, key: str) -> None:
        self._redis.delete(self._kv(key))

    async def aget(self, key: str, default: Any = None) -> Any:
        raw = await self._loop_state().client.get(self._kv(key))
        return default if raw is None else decode(raw)

    async def aset(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        px = max(1, round(ttl * 1000)) if ttl is not None else None
        await self._loop_state().client.set(self._kv(key), encode(value), px=px)

    async def adelete(self, key: str) -> None:
        await self._loop_state().client.delete(self._kv(key))

    # --- pub/sub -----------------------------------------------------------
    def publish(self, topic: str, message: Any, ttl: Optional[float] = None) -> None:
        check_topic_ttl(ttl)
        self.start()
        self._publish_script(
            keys=self._topic_keys(topic),
            args=[
                encode(message),
                self._buffer_size,
                round(ttl * _TTL_SLACK * 1000) if ttl is not None else 0,
            ],
        )

    async def apublish(
        self, topic: str, message: Any, ttl: Optional[float] = None
    ) -> None:
        check_topic_ttl(ttl)
        await self._loop_state().publish_script(
            keys=self._topic_keys(topic),
            args=[
                encode(message),
                self._buffer_size,
                round(ttl * _TTL_SLACK * 1000) if ttl is not None else 0,
            ],
        )

    def _head(self, topic: str) -> int:
        raw = self._redis.get(self._seq(topic))
        return int(raw) if raw is not None else 0

    async def _arenew(self, topic: str) -> Tuple[int, Optional[int]]:
        """Renew the topic's lifetime, if it has one; its head and lifetime."""
        raw_head, _first, lifetime_ms = await self._loop_state().poll_head_script(
            keys=self._topic_keys(topic)
        )
        head = int(raw_head) if raw_head is not None else 0
        return head, int(lifetime_ms) if lifetime_ms else None

    def _poll(self, topic: str, after_seq: int, timeout: float) -> PollResult:
        self.start()
        stream = self._stream(topic)
        raw_head, first, lifetime_ms = self._poll_head_script(
            keys=self._topic_keys(topic)
        )
        head = int(raw_head) if raw_head is not None else 0
        # Cursor past the head: it was minted before the stream was reset (the
        # key was flushed, expired, or evicted under a maxmemory policy). Gap so
        # the consumer resets rather than blocking on XREAD until the sequence
        # climbs back past the cursor.
        if after_seq > head:
            return PollResult([], after_seq, True)
        # Gap: the next wanted sequence sits below the trimmed floor. Checked
        # before XREAD, which would otherwise silently resume at the floor.
        if first and after_seq + 1 < _seq_of(first[0][0]):
            return PollResult([], after_seq, True)
        block_ms = int(timeout * 1000)
        if lifetime_ms is not None:
            block_ms = min(block_ms, int(lifetime_ms) // 3)
        if self._block_cap is not None:
            block_ms = min(block_ms, self._block_cap)
        entries = self._redis.xread({stream: f"{after_seq}-0"}, block=max(1, block_ms))
        if not entries:
            return PollResult([], after_seq, False)
        items = entries[0][1]
        messages = [decode(_payload_of(fields)) for (_id, fields) in items]
        return PollResult(messages, _seq_of(items[-1][0]), False)

    def subscribe(self, topic: str, replay_from: Optional[int] = None) -> Subscription:
        start = replay_from if replay_from is not None else self._head(topic)
        return RedisSubscription(self, topic, start)


class _LoopState:  # pylint: disable=too-few-public-methods
    def __init__(self, storage: RedisSharedStorage, client: Any):
        self.client = client
        self.publish_script = client.register_script(_PUBLISH_LUA)
        self.poll_head_script = client.register_script(_POLL_HEAD_LUA)
        self.reader = _StreamReader(storage, client)

    async def aclose(self) -> None:
        # Also the pool a client built around a passed one's options, which
        # aclose() leaves open by default.
        await self.client.aclose(close_connection_pool=True)
