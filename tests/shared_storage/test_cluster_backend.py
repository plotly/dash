"""ClusterSharedStorage across "pods" on loopback.

Each pod is a ClusterSharedStorage on its own port pair (lock port, data port);
a second instance on the same port plays another worker of that pod, which
finds the owner through the pod's lock process. ``peers`` stands in for DNS.
"""
# pylint: disable=protected-access
import asyncio
import socket
import threading
import time

import pytest

from dash._shared_storage import (
    ClusterSharedStorage,
    SharedStorageError,
    SharedStorageGap,
)

FAST = {"probe_interval": 0.05, "settle_timeout": 10.0}


def until(predicate, timeout=10.0, message="condition not met"):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError(message)


def _port_pair():
    """A port whose next one up is free too."""
    for _ in range(50):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        if port >= 65534:
            continue
        try:
            with socket.create_server(("", port)), socket.create_server(("", port + 1)):
                return port
        except OSError:
            continue
    raise RuntimeError("no free port pair")


class Pods:
    def __init__(self):
        self.ports = []
        self.views = {}
        self.stores = []
        self._mutex = threading.Lock()

    def add_pod(self):
        self.ports.append(_port_pair())
        return len(self.ports) - 1

    def worker(self, pod, secret="s3cret", **kw):
        def peers():
            with self._mutex:
                allowed = self.views.get(pod)
                ports = list(enumerate(self.ports))
            return [
                ("127.0.0.1", p) for i, p in ports if allowed is None or i in allowed
            ]

        store = ClusterSharedStorage(
            port=self.ports[pod], secret=secret, peers=peers, **{**FAST, **kw}
        )
        self.stores.append(store)
        return store

    def isolate(self, *groups):
        with self._mutex:
            for group in groups:
                for pod in group:
                    self.views[pod] = set(group)

    def join(self):
        with self._mutex:
            self.views.clear()

    def close(self):
        for store in self.stores:
            store.close()


@pytest.fixture
def pods():
    p = Pods()
    yield p
    p.close()


def _owner_of(store):
    store.start()
    return store._coord._cluster


def test_pods_share_kv_and_pubsub(pods):
    a, b = pods.add_pod(), pods.add_pod()
    a1 = pods.worker(a)
    a1.start()
    b1 = pods.worker(b)
    a2 = pods.worker(a)  # another worker of pod a: no lock of its own
    for store in (a1, b1, a2):
        store.start()
    assert a2._coord._cluster is None
    assert a1._coord.is_owner()
    assert not b1._coord.is_owner() and not a2._coord.is_owner()

    b1.set("k", {"from": "b"})
    assert a1.get("k") == {"from": "b"}
    assert a2.get("k") == {"from": "b"}

    sub = a2.subscribe("t")
    b1.publish("t", 1)
    a1.publish("t", 2)
    assert sub.poll(timeout=5) == [(1, 1), (2, 2)]


def test_owner_loss_gaps_readers_and_a_survivor_takes_over(pods):
    a, b = pods.add_pod(), pods.add_pod()
    owner = pods.worker(a)
    owner.start()
    other = pods.worker(b)
    other.start()
    other.set("k", 1)
    sub = other.subscribe("t")
    owner.publish("t", "before")
    assert sub.poll(timeout=5) == [(1, "before")]

    owner.close()
    with pytest.raises(SharedStorageGap):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            sub.poll(timeout=0.2)
    assert other._coord.is_owner()
    assert other.get("k") is None  # memory mode: the new owner starts empty
    other.set("k", 2)
    assert other.get("k") == 2


def test_blocked_reader_on_a_dead_owner_gaps(pods):
    a, b = pods.add_pod(), pods.add_pod()
    owner = pods.worker(a)
    owner.start()
    reader = pods.worker(b)
    reader.start()
    sub = reader.subscribe("t")
    errors = []

    def read():
        try:
            for _msg in sub:
                pass
        except SharedStorageGap as err:
            errors.append(err)

    thread = threading.Thread(target=read, daemon=True)
    thread.start()
    time.sleep(0.3)
    owner.close()
    thread.join(15)
    assert not thread.is_alive() and errors


def test_split_owners_merge_and_the_loser_stops_taking_writes(pods):
    a, b = pods.add_pod(), pods.add_pod()
    pods.isolate([a], [b])
    first = pods.worker(a)
    first.start()
    time.sleep(0.2)
    second = pods.worker(b)
    second.start()
    assert first._coord.is_owner() and second._coord.is_owner()
    first.set("k", "first")
    second.set("k", "second")
    sub = second.subscribe("t")

    pods.join()
    until(lambda: not second._coord._cluster.is_owner(second._coord._term))
    # The writes go to the owner that held on, never the deposed one's engine.
    second.set("after", 1)
    assert first.get("after") == 1
    assert second.get("k") == "first"
    with pytest.raises(SharedStorageGap):
        sub.poll()


def test_worker_follows_the_owner_change_through_its_pods_lock(pods):
    a, b = pods.add_pod(), pods.add_pod()
    owner = pods.worker(a)
    owner.start()
    holder = pods.worker(b)
    holder.start()
    worker = pods.worker(b)
    worker.start()
    worker.set("k", 1)
    assert owner.get("k") == 1

    owner.close()
    until(lambda: holder._coord._cluster.state.role == "owner")
    deadline = time.monotonic() + 10
    while True:
        try:
            worker.set("k", 2)
            break
        except SharedStorageError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.1)
    assert holder.get("k") == 2


def test_wrong_secret_never_joins(pods):
    a, b = pods.add_pod(), pods.add_pod()
    good = pods.worker(a)
    good.start()
    rogue = pods.worker(b, secret="other")
    rogue.start()
    good.set("k", "good")
    rogue.set("k", "rogue")
    assert good.get("k") == "good"
    assert good._coord.is_owner() and rogue._coord.is_owner()


def test_data_port_rejects_a_wrong_token(pods):
    from dash._shared_storage._transport import connect_to_owner

    a = pods.add_pod()
    store = pods.worker(a)
    store.start()
    with pytest.raises((ConnectionError, OSError)):
        connect_to_owner(socket.AF_INET, ("127.0.0.1", pods.ports[a] + 1), "guess")


def test_async_paths(pods):
    a, b = pods.add_pod(), pods.add_pod()
    owner = pods.worker(a)
    owner.start()
    client = pods.worker(b)
    client.start()

    async def run():
        await client.aset("k", [1, 2])
        assert await client.aget("k") == [1, 2]
        sub = client.subscribe("t")
        await client.apublish("t", "x")
        owner.publish("t", "y")
        got = []
        async for pair in sub.aiter_with_seq():
            got.append(pair)
            if len(got) == 2:
                break
        return got

    assert asyncio.run(run()) == [(1, "x"), (2, "y")]


def test_no_owner_in_time_raises(pods):
    a = pods.add_pod()
    # Another process holds the lock port but never answers as a lock.
    squatter = socket.create_server(("", pods.ports[a]))
    try:
        store = pods.worker(a, settle_timeout=0.5)
        with pytest.raises(SharedStorageError, match="no shared-storage cluster owner"):
            store.start()
    finally:
        squatter.close()


def test_needs_a_secret(monkeypatch):
    monkeypatch.delenv("DASH_SECRET_KEY", raising=False)
    with pytest.raises(SharedStorageError, match="secret"):
        ClusterSharedStorage(host="peers")
    monkeypatch.setenv("DASH_SECRET_KEY", "x")
    ClusterSharedStorage(host="peers").close()


def test_readers_never_get_a_new_owners_data_with_an_old_cursor(pods):
    a, b, c = pods.add_pod(), pods.add_pod(), pods.add_pod()
    owner = pods.worker(a)
    owner.start()
    readers = [pods.worker(b), pods.worker(c)]
    for store in readers:
        store.start()
    owner.publish("t", "before")
    events = {0: [], 1: []}

    def read(idx, store):
        sub = store.subscribe("t", replay_from=0)
        try:
            for seq, msg in sub.iter_with_seq():
                events[idx].append(("data", seq, msg))
        except SharedStorageGap:
            events[idx].append(("gap",))
        except SharedStorageError as err:
            events[idx].append(("error", str(err)))

    threads = [
        threading.Thread(target=read, args=(i, s), daemon=True)
        for i, s in enumerate(readers)
    ]
    for thread in threads:
        thread.start()
    until(lambda: all(events[i] for i in events), message="readers saw nothing")
    owner.close()

    # Publish on the survivors until the new owner takes it: its topic starts
    # over, so an old cursor reading it would see these as fresh data.
    deadline = time.monotonic() + 15
    published = 0
    while published < 3 and time.monotonic() < deadline:
        try:
            readers[0].publish("t", f"after-{published}")
            published += 1
        except SharedStorageError:
            time.sleep(0.1)
    assert published == 3
    for thread in threads:
        thread.join(15)
    for idx in events:
        assert events[idx][0] == ("data", 1, "before")
        assert events[idx][1:] == [("gap",)], events[idx]


def test_async_connect_times_out_on_a_silent_owner():
    from dash._shared_storage._transport import aconnect_to_owner

    silent = socket.create_server(("127.0.0.1", 0))
    try:

        async def run():
            started = time.monotonic()
            with pytest.raises(asyncio.TimeoutError):
                await aconnect_to_owner(
                    socket.AF_INET, silent.getsockname(), "token", timeout=0.5
                )
            return time.monotonic() - started

        assert asyncio.run(run()) < 2
    finally:
        silent.close()


def test_long_client_poll_returns_within_a_cycle(pods):
    a, b = pods.add_pod(), pods.add_pod()
    pods.worker(a).start()
    client = pods.worker(b)
    client.start()
    client._coord.client_poll_timeout = 0.5
    sub = client.subscribe("t")
    started = time.monotonic()
    assert sub.poll(timeout=60) == []
    assert time.monotonic() - started < 3


def test_deposed_persistent_owner_does_not_overwrite_the_store(pods, tmp_path):
    from dash._shared_storage import LocalSharedStorage

    path = str(tmp_path / "shared")
    a, b = pods.add_pod(), pods.add_pod()
    pods.isolate([a], [b])
    first = pods.worker(a, mode="persist-reset", path=path, flush_interval=3600)
    first.start()
    time.sleep(0.2)
    second = pods.worker(b, mode="persist-reset", path=path, flush_interval=3600)
    second.start()
    assert first._coord.is_owner() and second._coord.is_owner()
    second.set("k", "second")
    first.set("k", "first")
    first._coord.engine._persistence._flush(["k"])

    pods.join()
    until(lambda: not second._coord._cluster.is_owner(second._coord._term))
    until(lambda: second._coord.engine is None or second._coord._role != "owner")
    reader = LocalSharedStorage(namespace="deposed-check", mode="persist", path=path)
    try:
        assert reader.get("k") == "first"
    finally:
        reader.close()


def test_bind_errors_other_than_in_use_are_reported(pods, monkeypatch):
    import errno

    from dash._shared_storage import cluster

    def refuse(*_args, **_kwargs):
        raise OSError(errno.EACCES, "permission denied")

    monkeypatch.setattr(cluster, "ClusterLock", refuse)
    store = pods.worker(pods.add_pod())
    with pytest.raises(SharedStorageError, match="cannot listen on the cluster port"):
        store.start()


def test_tls_pods_share_kv_and_pubsub_encrypted(pods, make_cert):
    import ssl

    cert, key = make_cert()
    a, b = pods.add_pod(), pods.add_pod()
    tls = {"tls_cert": cert, "tls_key": key}
    owner = pods.worker(a, **tls)
    owner.start()
    other = pods.worker(b, **tls)
    worker = pods.worker(a, **tls)  # finds the owner through its pod's lock
    other.start()
    worker.start()

    other.set("k", "v")
    assert owner.get("k") == "v" and worker.get("k") == "v"
    assert isinstance(other._conn, ssl.SSLSocket)
    sub = worker.subscribe("t")
    other.publish("t", 1)
    assert sub.poll(timeout=5) == [(1, 1)]

    async def run():
        await other.aset("a", 2)
        return await worker.aget("a")

    assert asyncio.run(run()) == 2


def test_tls_data_port_refuses_plaintext(pods, make_cert):
    from dash._shared_storage._transport import connect_to_owner

    cert, key = make_cert()
    a = pods.add_pod()
    store = pods.worker(a, tls_cert=cert, tls_key=key)
    store.start()
    token = store._coord.token
    data = ("127.0.0.1", pods.ports[a] + 1)
    socket.create_connection(data, timeout=2).close()  # it is listening
    # The server drops a client that does not open with a TLS handshake: a
    # reset or a closed connection, never an answer.
    with pytest.raises(ConnectionError) as err:
        connect_to_owner(socket.AF_INET, data, token)
    assert not isinstance(err.value, ConnectionRefusedError)
    assert isinstance(err.value, ConnectionResetError) or "rejected" in str(err.value)


def test_tls_needs_cert_and_key(make_cert):
    cert, _key = make_cert()
    with pytest.raises(SharedStorageError, match="both tls_cert and tls_key"):
        ClusterSharedStorage(host="peers", secret="s", tls_cert=cert)
    with pytest.raises(SharedStorageError, match="cannot load the cluster TLS"):
        ClusterSharedStorage(
            host="peers", secret="s", tls_cert=cert, tls_key="/does/not/exist"
        )


def test_tls_with_a_ca_and_a_certificate_per_pod(pods, make_cert):
    ca = make_cert("cluster-ca")
    a, b = pods.add_pod(), pods.add_pod()
    stores = []
    for pod in (a, b):
        cert, key = make_cert(f"pod-{pod}", signed_by=ca)
        stores.append(pods.worker(pod, tls_cert=cert, tls_key=key, tls_ca=ca[0]))
    for store in stores:
        store.start()
    stores[1].set("k", "signed")
    assert stores[0].get("k") == "signed"

    # Signed by another CA: it never joins.
    stranger_ca = make_cert("stranger-ca")
    cert, key = make_cert("stranger", signed_by=stranger_ca)
    c = pods.add_pod()
    stranger = pods.worker(c, tls_cert=cert, tls_key=key, tls_ca=stranger_ca[0])
    stranger.start()
    stranger.set("k", "stranger")
    assert stores[0].get("k") == "signed"


def test_tls_server_only_certificate_is_refused_and_logged(pods, make_cert, caplog):
    from dash._shared_storage import _cluster_lock

    cert, key = make_cert(
        "server-only", extra=("-addext", "extendedKeyUsage=serverAuth")
    )
    _cluster_lock._tls_failed.clear()
    a, b = pods.add_pod(), pods.add_pod()
    first = pods.worker(a, tls_cert=cert, tls_key=key)
    first.start()
    second = pods.worker(b, tls_cert=cert, tls_key=key)
    second.start()
    assert first._coord.is_owner() and second._coord.is_owner()
    assert any("TLS handshake" in r.getMessage() for r in caplog.records)


def test_tls_options_fail_loudly(make_cert):
    cert, key = make_cert()
    with pytest.raises(SharedStorageError, match="both tls_cert and tls_key"):
        ClusterSharedStorage(host="peers", secret="s", tls_cert="", tls_key="")
    locked, locked_key = make_cert("locked", extra=("-passout", "pass:pw"))
    started = time.monotonic()
    with pytest.raises(SharedStorageError, match="cannot load the cluster TLS"):
        ClusterSharedStorage(
            host="peers", secret="s", tls_cert=locked, tls_key=locked_key
        )
    assert time.monotonic() - started < 5
    ClusterSharedStorage(host="peers", secret="s", tls_cert=cert, tls_key=key).close()
