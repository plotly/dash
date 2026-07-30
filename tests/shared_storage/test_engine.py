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
