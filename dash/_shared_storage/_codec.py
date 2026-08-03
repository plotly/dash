"""Codec for the shared-storage socket transport.

Uses ``msgspec`` (msgpack: fast, compact), a hard dependency of Dash. The
format is data-only, so bytes read off the socket cannot execute code.

Payloads must be JSON-compatible (dict / list / str / int / float / bool /
None) -- the same constraint as ``dcc.Store`` and callback outputs.
"""

from typing import Any

import msgspec

_encoder = msgspec.msgpack.Encoder()
_decoder = msgspec.msgpack.Decoder()


def encode(obj: Any) -> bytes:
    return _encoder.encode(obj)


def decode(data: bytes) -> Any:
    return _decoder.decode(data)
