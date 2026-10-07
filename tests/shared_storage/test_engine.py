"""Unit tests for the in-memory StoreEngine (KV + sequenced pub/sub)."""
import threading
import time

from dash._shared_storage._engine import StoreEngine


def test_kv_get_set_delete():
    e = StoreEngine()
    assert e.get("missing") is None
    assert e.get("missing", 42) == 42
    e.set("a", {"x": 1})
    assert e.get("a") == {"x": 1}
    e.delete("a")
    assert e.get("a") is None
    e.delete("a")  # idempotent


def test_kv_ttl_expires_lazily(monkeypatch):
    from dash._shared_storage import _engine

    clock = {"t": 1000.0}
    monkeypatch.setattr(_engine.time, "monotonic", lambda: clock["t"])
    e = _engine.StoreEngine()
    e.set("a", "v", ttl=10)
    assert e.get("a") == "v"
    clock["t"] += 9  # 9s in, still alive
    assert e.get("a") == "v"
    clock["t"] += 2  # 11s in, past the ttl
    assert e.get("a", "gone") == "gone"
    assert "a" not in e._data  # expired entry is dropped, not just hidden


def test_kv_ttl_none_never_expires(monkeypatch):
    from dash._shared_storage import _engine

    clock = {"t": 0.0}
    monkeypatch.setattr(_engine.time, "monotonic", lambda: clock["t"])
    e = _engine.StoreEngine()
    e.set("a", "v")  # no ttl
    clock["t"] += 10_000
    assert e.get("a") == "v"


def test_kv_set_without_ttl_clears_prior_ttl(monkeypatch):
    from dash._shared_storage import _engine

    clock = {"t": 0.0}
    monkeypatch.setattr(_engine.time, "monotonic", lambda: clock["t"])
    e = _engine.StoreEngine()
    e.set("a", "v1", ttl=5)
    e.set("a", "v2")  # overwrite drops the expiry
    clock["t"] += 100
    assert e.get("a") == "v2"


def test_publish_assigns_monotonic_seq():
    e = StoreEngine()
    assert e.head_seq("t") == 0
    assert e.publish("t", "a") == 1
    assert e.publish("t", "b") == 2
    assert e.head_seq("t") == 2


def test_fresh_subscriber_only_sees_future_messages():
    e = StoreEngine()
    e.publish("t", "old")
    cursor = e.head_seq("t")  # subscribe "now"
    e.publish("t", "new1")
    e.publish("t", "new2")
    res = e.poll("t", cursor, timeout=1)
    assert res.messages == ["new1", "new2"]
    assert res.last_seq == 3  # "old" took seq 1, so new2 is seq 3
    assert res.gap is False


def test_replay_from_cursor_after_reconnect():
    e = StoreEngine()
    e.publish("t", "m1")
    e.publish("t", "m2")
    e.publish("t", "m3")
    # A consumer that saw up to seq 1 reconnects and replays 2 and 3.
    res = e.poll("t", 1, timeout=1)
    assert res.messages == ["m2", "m3"]
    assert res.last_seq == 3
    assert res.gap is False


def test_gap_when_buffer_overruns():
    e = StoreEngine(buffer_size=2)
    for i in range(5):
        e.publish("t", f"m{i}")  # seqs 1..5, buffer holds only seqs 4,5
    # A consumer stuck at seq 1 wanted seq 2, which was evicted -> gap.
    res = e.poll("t", 1, timeout=1)
    assert res.gap is True
    assert res.messages == []


def test_no_gap_at_buffer_edge():
    e = StoreEngine(buffer_size=2)
    for i in range(4):
        e.publish("t", f"m{i}")  # seqs 1..4, buffer holds 3,4
    # Consumer at seq 2 wants seq 3, which is still buffered -> no gap.
    res = e.poll("t", 2, timeout=1)
    assert res.gap is False
    assert res.messages == ["m2", "m3"]


def test_poll_times_out_empty_when_no_messages():
    e = StoreEngine()
    start = time.monotonic()
    res = e.poll("t", 0, timeout=0.2)
    assert res.messages == []
    assert res.gap is False
    assert time.monotonic() - start >= 0.2


def test_poll_wakes_on_publish_from_another_thread():
    e = StoreEngine()
    received = []

    def consumer():
        res = e.poll("t", 0, timeout=2)
        received.extend(res.messages)

    th = threading.Thread(target=consumer)
    th.start()
    time.sleep(0.1)  # ensure the poll is waiting
    e.publish("t", "live")
    th.join(timeout=2)
    assert received == ["live"]


def test_close_unblocks_waiting_pollers():
    e = StoreEngine()
    done = threading.Event()

    def consumer():
        e.poll("t", 0, timeout=10)
        done.set()

    th = threading.Thread(target=consumer)
    th.start()
    time.sleep(0.1)
    e.close()
    assert done.wait(timeout=2)


def test_multiple_subscribers_each_get_every_message():
    e = StoreEngine()
    cursor = e.head_seq("t")
    e.publish("t", "a")
    e.publish("t", "b")
    a = e.poll("t", cursor, timeout=1)
    b = e.poll("t", cursor, timeout=1)
    assert a.messages == ["a", "b"]
    assert b.messages == ["a", "b"]  # independent cursors, both see all


def test_apoll_wakes_on_publish_from_another_thread():
    import asyncio

    e = StoreEngine()

    async def scenario():
        loop = asyncio.get_running_loop()
        threading.Timer(0.1, lambda: e.publish("t", "hello")).start()
        started = loop.time()
        res = await e.apoll("t", 0, timeout=5.0)
        assert res.messages == ["hello"] and res.last_seq == 1 and not res.gap
        assert loop.time() - started < 2.0  # woken, not timed out
        # Nothing new: times out empty without blocking a thread.
        res = await e.apoll("t", 1, timeout=0.05)
        assert res.messages == [] and res.last_seq == 1
        # A waiter that timed out was removed from the topic.
        assert e._topics["t"].waiters == []

    asyncio.run(scenario())


def test_apoll_wakes_on_close_and_serves_many_waiters():
    import asyncio

    e = StoreEngine()

    async def scenario():
        waits = [asyncio.ensure_future(e.apoll(f"t{i}", 0, 5.0)) for i in range(200)]
        await asyncio.sleep(0.05)
        assert sum(len(e._topics[f"t{i}"].waiters) for i in range(200)) == 200
        threading.Timer(0.05, e.close).start()
        results = await asyncio.wait_for(asyncio.gather(*waits), 5.0)
        assert all(r.messages == [] for r in results)

    asyncio.run(scenario())


def _clocked_engine(monkeypatch):
    from dash._shared_storage import _engine

    clock = {"t": 1000.0}
    monkeypatch.setattr(_engine.time, "monotonic", lambda: clock["t"])
    return _engine.StoreEngine(), clock


def test_idle_topic_is_released(monkeypatch):
    e, clock = _clocked_engine(monkeypatch)
    for i in range(5):
        e.publish("gone", i, ttl=10)
    e.publish("kept", "x")
    clock["t"] += 12  # past the ttl and a sweep interval
    e.publish("other", "x")  # any pub/sub call sweeps
    assert sorted(e._topics) == ["kept", "other"]
    # A later publish starts the topic over.
    assert e.publish("gone", "again") == 1


def test_polling_keeps_a_topic_alive(monkeypatch):
    e, clock = _clocked_engine(monkeypatch)
    e.publish("t", "m", ttl=10)
    for _ in range(5):
        clock["t"] += 6  # each gap is under the ttl, the total is well past it
        e.poll("t", 1, timeout=0)
    e.publish("other", "x")
    assert e.head_seq("t") == 1


def test_topic_held_by_a_blocked_poll_is_not_released(monkeypatch):
    e, clock = _clocked_engine(monkeypatch)
    e.publish("t", "m1", ttl=10)
    t = e._topics["t"]
    got = []
    poller = threading.Thread(target=lambda: got.append(e.poll("t", 1, timeout=100)))
    poller.start()
    until_parked = time.time() + 2
    while t.users == 0 and time.time() < until_parked:
        time.sleep(0.01)
    clock["t"] += 60
    e.publish("other", "x")
    assert e._topics["t"] is t
    e.publish("t", "m2")  # still reaches the parked poll
    poller.join(timeout=2)
    assert got[0].messages == ["m2"]


def test_latest_publish_sets_the_ttl(monkeypatch):
    e, clock = _clocked_engine(monkeypatch)
    e.publish("t", "m", ttl=10)
    e.publish("t", "m")
    clock["t"] += 10_000
    e.publish("other", "x")
    assert e.head_seq("t") == 2


def test_released_topic_gaps_a_stale_cursor(monkeypatch):
    # A consumer that comes back after its topic was released gets the gap
    # signal, not a silent restart.
    e, clock = _clocked_engine(monkeypatch)
    for i in range(3):
        e.publish("t", i, ttl=10)
    clock["t"] += 12
    e.publish("t", "fresh")
    assert e.poll("t", 3, timeout=0).gap is True
