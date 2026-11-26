"""Cross-process tests for LocalSharedStorage.

An owner runs in a spawned child process; the pytest process attaches as a
client (the child wins election first). Exercises KV visibility, pub/sub, and
client reconnect-with-replay across a forced socket drop -- all over the real
socket transport, not the in-process fast path.
"""
import multiprocessing as mp
import os
import signal
import json
import socket
import subprocess
import sys
import threading
import time
import uuid

import pytest

from dash._shared_storage import LocalSharedStorage

CTX = mp.get_context("spawn")


def _owner_main(namespace, cmd_q, done_q, ready_ev, mode="memory", path=None):
    """A controllable owner: wins election, then runs commands on demand."""
    store = LocalSharedStorage(namespace=namespace, mode=mode, path=path)
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

    def __init__(self, namespace, mode="memory", path=None):
        self.cmd_q = CTX.Queue()
        self.done_q = CTX.Queue()
        self.ready = CTX.Event()
        self.proc = CTX.Process(
            target=_owner_main,
            args=(namespace, self.cmd_q, self.done_q, self.ready, mode, path),
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


@pytest.mark.skipif(
    not hasattr(socket, "AF_UNIX") or not hasattr(signal, "SIGSTOP"),
    reason="needs unix sockets and SIGSTOP",
)
def test_busy_owner_is_not_replaced(owner):
    """An owner too busy to accept (its backlog full) is alive. A client that
    re-elects must not take its socket over and start a second, empty store."""
    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()
    o.do("set", "before", "value")
    assert client.get("before") == "value"

    os.kill(o.proc.pid, signal.SIGSTOP)
    held = []
    try:
        for _ in range(200):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.setblocking(False)
            try:
                sock.connect(client._coord._sock_path)
            except OSError:
                pass
            held.append(sock)
        client._coord.on_owner_lost()
        assert not client._coord.is_owner()
    finally:
        os.kill(o.proc.pid, signal.SIGCONT)
        for sock in held:
            sock.close()

    assert client.get("before") == "value"
    client.close()


@pytest.mark.skipif(not hasattr(socket, "AF_UNIX"), reason="needs unix sockets")
def test_stale_socket_probe(tmp_path, monkeypatch):
    from dash._shared_storage import local

    sock_path = str(tmp_path / "s.sock")
    addr_path = str(tmp_path / "s.addr")
    assert local._unix_is_stale(sock_path, addr_path)  # no file

    leftover = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    leftover.bind(sock_path)
    leftover.close()  # the file stays, nobody listens
    assert local._unix_is_stale(sock_path, addr_path)

    stray = tmp_path / "stray"
    stray.write_text("not a socket")
    assert local._unix_is_stale(str(stray), addr_path)

    # macOS and the BSDs also refuse when the backlog is full: there a refused
    # probe means stale only once the advertised owner process is gone.
    monkeypatch.setattr(local.sys, "platform", "darwin")
    assert local._unix_is_stale(sock_path, addr_path)  # no advertisement
    with open(addr_path, "w", encoding="utf-8") as f:
        json.dump({"pid": os.getpid()}, f)
    assert not local._unix_is_stale(sock_path, addr_path)
    gone = subprocess.Popen([sys.executable, "-c", ""])
    gone.wait()
    with open(addr_path, "w", encoding="utf-8") as f:
        json.dump({"pid": gone.pid}, f)
    assert local._unix_is_stale(sock_path, addr_path)


@pytest.mark.skipif(not hasattr(socket, "AF_UNIX"), reason="needs unix sockets")
def test_starting_owner_is_not_stale(tmp_path):
    """An owner that has bound its socket but is still recovering its data
    before serving is alive, so a re-election must not take its socket over."""
    from dash._shared_storage import local

    sock_path = str(tmp_path / "s.sock")
    addr_path = str(tmp_path / "s.addr")
    listen_sock, _, _ = local._try_bind("unused", sock_path, addr_path)
    try:
        assert not local._unix_is_stale(sock_path, addr_path)
        assert local._try_bind("unused", sock_path, addr_path) is None
    finally:
        listen_sock.close()


@pytest.mark.skipif(not hasattr(socket, "AF_UNIX"), reason="needs unix sockets")
def test_failed_election_releases_the_socket(tmp_path, monkeypatch):
    """An election that fails after binding (here, recovering persisted data)
    must not leave a listening socket that would pass for a live owner."""
    from dash._shared_storage import local

    pytest.importorskip("msgspec")
    real_recover = local._Persistence.recover

    def broken(self):
        raise OSError("disk unreadable")

    monkeypatch.setattr(local._Persistence, "recover", broken)
    store = LocalSharedStorage(
        namespace=f"t-{uuid.uuid4().hex[:8]}",
        mode="persist",
        path=str(tmp_path / "store"),
    )
    # Keep the traceback alive, as a logged or stored error would: its frames
    # must not be what holds the socket open.
    with pytest.raises(OSError, match="disk unreadable") as failure:
        store.start()
    assert failure.traceback
    assert local._unix_is_stale(store._coord._sock_path, store._coord._addr_path)

    monkeypatch.setattr(local._Persistence, "recover", real_recover)
    store._coord.ensure()
    assert store._coord.is_owner()
    store.set("k", "v")
    assert store.get("k") == "v"
    store.close()


def test_reelection_recovers_persisted_data(tmp_path):
    """With mode='persist', a re-elected owner recovers the killed owner's data
    from disk instead of coming up cold."""
    ns = f"xproc-{uuid.uuid4().hex[:12]}"
    path = str(tmp_path / "store")
    o = _Owner(ns, mode="persist", path=path)
    o.start()
    try:
        client = LocalSharedStorage(namespace=ns, mode="persist", path=path)
        client.start()
        assert not client._coord.is_owner()

        o.do("set", "durable", {"n": 7})
        assert client.get("durable") == {"n": 7}

        # Kill the owner without a clean shutdown; write-through already flushed.
        o.proc.terminate()
        o.proc.join(timeout=10)

        # The survivor re-elects and recovers the persisted value from disk.
        assert client.get("durable") == {"n": 7}
        assert client._coord.is_owner()
        client.close()
    finally:
        o.stop()


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


def test_async_client_subscription_across_processes(owner):
    """The asyncio subscription path (ASGI servers) long-polls the owner over an
    asyncio-streams connection -- no executor thread -- and resumes after a
    reconnect from its cursor."""
    import asyncio

    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()
    assert not client._coord.is_owner()
    sub = client.subscribe("atopic")

    async def consume():
        got = []
        async for msg in sub:
            got.append(msg)
            if len(got) == 3:
                break
        return got

    async def scenario():
        task = asyncio.ensure_future(consume())
        await asyncio.sleep(0.3)  # the long-poll is established
        for i in range(3):
            o.do("publish", "atopic", f"a{i}")
        return await asyncio.wait_for(task, 10)

    assert asyncio.run(scenario()) == ["a0", "a1", "a2"]
    sub.close()
    client.close()


def test_async_ops_across_processes(owner):
    """aget/aset/apublish from a client worker's event loop go over an
    asyncio-streams connection of their own: no executor, no blocking."""
    import asyncio

    ns, o = owner
    client = LocalSharedStorage(namespace=ns)
    client.start()

    async def scenario():
        await client.aset("k", {"v": 1})
        assert await client.aget("k") == {"v": 1}
        assert await client.aget("missing", "dflt") == "dflt"
        sub = client.subscribe("apub", replay_from=0)
        await client.apublish("apub", "m1")
        await client.apublish("apub", "m2")
        assert sub.poll(0.0) == [(1, "m1"), (2, "m2")]
        sub.close()
        await client.adelete("k")
        assert await client.aget("k") is None
        # Many concurrent calls share the one connection safely.
        await asyncio.gather(*(client.aset(f"k{i}", i) for i in range(50)))
        assert await client.aget("k49") == 49

    asyncio.run(scenario())
    assert client.get("k7") == 7  # landed in the owner, visible over the sync path
    client.close()
