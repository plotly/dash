"""
Utilities for decompressing callback payloads.

Payload compression reduces network traffic for large callback requests,
particularly useful for callbacks with large data payloads.
"""

import json
import zlib
from typing import Any


def decompress_payload(data: bytes) -> Any:
    """
    Decompress a gzip-compressed callback request body.

    The data is expected to be the raw bytes of a gzip-compressed UTF-8 JSON payload,
    as produced by fflate's ``gzipSync`` on the client side.

    Args:
        data: The raw compressed request body bytes.

    Returns:
        The decompressed and parsed callback request dictionary.

    Raises:
        ValueError: If the data cannot be decompressed or parsed.
    """
    try:
        # fflate's gzipSync produces gzip format; use 16 + MAX_WBITS to signal gzip
        decompressed = zlib.decompress(data, zlib.MAX_WBITS | 16)
        return json.loads(decompressed.decode("utf-8"))
    except Exception as e:
        raise ValueError("Failed to decompress callback payload.") from e
