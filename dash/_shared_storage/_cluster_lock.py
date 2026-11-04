"""Network lock that elects one owner among the replicas of an app.

Every replica runs a ``ClusterLock`` on the same port. It finds its peers
through a name that resolves to all of them (a Kubernetes headless Service, a
podman network alias), asks each one who owns the store, and follows the owner
it finds. With no owner in sight, the lowest id among the replicas it reaches
claims ownership under a fresh term.

There is no consensus. Two owners exist for a while when replicas see
different DNS answers, which is normal when they all boot at once from zero.
Owners probe each other too: when they meet, the one that has owned longer
wins and the other steps down. The shared-storage contract already allows
this, since an owner change loses its buffer and readers get a gap. A data
server checks its term with ``is_owner`` so a deposed owner stops taking
writes. An owner cut off from every peer keeps owning until it can reach them
again, and replicas that cannot reach each other at all stay split.

With ``replicas`` set (the number of replicas the app runs), a majority is
needed. Each electing replica backs one candidate, the lowest electing id it
sees, and a replica claims only once a majority (itself included) has backed
it without a break for a whole lease. An owner holds a lease that it renews
only while a majority follows its term. An owner on the minority side of a
partition stops owning when its lease runs out, before the majority side may
claim, a peer backs one claimant at a time, and a replica that starts alone
waits for its peers.

Peers prove they hold the shared secret with an HMAC challenge both ways, and
the view a replica answers with is MACed too, so the secret never crosses the
wire and an on-path attacker cannot forge a view. Nothing is encrypted.
"""

import hashlib
import hmac
import json
import logging
import secrets
import socket
import ssl
import struct
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Tuple

from ._codec import decode, encode

Addr = Tuple[str, int]

ELECTING = "electing"
FOLLOWER = "follower"
OWNER = "owner"
_ROLES = (ELECTING, FOLLOWER, OWNER)

_MAX_PROBE_WORKERS = 16
_MAX_CONNECTIONS = 64
_MAX_FRAME = 16384

logger = logging.getLogger(__name__)


class LockState(NamedTuple):
    role: str
    term: Optional[str] = None
    owner_id: Optional[str] = None
    # The owner's lock address as this replica reached it, and what the owner
    # advertises (its data port, ...). None for the owner itself.
    owner_addr: Optional[Addr] = None
    advert: Any = None


class TLS(NamedTuple):
    """Mutual TLS between replicas: each side presents its certificate and
    checks the other's against the CA. Peers are reached by IP, so there is no
    hostname to check; trust comes from the CA (and the shared secret)."""

    server: ssl.SSLContext
    client: ssl.SSLContext


def tls_contexts(cert: str, key: str, ca: Optional[str] = None) -> TLS:
    """Contexts from PEM files. ``ca`` defaults to ``cert``, so a single
    self-signed certificate mounted in every replica is enough."""
    server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    client = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    client.check_hostname = False
    for context in (server, client):
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.verify_mode = ssl.CERT_REQUIRED
        # An encrypted key would prompt for a password on a terminal.
        context.load_cert_chain(cert, key, password=_no_password)
        context.load_verify_locations(ca or cert)
    return TLS(server, client)


def _no_password() -> str:
    raise ssl.SSLError("the cluster TLS key must not be encrypted")


def resolve_peers(host: str, port: int) -> List[Addr]:
    """Every address ``host`` resolves to, on ``port``. Empty when it does not
    resolve, which is normal while the first replicas start."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return []
    return sorted({(str(info[4][0]), port) for info in infos})


def listen(host: str, port: int) -> socket.socket:
    """A listening TCP socket. ``host`` of ``""`` takes every address, IPv4 and
    IPv6 both where the host has them."""
    if host == "" and socket.has_dualstack_ipv6():
        return socket.create_server(
            ("", port), family=socket.AF_INET6, dualstack_ipv6=True
        )
    return socket.create_server((host or "0.0.0.0", port))


def _mac(secret: bytes, label: bytes, *parts: str) -> str:
    return hmac.new(
        secret, label + "\0".join(parts).encode(), hashlib.sha256
    ).hexdigest()


def _send(conn: socket.socket, obj: Any) -> None:
    data = encode(obj)
    conn.sendall(struct.pack("!I", len(data)) + data)


def _recv(conn: socket.socket, deadline: float) -> Any:
    """One small frame, read before ``deadline`` (monotonic) or not at all, so
    a peer that drips bytes or claims a huge frame cannot hold a thread."""

    def exactly(n: int) -> bytes:
        chunks = []
        while n:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError("cluster lock exchange timed out")
            conn.settimeout(left)
            chunk = conn.recv(n)
            if not chunk:
                raise ConnectionError("peer closed")
            chunks.append(chunk)
            n -= len(chunk)
        return b"".join(chunks)

    (length,) = struct.unpack("!I", exactly(4))
    if length > _MAX_FRAME:
        raise ValueError("cluster lock frame too large")
    return decode(exactly(length))


# Peers whose TLS handshake failed, so the warning is logged once per peer
# until it succeeds again.
_tls_failed: Set[Addr] = set()


def probe(
    addr: Addr,
    secret: bytes,
    timeout: float,
    tls: Optional[ssl.SSLContext] = None,
) -> Optional[Dict[str, Any]]:
    """Ask the lock at ``addr`` for its view: its id, role and term, plus the
    owner's advert (and, from a follower, the owner's host). None when it does
    not answer or cannot prove it holds ``secret``. ``tls`` is the client
    context when the replicas talk TLS."""
    deadline = time.monotonic() + timeout
    try:
        raw = socket.create_connection(addr, timeout=timeout)
        conn = tls.wrap_socket(raw) if tls is not None else raw
        _tls_failed.discard(addr)
        with conn:
            nonce = secrets.token_hex(16)
            _send(conn, nonce)
            challenge, proof = _recv(conn, deadline)
            if not hmac.compare_digest(proof, _mac(secret, b"server", nonce)):
                return None
            _send(conn, _mac(secret, b"client", challenge))
            raw, view_mac = _recv(conn, deadline)
            if not hmac.compare_digest(view_mac, _mac(secret, b"view", nonce, raw)):
                return None
            view = json.loads(raw)
    except ssl.SSLError as err:
        # Otherwise silent: replicas would just never see each other.
        if addr not in _tls_failed:
            _tls_failed.add(addr)
            logger.warning("dash cluster TLS handshake with %s failed: %s", addr, err)
        return None
    except Exception:  # pylint: disable=broad-exception-caught
        return None
    if not _valid_view(view):
        return None
    return dict(view)


def _valid_view(view: Any) -> bool:
    if not isinstance(view, dict):
        return False
    if not isinstance(view.get("id"), str) or view.get("role") not in _ROLES:
        return False
    if view["role"] == OWNER:
        age = view.get("age")
        return (
            isinstance(view.get("term"), str)
            and isinstance(age, (int, float))
            and not isinstance(age, bool)
            and age >= 0
            and isinstance(view.get("rivals"), list)
            and all(isinstance(r, str) for r in view["rivals"])
        )
    if view["role"] == FOLLOWER:
        return isinstance(view.get("term"), str) and isinstance(
            view.get("owner_host"), str
        )
    ballot = view.get("ballot")
    return ballot is None or (
        isinstance(ballot, list)
        and len(ballot) == 2
        and (ballot[0] is None or isinstance(ballot[0], str))
        and isinstance(ballot[1], int)
        and not isinstance(ballot[1], bool)
    )


class ClusterLock:  # pylint: disable=too-many-instance-attributes
    """Elects and tracks the owner among the replicas ``peers`` returns.

    ``peers`` is called every probe and returns lock addresses, this replica's
    own included or not. ``advert`` is handed to followers along with the
    owner's address. ``on_change`` is called with the new ``LockState`` from
    the probe thread whenever the role, owner or term changes.

    ``miss_limit`` probes in a row without its owner make a follower give up
    on it; a replica waiting on a lower id to claim waits that many probes too.
    """

    def __init__(
        self,
        peers: Callable[[], List[Addr]],
        secret: bytes,
        bind: Addr = ("0.0.0.0", 0),
        advert: Any = None,
        on_change: Optional[Callable[[LockState], None]] = None,
        tls: Optional[TLS] = None,
        probe_interval: float = 1.0,
        probe_timeout: float = 0.5,
        miss_limit: int = 3,
        replicas: Optional[int] = None,
    ):
        if not secret:
            raise ValueError("ClusterLock needs a non-empty secret")
        if replicas is not None and (
            not isinstance(replicas, int) or isinstance(replicas, bool) or replicas < 1
        ):
            raise ValueError("replicas must be a positive integer")
        self.id = secrets.token_hex(8)
        self._peers = peers
        self._secret = secret
        self._advert = advert
        self._on_change = on_change
        self._tls = tls
        self._interval = probe_interval
        self._timeout = probe_timeout
        self._miss_limit = miss_limit
        self._misses = 0
        self._deferred = 0
        self._owned_since = 0.0
        # Owners this one judged younger than itself, which must step down.
        self._rivals: List[str] = []
        self._majority = replicas // 2 + 1 if replicas else None
        # Ticks start at most interval + timeout apart. A new owner needs
        # about three of them to see its followers follow, and a lease of four
        # survives a dropped probe after that.
        self.lease = 4 * (probe_interval + probe_timeout)
        self._quorum_at = 0.0
        # Majority mode: whom this replica would see own (its candidate) and
        # a counter bumped on every change, since when, and which candidates
        # it gave up on. Peers backing this replica: id -> (their counter,
        # first seen with it).
        self._ballot: Tuple[Optional[str], int] = (None, 0)
        self._ballot_since = time.monotonic()
        self._banned: Dict[str, float] = {}
        self._backers: Dict[str, Tuple[int, float]] = {}
        self._state = LockState(ELECTING)
        self._cond = threading.Condition()
        self._closed = threading.Event()
        self._slots = threading.BoundedSemaphore(_MAX_CONNECTIONS)
        self._sock = listen(*bind)
        self.port = self._sock.getsockname()[1]
        self._pool = ThreadPoolExecutor(
            _MAX_PROBE_WORKERS, thread_name_prefix="dash-cluster-probe"
        )
        self._threads = [
            threading.Thread(target=self._serve, name="dash-cluster-lock", daemon=True),
            threading.Thread(target=self._run, name="dash-cluster-probe", daemon=True),
        ]

    # --- public ------------------------------------------------------------
    def start(self) -> "ClusterLock":
        for thread in self._threads:
            thread.start()
        return self

    def close(self) -> None:
        if self._closed.is_set():
            return
        self._closed.set()
        try:
            # close() alone does not wake a thread blocked in accept() on Linux.
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self._sock.close()
        except OSError:
            pass
        self._pool.shutdown(wait=False, cancel_futures=True)
        with self._cond:
            self._cond.notify_all()

    @property
    def state(self) -> LockState:
        return self._state

    def is_owner(self, term: Optional[str]) -> bool:
        state = self._state
        return (
            not self._closed.is_set()
            and state.role == OWNER
            and term is not None
            and state.term == term
            and self._leased()
        )

    def _leased(self) -> bool:
        return (
            self._majority is None or time.monotonic() - self._quorum_at <= self.lease
        )

    def wait_settled(self, timeout: Optional[float] = None) -> LockState:
        """Block until this replica is an owner or a follower, or the timeout
        passes. Returns the state either way."""
        with self._cond:
            self._cond.wait_for(
                lambda: self._state.role != ELECTING or self._closed.is_set(),
                timeout,
            )
            return self._state

    # --- server ------------------------------------------------------------
    def _view(self) -> Dict[str, Any]:
        state = self._state
        if state.role == OWNER and not self._leased():
            state = LockState(ELECTING)
        view = {"id": self.id, "role": state.role, "term": state.term}
        if state.role == ELECTING and self._majority is not None:
            view["ballot"] = list(self._ballot)
        if state.role == OWNER:
            view["age"] = time.monotonic() - self._owned_since
            view["advert"] = self._advert
            view["rivals"] = list(self._rivals)
        elif state.role == FOLLOWER:
            view["owner_id"] = state.owner_id
            view["owner_host"] = state.owner_addr[0] if state.owner_addr else None
            view["advert"] = state.advert
        return view

    def _serve(self) -> None:
        while not self._closed.is_set():
            try:
                conn, _ = self._sock.accept()
            except OSError:
                if self._closed.is_set():
                    return
                # Out of file descriptors or similar: an owner that stops
                # answering looks dead to its peers, so keep trying.
                time.sleep(0.1)
                continue
            if not self._slots.acquire(  # pylint: disable=consider-using-with
                blocking=False
            ):
                conn.close()
                continue
            threading.Thread(target=self._answer, args=(conn,), daemon=True).start()

    def _answer(self, conn: socket.socket) -> None:
        deadline = time.monotonic() + self._timeout
        try:
            if self._tls is not None:
                conn.settimeout(self._timeout)
                conn = self._tls.server.wrap_socket(conn, server_side=True)
            with conn:
                nonce = _recv(conn, deadline)
                if not isinstance(nonce, str) or not 0 < len(nonce) <= 64:
                    return
                challenge = secrets.token_hex(16)
                _send(conn, [challenge, _mac(self._secret, b"server", nonce)])
                proof = _recv(conn, deadline)
                expected = _mac(self._secret, b"client", challenge)
                if not isinstance(proof, str) or not hmac.compare_digest(
                    proof, expected
                ):
                    return
                if self._closed.is_set():
                    return
                view = json.dumps(self._view(), sort_keys=True)
                _send(conn, [view, _mac(self._secret, b"view", nonce, view)])
        except Exception:  # pylint: disable=broad-exception-caught
            # Garbage, a timeout or a dropped peer: it just gets no answer.
            pass
        finally:
            self._slots.release()

    # --- probing -----------------------------------------------------------
    def _probe(self, addr: Addr) -> Optional[Dict[str, Any]]:
        return probe(
            addr,
            self._secret,
            self._timeout,
            self._tls.client if self._tls is not None else None,
        )

    def _run(self) -> None:
        while not self._closed.is_set():
            try:
                self._tick()
            except Exception:  # pylint: disable=broad-exception-caught
                if self._closed.is_set():
                    return
                logger.exception("dash cluster lock probe failed")
            self._closed.wait(self._interval)

    def _tick(self) -> None:  # pylint: disable=too-many-branches
        started = time.monotonic()
        peers = list(self._peers())
        views = {}
        for addr, view in zip(peers, self._pool.map(self._probe, peers)):
            if view is not None and view["id"] != self.id:
                views[view["id"]] = (addr, view)
        if self._closed.is_set():
            return
        if self._majority is not None:
            self._vote(views)

        state = self._state
        if state.role == FOLLOWER:
            if state.owner_id in views:
                self._misses = 0
            else:
                # Its owner may be briefly unreachable: stick with it rather
                # than flap to another owner or claim.
                self._misses += 1
                if self._misses < self._miss_limit:
                    return

        owners = {
            view_id: (addr, view)
            for view_id, (addr, view) in views.items()
            if view["role"] == OWNER
        }
        if owners:
            self._misses = 0
            self._deferred = 0
        if state.role == OWNER:
            if self._majority is not None:
                if not self._leased():
                    # Peers may already count it as electing: never renew.
                    self._step_down()
                    return
                following = [
                    view
                    for _, view in views.values()
                    if view["role"] == FOLLOWER and view["term"] == state.term
                ]
                if 1 + len(following) >= self._majority:
                    self._quorum_at = started
            self._resolve_owners(owners)
            return
        if owners:
            # Longest owned, then lowest id. Ages are monotonic durations, so
            # wall clocks that disagree across hosts do not matter.
            owner_id = min(owners, key=lambda o: (-owners[o][1]["age"], o))
            self._follow(owner_id, *owners[owner_id])
            return

        if self._majority is not None:
            if self._may_claim():
                self._claim(started)
            else:
                self._set(LockState(ELECTING))
            return

        # No owner anywhere: the lowest id claims. Wait on a lower one only so
        # long, in case it follows an owner this replica cannot reach.
        if all(self.id < other for other in views) or (
            self._deferred >= self._miss_limit
        ):
            self._claim(started)
        else:
            self._deferred += 1
            self._set(LockState(ELECTING))

    def _claim(self, started: float) -> None:
        self._deferred = 0
        self._misses = 0
        self._owned_since = time.monotonic()
        # Majority mode: lease from the probe round that saw the backing, not
        # from now. A voter may switch right after answering, and a slow
        # round would otherwise stretch this lease past that switch.
        self._quorum_at = started
        self._rivals = []
        self._set(LockState(OWNER, secrets.token_hex(8), self.id))

    def _vote(self, views: Dict[str, Tuple[Addr, Dict[str, Any]]]) -> None:
        """Back the lowest electing id in sight, and track who backs this one.

        A candidate that never manages to claim (it cannot reach a majority
        itself) is passed over for a while, so the others are not stuck."""
        now = time.monotonic()
        if self._state.role != ELECTING:
            candidate = None
        else:
            self._banned = {i: t for i, t in self._banned.items() if t > now}
            electing = [
                view_id
                for view_id, (_, view) in views.items()
                if view["role"] == ELECTING and view_id not in self._banned
            ]
            candidate = min([self.id, *electing])
            stuck = now - self._ballot_since > 3 * self.lease
            if candidate == self._ballot[0] != self.id and stuck:
                self._banned[candidate] = now + 3 * self.lease
        if candidate != self._ballot[0]:
            self._ballot = (candidate, self._ballot[1] + 1)
            self._ballot_since = now
        backers = {}
        for view_id, (_, view) in views.items():
            ballot = view.get("ballot")
            if view["role"] != ELECTING or not ballot or ballot[0] != self.id:
                continue
            seen = self._backers.get(view_id)
            same = seen is not None and seen[0] == ballot[1]
            backers[view_id] = seen if same else (ballot[1], now)
        self._backers = backers

    def _may_claim(self) -> bool:
        """A majority, this replica included, that has backed it without a
        break for longer than a lease.

        A ballot stands for one candidate; any change, following an owner
        included, bumps its counter and restarts the run. An owner renews only
        from peers that follow it, and two majorities share a peer: a peer
        that backed this replica for a whole lease neither followed an owner
        (whose lease has run out since) nor backed another claimant then.
        """
        assert self._majority is not None
        if self._state.role == FOLLOWER:
            return False
        now = time.monotonic()
        if self._ballot[0] != self.id or now - self._ballot_since <= self.lease:
            return False
        backed = [
            since for _, since in self._backers.values() if now - since > self.lease
        ]
        return 1 + len(backed) >= self._majority

    def _step_down(self) -> None:
        self._rivals = []
        self._misses = 0
        self._deferred = 0
        self._set(LockState(ELECTING))

    def _resolve_owners(self, owners: Dict[str, Tuple[Addr, Dict[str, Any]]]) -> None:
        """Settle which of several owners keeps owning.

        Both sides comparing ages would deadlock: each measures its own age
        now and the other's as reported a moment ago, so two owners that
        claimed within a round trip of each other would each think they are
        older. Instead only the lower id judges. It steps down to an older
        owner, or keeps owning and lists the younger ones as rivals; an owner
        steps down once a lower id lists it.
        """
        judged_by = [
            o for o in owners if o < self.id and self.id in owners[o][1]["rivals"]
        ]
        if judged_by:
            winner = min(judged_by)
            self._follow(winner, *owners[winner])
            return
        age = time.monotonic() - self._owned_since
        older = [o for o in owners if o > self.id and owners[o][1]["age"] > age]
        if older:
            winner = max(older, key=lambda o: owners[o][1]["age"])
            self._follow(winner, *owners[winner])
            return
        self._rivals = sorted(o for o in owners if o > self.id)

    def _follow(self, owner_id: str, addr: Addr, view: Dict[str, Any]) -> None:
        self._rivals = []
        self._set(LockState(FOLLOWER, view["term"], owner_id, addr, view.get("advert")))

    def _set(self, state: LockState) -> None:
        with self._cond:
            if state == self._state or self._closed.is_set():
                return
            self._state = state
            self._cond.notify_all()
        if self._on_change is not None:
            try:
                self._on_change(state)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("dash cluster lock on_change failed")
