"""Shared storage across the replicas of an app, with no external service.

``ClusterSharedStorage`` is ``LocalSharedStorage`` stretched across pods or
containers. In each replica the first process to bind the cluster port runs a
:class:`ClusterLock`, which elects one owner among the replicas. The owner's
lock process hosts the ``StoreEngine`` on the next port up; every other worker,
in any replica, proxies to it over TCP. Workers that did not get the cluster
port ask their replica's lock process, on loopback, where the owner is.

The owner's term is the token clients present, so an owner change looks like
a re-election does locally: the buffer is gone and readers get
``SharedStorageGap``. A deposed owner's server stops answering at once. Data
crosses the network unencrypted, so keep the ports on a private network, as
with a Redis without TLS.
"""

import atexit
import errno
import hashlib
import hmac
import os
import socket
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from ._cluster_lock import (
    ELECTING,
    FOLLOWER,
    OWNER,
    Addr,
    ClusterLock,
    LockState,
    listen,
    probe,
    resolve_peers,
)
from ._engine import DEFAULT_BUFFER
from ._transport import OwnerServer
from .base import SharedStorageError
from .local import LocalSharedStorage, _Coordinator

DEFAULT_PORT = 7100
SECRET_ENV = "DASH_SECRET_KEY"

_PROBE_INTERVAL = 1.0
_PROBE_TIMEOUT = 0.5
_SETTLE_TIMEOUT = 15.0
# A pod that vanishes does not close its sockets, so a client could wait on it
# forever: keep long polls short and give up on an answer that never comes.
_CLIENT_POLL_TIMEOUT = 5.0
_RECV_TIMEOUT = _CLIENT_POLL_TIMEOUT + 5.0
# Followers need a few missed probes to give up on a dead owner.
_FAILOVER_WINDOW = 10.0
_ADDR_IN_USE = {errno.EADDRINUSE, getattr(errno, "WSAEADDRINUSE", errno.EADDRINUSE)}


def _derive_secret(secret: str) -> bytes:
    # The app's signing secret signs other things too: never use it as is.
    return hmac.new(
        secret.encode(), b"dash-shared-storage-cluster", hashlib.sha256
    ).digest()


class _ClusterCoordinator(_Coordinator):
    """Elects the owner across replicas with a ClusterLock instead of a local
    socket bind. Role and token follow the lock: owner while it holds a term,
    client of the current owner otherwise."""

    client_poll_timeout = _CLIENT_POLL_TIMEOUT
    recv_timeout = _RECV_TIMEOUT
    failover_window = _FAILOVER_WINDOW

    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: str,
        port: int,
        secret: bytes,
        peers: Callable[[], List[Addr]],
        buffer_size: int,
        mode: str,
        path: Optional[str],
        flush_interval: float,
        probe_interval: float,
        settle_timeout: float,
    ):
        super().__init__(
            f"cluster-{host}-{port}", buffer_size, mode, path, flush_interval
        )
        self._port = port
        self._data_port = port + 1
        self._secret = secret
        self._peers = peers
        self._probe_interval = probe_interval
        self._settle_timeout = settle_timeout
        self._cluster: Optional[ClusterLock] = None
        self._term: Optional[str] = None
        self._closed = False

    def is_owner(self) -> bool:
        self.ensure()
        if self._role == "owner" and not self._holds_term():
            with self._lock:
                if self._role == "owner" and not self._holds_term():
                    self._stop_serving()
                    self._elect()
        return self._role == "owner"

    def connect(self) -> Tuple[socket.socket, str]:
        sock, token = super().connect()
        sock.settimeout(self.recv_timeout)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        return sock, token

    def needs_election(self) -> bool:
        return self._role is None or (self._role == "owner" and not self._holds_term())

    def _holds_term(self) -> bool:
        return self._cluster is not None and self._cluster.is_owner(self._term)

    def on_owner_lost(self) -> None:
        with self._lock:
            if self._role == "owner" and self._holds_term():
                return
            self._stop_serving()
            self._role = None
            self._elect()

    # --- election ----------------------------------------------------------
    def _elect(self) -> None:
        if self._closed:
            raise SharedStorageError("shared storage is closed")
        deadline = time.monotonic() + self._settle_timeout
        while True:
            if self._cluster is None:
                self._try_hold_lock()
            if self._cluster is not None:
                state = self._cluster.wait_settled(deadline - time.monotonic())
                if self._apply(state):
                    return
            elif self._follow_local():
                return
            if time.monotonic() >= deadline:
                raise SharedStorageError(
                    "no shared-storage cluster owner was elected in "
                    f"{self._settle_timeout:g}s"
                )
            time.sleep(min(0.1, self._probe_interval))

    def _try_hold_lock(self) -> None:
        try:
            self._cluster = ClusterLock(
                peers=self._peers,
                secret=self._secret,
                bind=("", self._port),
                advert={"data_port": self._data_port},
                on_change=self._on_change,
                probe_interval=self._probe_interval,
                probe_timeout=_PROBE_TIMEOUT,
            ).start()
        except OSError as err:
            if err.errno in _ADDR_IN_USE:
                return  # another process of this replica holds the port
            raise SharedStorageError(
                f"cannot listen on the cluster port {self._port}: {err}"
            ) from err
        atexit.register(self.close)

    def _follow_local(self) -> bool:
        """Learn the owner from this replica's lock process."""
        view = probe(("127.0.0.1", self._port), self._secret, _PROBE_TIMEOUT)
        if view is None:
            return False
        if view["role"] == ELECTING:
            return False
        host = "127.0.0.1" if view["role"] == OWNER else view["owner_host"]
        return self._follow(host, view.get("advert"), view["term"])

    def _apply(self, state: LockState) -> bool:
        if state.role == OWNER:
            self._serve(state.term)
            return True
        if state.role == FOLLOWER and state.owner_addr is not None:
            return self._follow(state.owner_addr[0], state.advert, state.term)
        return False

    def _follow(self, host: str, advert, term: Optional[str]) -> bool:
        if not isinstance(advert, dict) or not term:
            return False
        port = advert.get("data_port")
        if not isinstance(port, int) or isinstance(port, bool):
            return False
        self._family = socket.AF_INET6 if ":" in host else socket.AF_INET
        self._address = (host, port)
        self._token = term
        self._role = "client"
        return True

    def _serve(self, term: Optional[str]) -> None:
        assert term is not None
        if self._role == "owner" and self._term == term:
            return
        self._stop_serving()
        sock = self._listen_data()
        engine = self._new_engine()
        server = OwnerServer(engine, sock, term, guard=lambda: self._guard(term))
        server.start()
        self._engine, self._server, self._term = engine, server, term
        self._family, self._address = socket.AF_INET, ("127.0.0.1", self._data_port)
        self._token = term
        self._role = "owner"

    def _guard(self, term: str) -> bool:
        return self._cluster is not None and self._cluster.is_owner(term)

    def _listen_data(self) -> socket.socket:
        # A server closed a moment ago, ours or a previous process's, can hold
        # the port briefly.
        for attempt in range(20):
            try:
                return listen("", self._data_port)
            except OSError:
                if attempt == 19:
                    raise
                time.sleep(0.1)
        raise AssertionError("unreachable")

    def _stop_serving(self) -> None:
        server, engine = self._server, self._engine
        self._server = self._engine = None
        if server is not None:
            if engine is not None and not self._holds_term():
                # Deposed: a persistent store must not flush this owner's
                # state over the new owner's on a shared volume.
                engine.abandon()
            # Also closes the engine, flushing a persistent store.
            server.close()
        self._term = None

    def _on_change(self, state: LockState) -> None:
        with self._lock:
            if self._closed:
                return
            if state.role == OWNER:
                # Serve at once: followers start connecting as soon as they
                # see this replica as owner.
                self._serve(state.term)
            elif self._role == "owner" or (
                self._role == "client" and state.term != self._token
            ):
                self._stop_serving()
                self._role = None

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._stop_serving()
            if self._cluster is not None:
                self._cluster.close()
                self._cluster = None
            self._role = None


class ClusterSharedStorage(LocalSharedStorage):
    """Shared storage across every replica of an app, with no external service.

    Replicas find each other through ``host``, a name that resolves to all of
    them (a Kubernetes headless Service, a podman network alias), and elect one
    owner that holds the store. Each replica needs ``port`` (the election) and
    ``port + 1`` (the store) reachable from the others. ``peers`` replaces the
    DNS lookup with a function returning ``(host, port)`` lock addresses, for a
    fixed list of hosts.

    All replicas share ``secret`` (default: ``$DASH_SECRET_KEY``), which they
    prove to each other without sending it. Traffic is not encrypted.

    When the owner goes, another replica takes over with an empty store
    (``mode="memory"``) or what it recovers from ``path`` (the persistent
    modes, which only help when ``path`` is on a volume the replicas share).
    Readers get ``SharedStorageGap``. If replicas briefly elect two owners,
    say when they all start at once, the one that owned longer wins and
    writes made on the other in the meantime are lost.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        host: Optional[str] = None,
        port: int = DEFAULT_PORT,
        secret: Optional[str] = None,
        peers: Optional[Callable[[], List[Addr]]] = None,
        buffer_size: int = DEFAULT_BUFFER,
        mode: str = "memory",
        path: Optional[str] = None,
        flush_interval: float = 60.0,
        probe_interval: float = _PROBE_INTERVAL,
        settle_timeout: float = _SETTLE_TIMEOUT,
    ):
        if host is None and peers is None:
            raise SharedStorageError("ClusterSharedStorage needs a host or peers")
        secret = secret or os.environ.get(SECRET_ENV)
        if not secret:
            raise SharedStorageError(
                "ClusterSharedStorage needs a secret shared by every replica: "
                f"pass secret= or set {SECRET_ENV}"
            )
        if peers is None:
            name: str = host or ""
            peers = lambda: resolve_peers(name, port)  # noqa: E731
        self._cluster_args: Dict[str, Any] = dict(
            host=host or "peers",
            port=port,
            secret=_derive_secret(secret),
            peers=peers,
            probe_interval=probe_interval,
            settle_timeout=settle_timeout,
        )
        super().__init__(
            namespace=f"cluster-{host}-{port}",
            buffer_size=buffer_size,
            mode=mode,
            path=path,
            flush_interval=flush_interval,
        )

    def _new_coordinator(  # pylint: disable=too-many-arguments
        self, namespace, buffer_size, mode, path, flush_interval
    ) -> _Coordinator:
        return _ClusterCoordinator(
            buffer_size=buffer_size,
            mode=mode,
            path=path,
            flush_interval=flush_interval,
            **self._cluster_args,
        )
