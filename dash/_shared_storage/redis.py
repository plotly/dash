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
floor gets a ``SharedStorageGap``.

On an event loop everything goes through ``redis.asyncio``, never the executor:
a blocking XREAD per subscription would hold one executor thread each, and at a
dozen open downlinks every other store call in the worker queues behind them.
Instead each loop gets one reader task that serves all of its subscriptions with
a single multi-stream XREAD.
"""
import asyncio
import os
import secrets
import threading
from typing import Any, Dict, List, Optional, Set, Tuple

from ._codec import decode, encode
from ._engine import DEFAULT_BUFFER, PollResult
from ._polling import PollingSubscription
from .base import BaseSharedStorage, SharedStorageError, Subscription

# Redis Stream XREAD blocks server-side, so a longer cycle than the diskcache
# sleep-poll is fine; close() latency is bounded by this.
_POLL_TIMEOUT = 5.0
# The async reader's XREAD block. A new subscription wakes it at once through
# its wake stream; this only bounds how long it lingers once all are gone.
_READER_BLOCK_MS = 5000
_WAKE_TTL_MS = 60_000
_DEFAULT_URL = "redis://localhost:6379"

# Allocate the next sequence and append atomically, so concurrent publishers
# never produce out-of-order stream IDs. Exact MAXLEN (not '~') keeps the replay
# window at exactly buffer_size, so the gap boundary is deterministic.
# KEYS: seq counter, stream key. ARGV: encoded payload, maxlen.
_PUBLISH_LUA = """
local seq = redis.call('INCR', KEYS[1])
redis.call('XADD', KEYS[2], 'MAXLEN', ARGV[2], seq .. '-0', 'm', ARGV[1])
return seq
"""


def _require_redis():
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
            if self._cursor > await self._storage._ahead(self._topic):
                raise self._gap()
            await reader.add(self)
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
        self._wake_key = f"{storage._prefix}:wake:{secrets.token_hex(8)}"
        self._wake_id = "0-0"
        self._task: Optional["asyncio.Task[None]"] = None

    async def add(self, sub: RedisSubscription) -> None:
        self._subs.setdefault(sub._stream_key, set()).add(sub)
        self._topics[sub._stream_key] = sub._topic
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

    async def _check_heads(self, starts: Dict[str, int]) -> None:
        """On a quiet cycle, catch a stream whose sequence was reset under its
        subscribers (the keys flushed or evicted): XREAD from their cursor would
        wait until the new sequence climbs back past it."""
        keys = [key for key in starts if key in self._topics]
        async with self._client.pipeline(transaction=False) as pipe:
            for key in keys:
                pipe.get(self._storage._seq(self._topics[key]))
            heads = await pipe.execute()
        for key, raw in zip(keys, heads):
            if starts[key] > (int(raw) if raw is not None else 0):
                for sub in list(self._subs.get(key, ())):
                    sub.fail(sub._gap())

    async def _run(self) -> None:
        error: Optional[BaseException] = None
        try:
            while True:
                starts = self._starts()
                if not starts:
                    return
                streams = {key: f"{start}-0" for key, start in starts.items()}
                streams[self._wake_key] = self._wake_id
                result = await self._client.xread(streams, block=_READER_BLOCK_MS)
                if not result:
                    await self._check_heads(starts)
                    continue
                for key, items in result:
                    key = _key_of(key)
                    if key == self._wake_key:
                        self._wake_id = items[-1][0]
                        continue
                    entries = [
                        (_seq_of(entry_id), decode(_payload_of(fields)))
                        for entry_id, fields in items
                    ]
                    start = starts[key]
                    for sub in list(self._subs.get(key, ())):
                        # Joined behind this read's start while it was in
                        # flight: the next read starts from its cursor.
                        if sub.cursor >= start:
                            sub.deliver(entries)
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
                for subs in self._subs.values():
                    for sub in subs:
                        sub.fail(error)
                self._subs.clear()
                self._topics.clear()


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
        self._prefix = key_prefix
        self._buffer_size = buffer_size
        self._publish_script: Any = None
        # One redis.asyncio client (and reader) per event loop: their
        # connections belong to the loop that opened them.
        self._loops: Dict[asyncio.AbstractEventLoop, _LoopState] = {}
        self._loops_lock = threading.Lock()

    def start(self) -> None:
        if self._publish_script is None:
            self._publish_script = self._redis.register_script(_PUBLISH_LUA)

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
        from redis import asyncio as aredis  # type: ignore[import-not-found,import-untyped] # pylint: disable=import-outside-toplevel

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
    def publish(self, topic: str, message: Any) -> None:
        self.start()
        self._publish_script(
            keys=[self._seq(topic), self._stream(topic)],
            args=[encode(message), self._buffer_size],
        )

    async def apublish(self, topic: str, message: Any) -> None:
        await self._loop_state().publish_script(
            keys=[self._seq(topic), self._stream(topic)],
            args=[encode(message), self._buffer_size],
        )

    def _head(self, topic: str) -> int:
        raw = self._redis.get(self._seq(topic))
        return int(raw) if raw is not None else 0

    async def _ahead(self, topic: str) -> int:
        raw = await self._loop_state().client.get(self._seq(topic))
        return int(raw) if raw is not None else 0

    def _poll(self, topic: str, after_seq: int, timeout: float) -> PollResult:
        stream = self._stream(topic)
        # Cursor past the head: it was minted before the stream was reset (the
        # key was flushed, or evicted under a maxmemory policy). Gap so the
        # consumer resets rather than blocking on XREAD until the sequence climbs
        # back past the cursor.
        if after_seq > self._head(topic):
            return PollResult([], after_seq, True)
        # Gap: the next wanted sequence sits below the trimmed floor. Checked
        # before XREAD, which would otherwise silently resume at the floor.
        first = self._redis.xrange(stream, count=1)
        if first and after_seq + 1 < _seq_of(first[0][0]):
            return PollResult([], after_seq, True)
        entries = self._redis.xread(
            {stream: f"{after_seq}-0"}, block=max(1, int(timeout * 1000))
        )
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
        self.reader = _StreamReader(storage, client)

    async def aclose(self) -> None:
        # Also the pool a client built around a passed one's options, which
        # aclose() leaves open by default.
        await self.client.aclose(close_connection_pool=True)
