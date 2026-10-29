"""Codec for the shared-storage transport and the persistent backends.

Uses ``msgspec`` (msgpack: fast, compact) from the ``dash[shared_storage]``
extra, also part of ``dash[diskcache]`` and ``dash[redis]``. Without it, only
the in-memory transport works and it falls back to stdlib JSON; the backends
that write encoded bytes somewhere lasting (disk persistence, diskcache, Redis)
call :func:`require_msgspec` so the stored format never depends on what
happens to be installed. Both formats are
data-only, so bytes read off the socket cannot execute code.

Payloads must be JSON-compatible (dict / list / str / int / float / bool /
None) -- the same constraint as ``dcc.Store`` and callback outputs.
"""

import json
from typing import Any

try:
    import msgspec
except ImportError:
    msgspec = None  # type: ignore[assignment]

HAS_MSGSPEC = msgspec is not None

if msgspec is not None:
    # msgspec raises this on malformed input. It subclasses ``ValueError`` in
    # current msgspec but not in every version, so callers should catch it by
    # name.
    DecodeError: Any = msgspec.DecodeError
    _encoder = msgspec.msgpack.Encoder()
    _decoder = msgspec.msgpack.Decoder()

    def encode(obj: Any) -> bytes:
        return _encoder.encode(obj)

    def decode(data: bytes) -> Any:
        return _decoder.decode(data)

else:
    DecodeError = json.JSONDecodeError

    def encode(obj: Any) -> bytes:
        return json.dumps(obj, separators=(",", ":")).encode("utf-8")

    def decode(data: bytes) -> Any:
        return json.loads(data)


def require_msgspec(what: str, extra: str = "shared_storage") -> None:
    if not HAS_MSGSPEC:
        raise ImportError(
            f"{what} requires the {extra} extra:\n\n"
            f'    $ pip install "dash[{extra}]"\n'
        )
