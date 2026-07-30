"""Owner-elected, cross-process shared storage.

Every worker constructs a :class:`LocalSharedStorage`; on first use they race to
become the single *owner* by binding a stable address (AF_UNIX socket on POSIX,
TCP loopback on Windows). The winner hosts the authoritative :class:`StoreEngine`
and serves it; the losers become clients that connect to it. The bind itself is
the lease -- when the owner dies the address frees, and a client that finds it
gone re-elects (coming up cold, by design for the in-memory backend).

Because the owner holds the engine directly, a single-process deployment (its
own owner) pays no socket overhead at all; only extra worker processes proxy.
"""

import asyncio
import atexit
import hashlib
import json
import os
import secrets
import socket
import sys
import tempfile
import threading
import time
from typing import Any, Optional

from ._engine import DEFAULT_BUFFER, PollResult, StoreEngine
from ._transport import EOF, OwnerServer, connect_to_owner, recv_frame, send_frame
from .base import BaseSharedStorage, SharedStorageError, SharedStorageGap, Subscription

_HAS_AF_UNIX = hasattr(socket, "AF_UNIX")
_CLIENT_POLL_TIMEOUT = 20.0  # long-poll cycle for remote subscribers
_OWNER_POLL_TIMEOUT = 1.0  # local poll cycle; short so close() stays responsive


def _default_namespace() -> str:
    raw = f"{os.getcwd()}|{sys.argv[0] if sys.argv else ''}".encode()
    return hashlib.sha1(raw).hexdigest()[:16]


def _paths(namespace: str):
    base = os.path.join(tempfile.gettempdir(), f"dash-shared-{namespace}")
    return base + ".sock", base + ".addr"


def _tcp_port(namespace: str) -> int:
    h = int(hashlib.sha1(namespace.encode()).hexdigest(), 16)
    return 49152 + (h % (65535 - 49152))


def _write_advertisement(addr_path, family, address, token) -> None:
    payload = json.dumps(
        {"family": int(family), "address": address, "token": token}
    ).encode("utf-8")
    tmp = f"{addr_path}.{os.getpid()}.tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(payload)
    os.replace(tmp, addr_path)


def _read_advertisement(addr_path, retries=100, delay=0.05):
    for _ in range(retries):
        try:
            with open(addr_path, "rb") as f:
                data = json.loads(f.read().decode("utf-8"))
            family = data["family"]
            address = data["address"]
            if family == int(socket.AF_INET):
                address = tuple(address)  # json list -> (host, port)
            return family, address, data["token"]
        except (FileNotFoundError, ValueError, KeyError):
            time.sleep(delay)
    raise ConnectionError("shared-storage owner advertisement not found")


def _unix_is_stale(path: str) -> bool:
    probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    probe.settimeout(0.5)
    try:
        probe.connect(path)
        return False  # a live owner answered
    except OSError:
        return True  # refused / no listener -> stale socket file
    finally:
        probe.close()


def _try_bind(namespace: str, sock_path: str):
    """Try to become the owner. Returns (listen_sock, family, address) or None."""
    if _HAS_AF_UNIX:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.bind(sock_path)
        except OSError:
            if _unix_is_stale(sock_path):
                try:
                    os.unlink(sock_path)
                    s.bind(sock_path)
                except OSError:
                    s.close()
                    return None
            else:
                s.close()
                return None
        os.chmod(sock_path, 0o600)
        return s, socket.AF_UNIX, sock_path

    port = _tcp_port(namespace)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", port))
    except OSError:
        s.close()
        return None
    return s, socket.AF_INET, ("127.0.0.1", port)


class _Coordinator:
    """Owns this worker's role (owner or client) and re-elects on owner loss."""

    def __init__(self, namespace: str, buffer_size: int):
        self._namespace = namespace
        self._buffer_size = buffer_size
        self._sock_path, self._addr_path = _paths(namespace)
        self._lock = threading.RLock()
        self._role: Optional[str] = None
        self._engine: Optional[StoreEngine] = None
        self._server: Optional[OwnerServer] = None
        self._family = None
        self._address = None
        self._token: Optional[str] = None

    @property
    def engine(self) -> Optional[StoreEngine]:
        return self._engine

    @property
    def token(self) -> Optional[str]:
        return self._token

    def ensure(self) -> None:
        if self._role is None:
            with self._lock:
                if self._role is None:
                    self._elect()

    def is_owner(self) -> bool:
        self.ensure()
        return self._role == "owner"

    def _elect(self) -> None:
        bound = _try_bind(self._namespace, self._sock_path)
        if bound:
            listen_sock, family, address = bound
            token = secrets.token_hex(16)
            _write_advertisement(self._addr_path, family, address, token)
            engine = StoreEngine(self._buffer_size)
            server = OwnerServer(engine, listen_sock, token)
            server.start()
            self._engine, self._server = engine, server
            self._family, self._address, self._token = family, address, token
            self._role = "owner"
            # Best-effort cleanup of the socket/advertisement on clean exit; a
            # crash leaves them stale, which the next election self-heals.
            atexit.register(self.close)
        else:
            self._family, self._address, self._token = _read_advertisement(
                self._addr_path
            )
            self._role = "client"

    def connect(self) -> socket.socket:
        self.ensure()
        return connect_to_owner(self._family, self._address, self._token)

    def on_owner_lost(self) -> None:
        """The owner became unreachable; re-elect (may promote us to owner)."""
        with self._lock:
            if self._role == "owner":
                return
            self._role = None
            self._elect()

    def close(self) -> None:
        with self._lock:
            if self._server is not None:
                self._server.close()
                for path in (self._sock_path, self._addr_path):
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
            self._role = None


class _LocalSubscription(Subscription):
    """A topic view that reads from the owner engine directly (owner role) or
    long-polls it over a dedicated connection (client role), resuming from its
    cursor on reconnect so no buffered message is missed.
    """

    def __init__(self, coord: _Coordinator, topic: str, start_seq: int):
        self._coord = coord
        self._topic = topic
        self._cursor = start_seq
        self._conn: Optional[socket.socket] = None
        self._closed = threading.Event()

    def close(self) -> None:
        self._closed.set()
        conn, self._conn = self._conn, None
        if conn is not None:
            try:
                conn.close()
            except OSError:
                pass

    def _poll_once(self) -> PollResult:
        if self._coord.is_owner():
            engine = self._coord.engine
            assert engine is not None
            return engine.poll(self._topic, self._cursor, _OWNER_POLL_TIMEOUT)
        return self._client_poll()

    def _client_poll(self) -> PollResult:
        for attempt in range(4):
            if self._closed.is_set():
                return PollResult([], self._cursor, False)
            if self._conn is None:
                prev_token = self._coord.token
                try:
                    self._conn = self._coord.connect()
                except OSError as exc:
                    # Owner unreachable: brief retries to the same owner, then
                    # re-elect. A changed owner means its buffer is gone -> gap.
                    if attempt >= 2:
                        self._coord.on_owner_lost()
                        if self._coord.token != prev_token:
                            raise SharedStorageGap(
                                "shared-storage owner changed; buffered "
                                "messages were lost"
                            ) from exc
                    time.sleep(0.1 * (attempt + 1))
                    continue
            try:
                send_frame(
                    self._conn,
                    ["poll", self._topic, self._cursor, _CLIENT_POLL_TIMEOUT],
                )
                resp = recv_frame(self._conn)
                if resp is EOF:
                    raise ConnectionError("owner closed the connection")
                status, val = resp
                if status == "err":
                    raise SharedStorageError(val)
                return PollResult(*val)
            except (OSError, EOFError, ConnectionError):
                if self._conn is not None:
                    try:
                        self._conn.close()
                    except OSError:
                        pass
                self._conn = None  # reconnect on the next attempt
        return PollResult([], self._cursor, False)

    def __iter__(self):
        try:
            while not self._closed.is_set():
                res = self._poll_once()
                if res.gap:
                    raise SharedStorageGap(
                        f"replay buffer overran on topic {self._topic!r}"
                    )
                yield from res.messages
                self._cursor = res.last_seq
        finally:
            self.close()

    def __aiter__(self):
        return self._aiter()

    async def _aiter(self):
        loop = asyncio.get_running_loop()
        try:
            while not self._closed.is_set():
                try:
                    res = await loop.run_in_executor(None, self._poll_once)
                except RuntimeError:
                    # The loop/executor is shutting down (client disconnected or
                    # the app is stopping) -- end the subscription cleanly.
                    break
                if res.gap:
                    raise SharedStorageGap(
                        f"replay buffer overran on topic {self._topic!r}"
                    )
                for message in res.messages:
                    yield message
                self._cursor = res.last_seq
        finally:
            self.close()


class LocalSharedStorage(BaseSharedStorage):
    """In-memory shared storage, elected to a single owner process per machine.

    Values and published messages must be JSON-compatible. State is not durable:
    if the owning process dies, a survivor re-elects with an empty store.
    """

    def __init__(
        self, namespace: Optional[str] = None, buffer_size: int = DEFAULT_BUFFER
    ):
        self._coord = _Coordinator(namespace or _default_namespace(), buffer_size)
        self._conn: Optional[socket.socket] = None
        self._conn_lock = threading.Lock()

    def start(self) -> None:
        self._coord.ensure()

    def close(self) -> None:
        with self._conn_lock:
            if self._conn is not None:
                try:
                    self._conn.close()
                except OSError:
                    pass
                self._conn = None
        self._coord.close()

    # --- key/value + publish (short request/response) ----------------------
    def _call(self, req):
        last_err: Optional[Exception] = None
        for _ in range(3):
            if self._coord.is_owner():
                return self._local(req)
            try:
                return self._remote(req)
            except (OSError, EOFError, ConnectionError) as err:
                last_err = err
                self._coord.on_owner_lost()
        raise SharedStorageError(f"shared-storage owner unreachable: {last_err}")

    def _local(self, req):
        engine = self._coord.engine
        assert engine is not None
        op = req[0]
        if op == "get":
            return engine.get(req[1], req[2])
        if op == "set":
            return engine.set(req[1], req[2])
        if op == "delete":
            return engine.delete(req[1])
        if op == "publish":
            return engine.publish(req[1], req[2])
        if op == "head":
            return engine.head_seq(req[1])
        raise ValueError(f"unknown op {op!r}")

    def _remote(self, req):
        with self._conn_lock:
            if self._conn is None:
                self._conn = self._coord.connect()
            try:
                send_frame(self._conn, req)
                resp = recv_frame(self._conn)
                if resp is EOF:
                    raise ConnectionError("owner closed the connection")
            except (OSError, EOFError, ConnectionError):
                try:
                    self._conn.close()
                except OSError:
                    pass
                self._conn = None
                raise
        status, val = resp
        if status == "err":
            raise SharedStorageError(val)
        return val

    def get(self, key: str, default: Any = None) -> Any:
        return self._call(["get", key, default])

    def set(self, key: str, value: Any) -> None:
        self._call(["set", key, value])

    def delete(self, key: str) -> None:
        self._call(["delete", key])

    def publish(self, topic: str, message: Any) -> None:
        self._call(["publish", topic, message])

    def _head(self, topic: str) -> int:
        return self._call(["head", topic])

    def subscribe(self, topic: str, replay_from: Optional[int] = None) -> Subscription:
        self._coord.ensure()
        start = replay_from if replay_from is not None else self._head(topic)
        return _LocalSubscription(self._coord, topic, start)
