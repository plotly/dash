"""Cross-process tests for LocalSharedStorage.

An owner runs in a spawned child process; the pytest process attaches as a
client (the child wins election first). Exercises KV visibility, pub/sub, and
client reconnect-with-replay across a forced socket drop -- all over the real
socket transport, not the in-process fast path.
"""
import multiprocessing as mp
import threading
import time
import uuid

import pytest

from dash._shared_storage import LocalSharedStorage

CTX = mp.get_context("spawn")


def _owner_main(namespace, cmd_q, done_q, ready_ev):
    """A controllable owner: wins election, then runs commands on demand."""
    store = LocalSharedStorage(namespace=namespace)
    store.start()
    if not store._coord.is_owner():  # pragma: no cover - defensive
        done_q.put(("error", "child did not win election"))
        return
    ready_ev.set()
    while True:
        cmd = cmd_q.get()
        if cmd is None:
            break
        op, args = cmd
        if op == "set":
            store.set(*args)
        elif op == "publish":
            store.publish(*args)
        done_q.put(("done", op))
    store.close()


class _Owner:
    """Test helper: spawn a controllable owner and drive it synchronously."""

    def __init__(self, namespace):
        self.cmd_q = CTX.Queue()
        self.done_q = CTX.Queue()
        self.ready = CTX.Event()
        self.proc = CTX.Process(
            target=_owner_main,
            args=(namespace, self.cmd_q, self.done_q, self.ready),
            daemon=True,
        )

    def start(self):
        self.proc.start()
        assert self.ready.wait(timeout=10), "owner failed to start"

    def do(self, op, *args):
        self.cmd_q.put((op, args))
        kind, _ = self.done_q.get(timeout=10)
        assert kind == "done"

    def stop(self):
        self.cmd_q.put(None)
        self.proc.join(timeout=10)


@pytest.fixture
def owner():
    ns = f"xproc-{uuid.uuid4().hex[:12]}"
    o = _Owner(ns)
    o.start()
    try:
        yield ns, o
    finally:
        o.stop()


def test_kv_visible_across_processes(owner):
    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()
    assert not client._coord.is_owner()  # child owns; we are the client

    o.do("set", "shared", {"n": 42})
    assert client.get("shared") == {"n": 42}
    assert client.get("nope", "fallback") == "fallback"
    client.close()


def test_pubsub_across_processes(owner):
    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()

    sub = client.subscribe("topic")  # cursor at current head
    received = []

    def consume():
        for msg in sub:
            received.append(msg)
            if len(received) == 3:
                break

    th = threading.Thread(target=consume)
    th.start()
    time.sleep(0.3)  # ensure the long-poll is established

    for i in range(3):
        o.do("publish", "topic", f"m{i}")

    th.join(timeout=10)
    sub.close()
    client.close()
    assert received == ["m0", "m1", "m2"]


def test_client_reconnect_replays_missed_messages(owner):
    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()

    sub = client.subscribe("stream")
    received = []
    ready = threading.Event()

    def consume():
        ready.set()
        for msg in sub:
            received.append(msg)
            if len(received) == 6:
                break

    th = threading.Thread(target=consume)
    th.start()
    ready.wait()
    time.sleep(0.3)

    o.do("publish", "stream", "a")
    o.do("publish", "stream", "b")

    # Wait until the first two land, then forcibly drop the client's socket.
    _wait_until(lambda: len(received) >= 2, timeout=5)
    conn = sub._conn
    if conn is not None:
        conn.close()  # simulate a proxy idle-timeout / network blip

    # Messages published during/after the drop must still arrive (buffer replay).
    for msg in ("c", "d", "e", "f"):
        o.do("publish", "stream", msg)

    th.join(timeout=10)
    sub.close()
    client.close()
    assert received == ["a", "b", "c", "d", "e", "f"]


def test_reelection_after_owner_killed(owner):
    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()
    assert not client._coord.is_owner()

    o.do("set", "before", "value")
    assert client.get("before") == "value"

    # Kill the owner without a clean shutdown (leaves a stale socket).
    o.proc.terminate()
    o.proc.join(timeout=10)

    # The survivor re-elects: it becomes the new (cold) owner and keeps serving.
    assert client.get("before") is None  # cold store, prior state gone
    client.set("after", "fresh")
    assert client.get("after") == "fresh"
    assert client._coord.is_owner()  # we are the new owner
    client.close()


def test_patch_frame_published_over_socket(owner):
    # Reproduces the multi-process failure: a client publishes a streaming frame
    # carrying a dash.Patch to the owner over the socket. The frame must arrive
    # reduced to plain JSON (the wire codec can't encode a Patch).
    from dash import Patch
    from dash._stream_hub import publish_frame, subscribe_envelopes

    ns, _ = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()
    assert not client._coord.is_owner()  # publishing over the socket

    out = []

    def drain():
        gen = subscribe_envelopes(client, "cp", replay_from=0)
        for env in gen:
            out.append(env)
            if env["frame"].get("done"):
                break
        gen.close()

    th = threading.Thread(target=drain, daemon=True)
    th.start()
    time.sleep(0.4)

    patch = Patch()
    patch["a"] = 1
    publish_frame(client, "cp", "r1", {"response": {"o": {"children": patch}}})
    publish_frame(client, "cp", "r1", {"done": True})

    th.join(timeout=8)
    assert (
        out[0]["frame"]["response"]["o"]["children"]["__dash_patch_update"]
        == "__dash_patch_update"
    )
    assert out[-1]["frame"] == {"done": True}
    client.close()


def _wait_until(pred, timeout):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return
        time.sleep(0.02)
    raise AssertionError("condition not met in time")
