"""ClusterLock: owner election among replicas over loopback TCP.

Each test hands its locks a fake DNS (a function returning peer addresses), so
partial and changing views are easy to set up.
"""
import json
import os
import secrets
import signal
import socket
import struct
import subprocess
import sys
import textwrap
import threading
import time

import pytest

from dash._shared_storage._cluster_lock import (
    ELECTING,
    FOLLOWER,
    OWNER,
    ClusterLock,
    _mac,
    _recv,
    _send,
    probe,
    resolve_peers,
)

SECRET = b"test-secret"
FAST = {"probe_interval": 0.05, "probe_timeout": 0.5, "miss_limit": 2}


def until(predicate, timeout=10.0, message="condition not met"):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError(message)


class Cluster:
    """Locks on loopback that see each other through ``views``: per lock, the
    indexes of the locks it can resolve (all of them by default)."""

    def __init__(self):
        self.locks = []
        self.views = {}
        self.changes = {}
        self._mutex = threading.Lock()

    def add(self, secret=SECRET, start=True, peers=None, **kw):
        idx = len(self.locks)
        changes = self.changes[idx] = []
        kw.setdefault("on_change", changes.append)
        lock = ClusterLock(
            peers=peers or (lambda: self._peers(idx)),
            secret=secret,
            bind=("127.0.0.1", 0),
            advert={"data_port": 1000 + idx},
            **{**FAST, **kw},
        )
        self.locks.append(lock)
        if start:
            lock.start()
        return lock

    def _peers(self, idx):
        with self._mutex:
            allowed = self.views.get(idx)
            ports = [lock.port for lock in self.locks]
        if allowed is not None:
            ports = [p for i, p in enumerate(ports) if i in allowed]
        return [("127.0.0.1", p) for p in ports]

    def see(self, idx, others):
        with self._mutex:
            self.views[idx] = set(others) | {idx}

    def see_all(self):
        with self._mutex:
            self.views.clear()

    def live(self):
        return [lock for lock in self.locks if not lock._closed.is_set()]

    def owners(self, locks=None):
        return [lock for lock in (locks or self.live()) if lock.state.role == OWNER]

    def settled(self, locks=None):
        """One owner, and everyone else following it under its term."""
        locks = locks or self.live()
        owners = self.owners(locks)
        if len(owners) != 1:
            return None
        owner = owners[0]
        for lock in locks:
            if lock is owner:
                continue
            state = lock.state
            if state.role != FOLLOWER or state.owner_id != owner.id:
                return None
            if state.term != owner.state.term:
                return None
        return owner

    def wait_settled(self, timeout=10.0, locks=None):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            owner = self.settled(locks)
            if owner is not None:
                return owner
            time.sleep(0.02)
        roles = [
            (lock.id, lock.state.role, lock.state.owner_id) for lock in self.live()
        ]
        raise AssertionError(f"cluster did not settle: {roles}")

    def close(self):
        for lock in self.locks:
            lock.close()


@pytest.fixture
def cluster():
    c = Cluster()
    yield c
    c.close()


def test_single_replica_owns(cluster):
    lock = cluster.add()
    state = lock.wait_settled(5)
    assert state.role == OWNER and state.term
    assert lock.is_owner(state.term)
    assert not lock.is_owner("other")
    assert not lock.is_owner(None)


def test_replicas_booting_together_settle_on_one_owner(cluster):
    for _ in range(6):
        cluster.add(start=False)
    for lock in cluster.locks:
        lock.start()
    owner = cluster.wait_settled()
    follower = next(lock for lock in cluster.locks if lock is not owner)
    assert follower.state.owner_addr == ("127.0.0.1", owner.port)
    idx = cluster.locks.index(owner)
    assert follower.state.advert == {"data_port": 1000 + idx}


def test_late_joiner_follows_and_never_deposes(cluster):
    first = cluster.add()
    assert first.wait_settled(5).role == OWNER
    cluster.add()
    owner = cluster.wait_settled()
    assert owner is first
    term = owner.state.term
    late = cluster.add()
    cluster.wait_settled()
    assert late.state.role == FOLLOWER
    assert owner.state == (OWNER, term, owner.id, None, None)


def test_split_views_heal_to_the_longest_owner(cluster):
    for _ in range(4):
        cluster.add(start=False)
    a, b, c, d = cluster.locks
    cluster.see(0, [1])
    cluster.see(1, [0])
    cluster.see(2, [3])
    cluster.see(3, [2])
    a.start()
    b.start()
    first = cluster.wait_settled(locks=[a, b])
    time.sleep(0.1)
    c.start()
    d.start()
    second = cluster.wait_settled(locks=[c, d])
    assert len(cluster.owners()) == 2

    cluster.see_all()
    assert cluster.wait_settled() is first
    assert not second.is_owner(second.state.term)
    last = cluster.changes[cluster.locks.index(second)][-1]
    assert last.role == FOLLOWER and last.owner_id == first.id


def test_owners_that_claimed_together_still_merge(cluster):
    # Each owner sees its own age now and the other's from a moment ago: with
    # claims a round trip apart, both would think they are older.
    for _ in range(20):
        cluster.add(start=False)
        cluster.add(start=False)
        i, j = len(cluster.locks) - 2, len(cluster.locks) - 1
        a, b = cluster.locks[i], cluster.locks[j]
        for idx in range(len(cluster.locks)):
            cluster.see(idx, [idx])
        a.start()
        b.start()
        assert a.wait_settled(5).role == OWNER and b.wait_settled(5).role == OWNER
        for idx in (i, j):
            cluster.see(idx, [i, j])
        cluster.wait_settled(timeout=5, locks=[a, b])
        a.close()
        b.close()


def test_followers_take_over_when_the_owner_goes(cluster):
    for _ in range(4):
        cluster.add()
    owner = cluster.wait_settled()
    old_term = owner.state.term
    owner.close()
    assert not owner.is_owner(old_term)
    new_owner = cluster.wait_settled()
    assert new_owner is not owner
    assert new_owner.state.term != old_term


def test_follower_gives_up_after_miss_limit_probes(cluster):
    cluster.add()
    cluster.wait_settled(5)
    probes = []
    hidden = threading.Event()

    def peers():
        if hidden.is_set():
            probes.append(1)
            return []
        return cluster._peers(1)

    follower = cluster.add(peers=peers, miss_limit=5)
    cluster.wait_settled()
    hidden.set()
    until(lambda: follower.state.role == OWNER, message="follower never claimed")
    # Five misses to give up on the owner, and alone it claims on the fifth.
    assert len(probes) >= 5


def test_brief_miss_does_not_flap_to_another_owner(cluster):
    a = cluster.add()
    assert a.wait_settled(5).role == OWNER
    f = cluster.add(miss_limit=1000)
    cluster.wait_settled()
    b = cluster.add(start=False)
    cluster.see(2, [])
    b.start()
    assert b.wait_settled(5).role == OWNER
    time.sleep(0.2)
    assert f.state.owner_id == a.id
    before = len(cluster.changes[1])

    cluster.see(1, [2])
    time.sleep(0.3)
    assert f.state.owner_id == a.id
    assert len(cluster.changes[1]) == before
    cluster.see(1, [0, 2])
    time.sleep(0.2)
    assert f.state.owner_id == a.id


def test_waits_for_a_lower_id_that_is_electing(cluster):
    release = threading.Event()
    a = cluster.add(start=False)
    b = cluster.add(start=False, miss_limit=1000)
    if a.id > b.id:
        a.id, b.id = b.id, a.id
    low, high = a, b

    def slow_peers():
        # The low replica answers probes but has not decided anything yet.
        release.wait()
        return cluster._peers(0)

    low._peers = slow_peers
    low.start()
    high.start()
    time.sleep(0.4)
    assert high.state.role == ELECTING
    release.set()
    assert cluster.wait_settled() is low


def test_wait_on_a_lower_id_is_bounded(cluster):
    release = threading.Event()
    a = cluster.add(start=False)
    b = cluster.add(start=False, miss_limit=3)
    if a.id > b.id:
        a.id, b.id = b.id, a.id
    a._peers = lambda: (release.wait(), cluster._peers(0))[1]
    a.start()
    b.start()
    try:
        assert b.wait_settled(5).role == OWNER
    finally:
        release.set()
    assert cluster.wait_settled() is b


def test_raising_on_change_does_not_stop_the_lock(cluster):
    def boom(_state):
        raise RuntimeError("callback bug")

    a = cluster.add(on_change=boom)
    assert a.wait_settled(5).role == OWNER
    cluster.add(on_change=boom)
    cluster.wait_settled()
    a.close()
    until(lambda: cluster.locks[1].state.role == OWNER)


class FakePeer:
    """Completes the handshake with the right secret, then answers ``view``."""

    def __init__(self, view, sent=None):
        self.view = view
        self.sent = sent
        self.sock = socket.create_server(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            with conn:
                try:
                    deadline = time.monotonic() + 2
                    nonce = _recv(conn, deadline)
                    challenge = secrets.token_hex(16)
                    _send(conn, [challenge, _mac(SECRET, b"server", nonce)])
                    _recv(conn, deadline)
                    raw = json.dumps(self.view)
                    mac = _mac(SECRET, b"view", nonce, raw)
                    if self.sent is not None:
                        raw = json.dumps(self.sent)
                    _send(conn, [raw, mac])
                except Exception:  # pylint: disable=broad-exception-caught
                    pass

    def close(self):
        self.sock.close()


@pytest.mark.parametrize(
    "view",
    [
        {"id": "zzz", "role": "owner", "term": "t"},
        {"id": "zzz", "role": "owner", "term": "t", "age": None},
        {"id": "zzz", "role": "owner", "term": "t", "age": "old"},
        {"id": ["x"], "role": "owner", "term": "t", "age": 1.0},
        {"id": "zzz", "role": "king"},
        {"id": "zzz", "role": "owner", "term": "t", "age": 1.0},
        {"id": "zzz", "role": "owner", "term": "t", "age": 1.0, "rivals": [1]},
        ["not", "a", "dict"],
    ],
)
def test_malformed_views_are_ignored(cluster, view):
    fake = FakePeer(view)
    try:
        lock = cluster.add(
            peers=lambda: [("127.0.0.1", fake.port), ("127.0.0.1", lock.port)]
        )
        assert lock.wait_settled(5).role == OWNER
        other = cluster.add(
            peers=lambda: [("127.0.0.1", fake.port), ("127.0.0.1", lock.port)]
        )
        until(lambda: other.state.owner_id == lock.id, message="probe thread died")
    finally:
        fake.close()


def test_forged_view_is_rejected(cluster):
    # Signs a harmless view, then sends one claiming the oldest ownership, as
    # an on-path attacker rewriting the answer would.
    fake = FakePeer(
        {"id": "aaa", "role": "electing", "term": None},
        sent={"id": "aaa", "role": "owner", "term": "t", "age": 1e9, "rivals": []},
    )
    try:
        lock = cluster.add(peers=lambda: [("127.0.0.1", fake.port)])
        assert lock.wait_settled(5).role == OWNER
        time.sleep(0.2)
        assert lock.state.role == OWNER
    finally:
        fake.close()


def test_signed_view_is_followed(cluster):
    fake = FakePeer(
        {"id": "aaa", "role": "owner", "term": "t", "age": 1e9, "rivals": []}
    )
    try:
        lock = cluster.add(peers=lambda: [("127.0.0.1", fake.port)])
        assert lock.wait_settled(5).owner_id == "aaa"
    finally:
        fake.close()


def test_answers_nothing_to_unauthenticated_clients(cluster):
    lock = cluster.add()
    lock.wait_settled(5)
    with socket.create_connection(("127.0.0.1", lock.port), timeout=2) as conn:
        _send(conn, "nonce")
        challenge, _proof = _recv(conn, time.monotonic() + 2)
        _send(conn, "not-the-proof")
        conn.settimeout(2)
        assert conn.recv(1) == b""
    assert isinstance(challenge, str)


def test_oversized_and_dripped_frames_are_dropped(cluster):
    lock = cluster.add(probe_timeout=0.3)
    lock.wait_settled(5)
    with socket.create_connection(("127.0.0.1", lock.port), timeout=2) as conn:
        conn.sendall(struct.pack("!I", 10**9))
        assert conn.recv(1) == b""
    with socket.create_connection(("127.0.0.1", lock.port), timeout=2) as conn:
        start = time.monotonic()
        conn.sendall(struct.pack("!I", 10))
        try:
            for _ in range(10):
                conn.sendall(b"x")
                time.sleep(0.1)
        except OSError:
            pass
        conn.settimeout(2)
        try:
            assert conn.recv(1) == b""
        except ConnectionResetError:
            pass
        assert time.monotonic() - start < 1.5


def test_closed_lock_stops_answering(cluster):
    lock = cluster.add()
    term = lock.wait_settled(5).term
    lock.close()
    assert not lock.is_owner(term)
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", lock.port), timeout=1).close()
    for thread in lock._threads:
        thread.join(2)
        assert not thread.is_alive()


def test_wrong_secret_is_never_followed(cluster):
    good = cluster.add()
    good.wait_settled(5)
    rogue = cluster.add(secret=b"wrong")
    rogue.wait_settled(5)
    time.sleep(0.3)
    assert good.state.role == OWNER
    assert rogue.state.role == OWNER
    assert cluster.changes[0] == [good.state]


_NODE = textwrap.dedent(
    """
    import sys, time
    from dash._shared_storage._cluster_lock import ClusterLock
    ports = [int(p) for p in sys.argv[1].split(",")]
    lock = ClusterLock(
        peers=lambda: [("127.0.0.1", p) for p in ports],
        secret=b"test-secret",
        bind=("127.0.0.1", int(sys.argv[2])),
        probe_interval=0.05,
        miss_limit=2,
    ).start()
    print(lock.id, flush=True)
    while True:
        time.sleep(1)
    """
)


def _free_ports(n):
    socks = [socket.create_server(("127.0.0.1", 0)) for _ in range(n)]
    ports = [s.getsockname()[1] for s in socks]
    for s in socks:
        s.close()
    return ports


@pytest.mark.skipif(sys.platform == "win32", reason="SIGKILL")
def test_killed_owner_process_is_replaced(cluster):
    ports = _free_ports(3)
    local_port = ports[2]
    all_ports = ",".join(str(p) for p in ports)
    procs = {}
    try:
        for port in ports[:2]:
            proc = subprocess.Popen(
                [sys.executable, "-c", _NODE, all_ports, str(port)],
                stdout=subprocess.PIPE,
                text=True,
            )
            procs[proc.stdout.readline().strip()] = proc
        time.sleep(0.5)
        # Joins after the processes elected, so it follows one of them.
        local = ClusterLock(
            peers=lambda: [("127.0.0.1", p) for p in ports],
            secret=SECRET,
            bind=("127.0.0.1", local_port),
            **FAST,
        ).start()
        cluster.locks.append(local)
        state = local.wait_settled(10)
        assert state.role == FOLLOWER and state.owner_id in procs

        dead = state.owner_id
        os.kill(procs[dead].pid, signal.SIGKILL)
        until(
            lambda: local.state.role != ELECTING
            and local.state.owner_id not in (dead, None)
            or local.state.role == OWNER,
            message="no new owner after the kill",
        )
    finally:
        for proc in procs.values():
            proc.kill()
            proc.wait()


def test_resolve_peers():
    peers = resolve_peers("localhost", 8050)
    assert peers and all(port == 8050 for _host, port in peers)
    assert resolve_peers("does-not-resolve.invalid", 8050) == []


def _tls(make_cert, name="replica"):
    from dash._shared_storage._cluster_lock import tls_contexts

    return tls_contexts(*make_cert(name))


def test_tls_replicas_settle(cluster, make_cert):
    tls = _tls(make_cert)
    for _ in range(3):
        cluster.add(tls=tls)
    owner = cluster.wait_settled()
    view = probe(("127.0.0.1", owner.port), SECRET, 1.0, tls.client)
    assert view["role"] == OWNER and view["id"] == owner.id


def test_tls_lock_answers_no_plaintext_probe(cluster, make_cert):
    lock = cluster.add(tls=_tls(make_cert))
    lock.wait_settled(5)
    assert probe(("127.0.0.1", lock.port), SECRET, 1.0) is None


def test_tls_rejects_a_certificate_from_another_ca(cluster, make_cert):
    good = cluster.add(tls=_tls(make_cert))
    good.wait_settled(5)
    other = _tls(make_cert, "other")
    assert probe(("127.0.0.1", good.port), SECRET, 1.0, other.client) is None
    rogue = cluster.add(tls=other)
    rogue.wait_settled(5)
    time.sleep(0.3)
    assert good.state.role == OWNER and rogue.state.role == OWNER


def test_plaintext_and_tls_replicas_do_not_mix(cluster, make_cert):
    tls_lock = cluster.add(tls=_tls(make_cert))
    tls_lock.wait_settled(5)
    plain = cluster.add()
    plain.wait_settled(5)
    time.sleep(0.3)
    assert tls_lock.state.role == OWNER and plain.state.role == OWNER
