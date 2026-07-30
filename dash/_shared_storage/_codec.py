"""Wire codec for the shared-storage socket transport.

Prefers ``msgspec`` (msgpack: fast, compact) and falls back to stdlib ``json``.
Both are **data-only -- never pickle** -- so bytes read off the socket cannot
execute code. All workers in one deployment share a single install, hence a
single codec, so the two ends always agree on the format.

Payloads must be JSON-compatible (dict / list / str / int / float / bool /
None) under either codec -- the same constraint as ``dcc.Store`` and callback
outputs.
"""

from typing import Any

try:
    import msgspec

    _encoder = msgspec.msgpack.Encoder()
    _decoder = msgspec.msgpack.Decoder()

    def encode(obj: Any) -> bytes:
        return _encoder.encode(obj)

    def decode(data: bytes) -> Any:
        return _decoder.decode(data)

    CODEC = "msgpack"
except ImportError:  # pragma: no cover - exercised via the fallback install
    import json

    def encode(obj: Any) -> bytes:
        return json.dumps(obj).encode("utf-8")

    def decode(data: bytes) -> Any:
        return json.loads(data.decode("utf-8"))

    CODEC = "json"
