"""Socket transport for the owner-elected shared store.

A single owner process serves one :class:`StoreEngine` over a stream socket
(AF_UNIX where available, TCP loopback otherwise). Messages are length-prefixed:
a 4-byte big-endian length followed by a body encoded by ``_codec`` (msgspec
msgpack). The codec is data-only -- the socket is
localhost-only, but deserializing untrusted bytes off a socket is a
remote-code-execution hazard, so the transport carries only data. The channel is
additionally gated by a per-owner random token; only same-host clients that read
the owner's advertisement file (written 0600) can attach.

The consequence is that stored values and published messages must be
JSON-serializable -- the same constraint as ``dcc.Store`` and callback outputs.

Requests are ``[op, *args]`` lists; responses are ``["ok", value]`` or
``["err", repr]``. Ops: get/set/delete/publish/head/poll -- a thin passthrough
to the engine. ``poll`` blocks server-side up to its timeout (one thread per
connection), which is what makes long-poll subscriptions cheap.
"""

import socket
import struct
import threading
from typing import Any, Optional

from ._codec import decode, encode

EOF = object()  # returned by recv_frame on a clean close
OK = ["ok", None]


def send_frame(sock: socket.socket, obj: Any) -> None:
    data = encode(obj)
    sock.sendall(struct.pack("!I", len(data)) + data)


def _recv_exactly(sock: socket.socket, n: int) -> Optional[bytes]:
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_frame(sock: socket.socket) -> Any:
    header = _recv_exactly(sock, 4)
    if header is None:
        return EOF
    (length,) = struct.unpack("!I", header)
    body = _recv_exactly(sock, length)
    if body is None:
        return EOF
    return decode(body)


class OwnerServer:
    """Serves one StoreEngine to client workers over ``listen_sock``."""

    def __init__(self, engine, listen_sock: socket.socket, token: str):
        self._engine = engine
        self._sock = listen_sock
        self._token = token
        self._closed = threading.Event()
        self._accept_thread = threading.Thread(
            target=self._accept_loop, name="dash-shared-owner", daemon=True
        )

    def start(self) -> None:
        self._sock.listen(128)
        self._accept_thread.start()

    def _accept_loop(self) -> None:
        while not self._closed.is_set():
            try:
                conn, _ = self._sock.accept()
            except OSError:
                break
            threading.Thread(target=self._handle, args=(conn,), daemon=True).start()

    def _handle(self, conn: socket.socket) -> None:
        try:
            if recv_frame(conn) != self._token:
                return
            send_frame(conn, OK)
            while not self._closed.is_set():
                req = recv_frame(conn)
                if req is EOF:
                    break
                send_frame(conn, self._dispatch(req))
        except (OSError, EOFError, ValueError):
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def _dispatch(self, req):  # pylint: disable=too-many-return-statements
        op = req[0]
        try:
            if op == "get":
                return ("ok", self._engine.get(req[1], req[2]))
            if op == "set":
                self._engine.set(req[1], req[2])
                return ("ok", None)
            if op == "delete":
                self._engine.delete(req[1])
                return ("ok", None)
            if op == "publish":
                return ("ok", self._engine.publish(req[1], req[2]))
            if op == "head":
                return ("ok", self._engine.head_seq(req[1]))
            if op == "poll":
                return ("ok", self._engine.poll(req[1], req[2], req[3]))
            return ("err", f"unknown op {op!r}")
        except Exception as err:  # pylint: disable=broad-exception-caught
            return ("err", repr(err))

    def close(self) -> None:
        self._closed.set()
        try:
            self._sock.close()
        except OSError:
            pass
        self._engine.close()


def connect_to_owner(family: int, address, token: str, timeout: float = 5.0):
    """Open a client connection and complete the token handshake."""
    sock = socket.socket(family, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(address)
    send_frame(sock, token)
    if recv_frame(sock) != OK:
        sock.close()
        raise ConnectionError("shared-storage owner rejected the handshake")
    sock.settimeout(None)
    return sock
