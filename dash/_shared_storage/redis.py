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
"""
import os
from typing import Any, Optional

from ._codec import decode, encode
from ._engine import DEFAULT_BUFFER, PollResult
from ._polling import PollingSubscription
from .base import BaseSharedStorage, Subscription

# Redis Stream XREAD blocks server-side, so a longer cycle than the diskcache
# sleep-poll is fine; close() latency is bounded by this.
_POLL_TIMEOUT = 5.0
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
        self._prefix = key_prefix
        self._buffer_size = buffer_size
        self._publish_script: Any = None

    def start(self) -> None:
        if self._publish_script is None:
            self._publish_script = self._redis.register_script(_PUBLISH_LUA)

    def close(self) -> None:
        if self._owns_client:
            try:
                self._redis.close()
            except Exception:  # pylint: disable=broad-except
                pass

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

    # --- pub/sub -----------------------------------------------------------
    def publish(self, topic: str, message: Any) -> None:
        self.start()
        self._publish_script(
            keys=[self._seq(topic), self._stream(topic)],
            args=[encode(message), self._buffer_size],
        )

    def _head(self, topic: str) -> int:
        raw = self._redis.get(self._seq(topic))
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
        return PollingSubscription(topic, start, self._poll, _POLL_TIMEOUT)
