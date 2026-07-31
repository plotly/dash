"""Tests for RedisSharedStorage (KV + Redis Streams pub/sub).

Requires a reachable Redis (``$REDIS_URL`` or ``redis://localhost:6379``); the
tests skip when none is available. The CI shared-storage job provides one. Each
test uses a unique key prefix so a shared Redis stays isolated.
"""
import os
import threading
import time
import uuid

import pytest

redis = pytest.importorskip("redis")

# pylint: disable=wrong-import-position
from dash._shared_storage import (  # noqa: E402
    RedisSharedStorage,
    SharedStorageGap,
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


def _redis_available():
    try:
        client = redis.Redis.from_url(REDIS_URL)
        client.ping()
        client.close()
        return True
    except Exception:  # pylint: disable=broad-except
        return False


pytestmark = pytest.mark.skipif(
    not _redis_available(), reason="no Redis reachable at REDIS_URL"
)


@pytest.fixture
def store():
    prefix = f"dash:sstest:{uuid.uuid4().hex[:12]}"
    s = RedisSharedStorage(url=REDIS_URL, key_prefix=prefix)
    s.start()
    try:
        yield s
    finally:
        s.close()


def _drain(sub, n):
    out = []
    for msg in sub:
        out.append(msg)
        if len(out) == n:
            break
    return out


def test_kv_get_set_delete(store):
    assert store.get("missing") is None
    assert store.get("missing", 42) == 42
    store.set("a", {"x": 1})
    assert store.get("a") == {"x": 1}
    store.delete("a")
    assert store.get("a") is None
    store.delete("a")  # idempotent


def test_fresh_subscriber_only_sees_future_messages(store):
    store.publish("t", "old")
    sub = store.subscribe("t")  # cursor at current head
    received = []
    th = threading.Thread(target=lambda: received.extend(_drain(sub, 2)))
    th.start()
    time.sleep(0.3)
    store.publish("t", "new1")
    store.publish("t", "new2")
    th.join(timeout=5)
    sub.close()
    assert received == ["new1", "new2"]


def test_replay_from_cursor(store):
    store.publish("t", "m1")
    store.publish("t", "m2")
    store.publish("t", "m3")
    sub = store.subscribe("t", replay_from=1)  # saw up to seq 1
    assert _drain(sub, 2) == ["m2", "m3"]
    sub.close()


def test_gap_when_buffer_overruns():
    prefix = f"dash:sstest:{uuid.uuid4().hex[:12]}"
    store = RedisSharedStorage(url=REDIS_URL, key_prefix=prefix, buffer_size=2)
    store.start()
    for i in range(5):
        store.publish("t", f"m{i}")  # seqs 1..5; stream trimmed to 4,5
    sub = store.subscribe("t", replay_from=1)  # wants seq 2, trimmed away
    with pytest.raises(SharedStorageGap):
        next(iter(sub))
    sub.close()
    store.close()


def test_no_gap_at_buffer_edge():
    prefix = f"dash:sstest:{uuid.uuid4().hex[:12]}"
    store = RedisSharedStorage(url=REDIS_URL, key_prefix=prefix, buffer_size=2)
    store.start()
    for i in range(4):
        store.publish("t", f"m{i}")  # seqs 1..4; stream holds 3,4
    sub = store.subscribe("t", replay_from=2)  # wants seq 3, still held
    assert _drain(sub, 2) == ["m2", "m3"]
    sub.close()
    store.close()


def test_two_instances_share_state(store):
    """A second client (separate connection pool) sees the first's writes and
    published messages -- the multi-worker / multi-pod case."""
    other = RedisSharedStorage(url=REDIS_URL, key_prefix=store._prefix)
    other.start()

    store.set("shared", {"n": 42})
    assert other.get("shared") == {"n": 42}

    sub = other.subscribe("topic")
    received = []
    th = threading.Thread(target=lambda: received.extend(_drain(sub, 3)))
    th.start()
    time.sleep(0.3)
    for i in range(3):
        store.publish("topic", f"m{i}")
    th.join(timeout=5)
    sub.close()
    other.close()
    assert received == ["m0", "m1", "m2"]
