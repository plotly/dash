"""Tests for RedisSharedStorage (KV + Redis Streams pub/sub).

Requires a reachable Redis (``$REDIS_URL`` or ``redis://localhost:6379``); the
tests skip when none is available. The CI shared-storage job provides one. Each
test uses a unique key prefix so a shared Redis stays isolated.
"""
import asyncio
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

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


def test_kv_ttl_expires(store):
    store.set("a", "v", ttl=0.2)
    assert store.get("a") == "v"
    time.sleep(0.35)
    assert store.get("a", "gone") == "gone"


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


# --- asyncio path -------------------------------------------------------------


async def _first(sub):
    async for pair in sub.aiter_with_seq():
        return pair
    return None


def test_async_subscriptions_hold_no_executor_threads(store):
    """Open async subscriptions must not occupy the loop's executor: on an ASGI
    worker every other store call (the pumps' publishes, the downlink records)
    would queue behind them."""

    async def scenario():
        executor = ThreadPoolExecutor(max_workers=1)
        asyncio.get_running_loop().set_default_executor(executor)
        subs = [store.subscribe(f"t{i}", replay_from=0) for i in range(20)]
        try:
            await asyncio.wait_for(check(subs), timeout=5)
        finally:
            for sub in subs:
                sub.close()
            executor.shutdown(wait=False, cancel_futures=True)

    async def check(subs):
        readers = [asyncio.ensure_future(_first(sub)) for sub in subs]
        await asyncio.sleep(0.3)  # every reader is now waiting

        started = time.monotonic()
        await store.aset("k", 1)
        assert await store.aget("k") == 1
        for i in range(20):
            await store.apublish(f"t{i}", f"m{i}")
        got = await asyncio.wait_for(asyncio.gather(*readers), timeout=2)
        assert got == [(1, f"m{i}") for i in range(20)]
        assert time.monotonic() - started < 1.0
        await store.adelete("k")
        assert await store.aget("k", "gone") == "gone"

    asyncio.run(scenario())


def test_async_replay_and_live_messages_in_order(store):
    store.publish("t", "m1")
    store.publish("t", "m2")

    async def scenario():
        out = []
        sub = store.subscribe("t", replay_from=1)
        async for pair in sub.aiter_with_seq():
            out.append(pair)
            if len(out) == 1:
                await store.apublish("t", "m3")
            if len(out) == 2:
                await store.apublish("t", "m4")
            if len(out) == 3:
                break
        return out

    assert asyncio.run(scenario()) == [(2, "m2"), (3, "m3"), (4, "m4")]


def test_async_subscribers_with_different_cursors_share_a_topic(store):
    for i in range(3):
        store.publish("t", f"m{i}")

    async def scenario():
        late = store.subscribe("t")  # at the head: seq 3
        early = store.subscribe("t", replay_from=0)
        late_first = asyncio.ensure_future(_first(late))
        assert await _first(early) == (1, "m0")
        await asyncio.sleep(0.1)
        await store.apublish("t", "m3")
        return await asyncio.wait_for(late_first, timeout=2)

    assert asyncio.run(scenario()) == (4, "m3")


def test_async_gap_when_buffer_overruns():
    prefix = f"dash:sstest:{uuid.uuid4().hex[:12]}"
    store = RedisSharedStorage(url=REDIS_URL, key_prefix=prefix, buffer_size=2)
    for i in range(5):
        store.publish("t", f"m{i}")  # stream trimmed to seqs 4,5

    async def scenario(replay_from):
        sub = store.subscribe("t", replay_from=replay_from)
        with pytest.raises(SharedStorageGap):
            await _first(sub)

    asyncio.run(scenario(1))  # wants seq 2, trimmed away
    asyncio.run(scenario(9))  # cursor past the head: the store was reset
    store.close()


def test_async_subscription_close_from_another_thread_ends_iteration(store):
    async def scenario():
        sub = store.subscribe("t")
        reader = asyncio.ensure_future(_first(sub))
        await asyncio.sleep(0.2)
        threading.Thread(target=sub.close).start()
        return await asyncio.wait_for(reader, timeout=1)

    assert asyncio.run(scenario()) is None


def test_async_path_with_a_passed_client():
    client = redis.Redis.from_url(REDIS_URL)
    store = RedisSharedStorage(
        client=client, key_prefix=f"dash:sstest:{uuid.uuid4().hex[:12]}"
    )

    async def scenario():
        await store.aset("a", {"x": 1})
        reader = asyncio.ensure_future(_first(store.subscribe("t")))
        await asyncio.sleep(0.1)
        await store.apublish("t", "m")
        return await store.aget("a"), await asyncio.wait_for(reader, timeout=2)

    assert asyncio.run(scenario()) == ({"x": 1}, (1, "m"))
    assert store.get("a") == {"x": 1}
    store.close()
    client.close()


def test_async_subscriber_joining_behind_a_read_in_flight_gets_no_false_gap(store):
    """A reconnecting downlink replays from behind while another subscription to
    the same topic is parked in the reader's XREAD: the read in flight started
    past the newcomer's cursor, which must not count as lost messages."""
    for i in range(5):
        store.publish("t", f"m{i}")

    async def head(_topic):
        return 10**9

    async def scenario():
        parked = store.subscribe("t")  # at the head: seq 5
        parked_first = asyncio.ensure_future(_first(parked))
        await asyncio.sleep(0.3)  # the reader is blocked reading from seq 5
        store._ahead = head  # joins without an await before the reader sees it
        store.publish("t", "m5")
        out = []
        async for pair in store.subscribe("t", replay_from=1).aiter_with_seq():
            out.append(pair)
            if len(out) == 5:
                break
        return out, await asyncio.wait_for(parked_first, timeout=2)

    out, parked = asyncio.run(scenario())
    assert out == [(2, "m1"), (3, "m2"), (4, "m3"), (5, "m4"), (6, "m5")]
    assert parked == (6, "m5")


def test_async_clients_of_closed_loops_are_dropped(store):
    for _ in range(3):
        asyncio.run(store.aget("k"))
    assert len(store._loops) == 1
