"""Tests for DiskcacheSharedStorage (KV + sequenced pub/sub on a disk cache).

Covers the contract semantics (future-only subscribe, replay, gap) in-process
and cross-process visibility over a shared cache directory. Requires the
diskcache extra, which the shared-storage CI job installs.
"""
import multiprocessing as mp
import threading
import time

import pytest

from dash._shared_storage import DiskcacheSharedStorage, SharedStorageGap

CTX = mp.get_context("spawn")


@pytest.fixture
def store(tmp_path):
    s = DiskcacheSharedStorage(directory=str(tmp_path / "cache"))
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
    time.sleep(0.2)
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


def test_gap_when_buffer_overruns(tmp_path):
    store = DiskcacheSharedStorage(directory=str(tmp_path / "c"), buffer_size=2)
    for i in range(5):
        store.publish("t", f"m{i}")  # seqs 1..5; only 4,5 retained
    sub = store.subscribe("t", replay_from=1)  # wants seq 2, evicted
    with pytest.raises(SharedStorageGap):
        next(iter(sub))
    sub.close()
    store.close()


def test_no_gap_at_buffer_edge(tmp_path):
    store = DiskcacheSharedStorage(directory=str(tmp_path / "c"), buffer_size=2)
    for i in range(4):
        store.publish("t", f"m{i}")  # seqs 1..4; 3,4 retained
    sub = store.subscribe("t", replay_from=2)  # wants seq 3, still held
    assert _drain(sub, 2) == ["m2", "m3"]
    sub.close()
    store.close()


def test_idle_topic_leaves_the_cache(tmp_path):
    store = DiskcacheSharedStorage(directory=str(tmp_path / "c"), topic_ttl=0.3)
    for i in range(3):
        store.publish("t", f"m{i}")
    time.sleep(0.5)
    assert store._cache.get(store._seq("t")) is None
    assert all(store._cache.get(store._msg("t", n)) is None for n in (1, 2, 3))
    store.publish("t", "again")
    assert store._head("t") == 1  # starts over
    store.close()


def test_polling_keeps_the_topic_counter(tmp_path):
    store = DiskcacheSharedStorage(directory=str(tmp_path / "c"), topic_ttl=0.4)
    store.publish("t", "m")
    sub = store.subscribe("t", replay_from=1)
    for _ in range(5):
        time.sleep(0.2)
        assert sub.poll(0.0) == []
    # Past the ttl since the publish, but read all along: the counter stays,
    # so the next publish continues the sequence instead of restarting it.
    store.publish("t", "m2")
    assert sub.poll(0.0) == [(2, "m2")]
    store.close()


def test_topic_ttl_none_sets_no_expiry(tmp_path):
    store = DiskcacheSharedStorage(directory=str(tmp_path / "c"), topic_ttl=None)
    store.publish("t", "m")
    _value, expire = store._cache.get(store._seq("t"), expire_time=True)
    assert expire is None
    store.close()


# --- cross-process (shared cache directory) -------------------------------


def _child_set(directory, key, value):
    s = DiskcacheSharedStorage(directory=directory)
    s.set(key, value)
    s.close()


def _child_publish(directory, topic, messages, start_ev):
    s = DiskcacheSharedStorage(directory=directory)
    start_ev.wait(timeout=10)
    for m in messages:
        s.publish(topic, m)
    s.close()


def test_kv_visible_across_processes(tmp_path):
    directory = str(tmp_path / "shared")
    store = DiskcacheSharedStorage(directory=directory)
    p = CTX.Process(target=_child_set, args=(directory, "shared", {"n": 42}))
    p.start()
    p.join(timeout=10)
    assert store.get("shared") == {"n": 42}
    store.close()


def test_pubsub_across_processes(tmp_path):
    directory = str(tmp_path / "shared")
    store = DiskcacheSharedStorage(directory=directory)
    sub = store.subscribe("topic")

    start_ev = CTX.Event()
    p = CTX.Process(
        target=_child_publish,
        args=(directory, "topic", ["m0", "m1", "m2"], start_ev),
    )
    p.start()

    received = []
    th = threading.Thread(target=lambda: received.extend(_drain(sub, 3)))
    th.start()
    time.sleep(0.3)  # ensure the subscriber is polling before publishing
    start_ev.set()

    th.join(timeout=10)
    p.join(timeout=10)
    sub.close()
    store.close()
    assert received == ["m0", "m1", "m2"]
