"""
Utilities for decompressing callback payloads.

Payload compression reduces network traffic for large callback requests,
particularly useful for callbacks with large data payloads.
"""

import json
import os
import zlib
from typing import Any

# Maximum decompressed payload size is 64 MB by default
MAX_PAYLOAD_SIZE = int(os.getenv("DASH_MAX_PAYLOAD_SIZE_MB", "64")) * 1024 * 1024


def decompress_payload(data: bytes, max_size: int = MAX_PAYLOAD_SIZE) -> Any:
    """
    Decompress a gzip-compressed callback request body.

    The data is expected to be the raw bytes of a gzip-compressed UTF-8 JSON payload.

    Args:
        data: The raw compressed request body bytes.
        max_size: The maximum allowed size of the decompressed payload in bytes.

    Returns:
        The decompressed and parsed callback request dictionary.

    Raises:
        ValueError: If the data cannot be decompressed or parsed.
    """
    try:
        decompressor = zlib.decompressobj(zlib.MAX_WBITS | 16)
        decompressed = decompressor.decompress(data, max_size + 1)

        if len(decompressed) > max_size:
            raise ValueError("Decompressed callback payload is too large.")

        if not decompressor.eof:
            raise ValueError("Incomplete gzip callback payload.")

        if decompressor.unused_data:
            raise ValueError("Unexpected data after gzip callback payload.")

        return json.loads(decompressed.decode("utf-8"))
    except Exception as e:
        raise ValueError("Failed to decompress callback payload.") from e
