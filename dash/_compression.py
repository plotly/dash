"""
Utilities for decompressing callback payloads.

Payload compression reduces network traffic for large callback requests,
particularly useful for callbacks with large data payloads.
"""

import base64
import json
import zlib
from typing import Any

COMPRESSED_PAYLOAD_FIELD = "__compressed_payload__"


def decompress_payload(request_body: dict[str, Any]) -> dict[str, Any]:
    """
    Decompress a callback request body if it was compressed.

    If the request body contains a ``__compressed_payload__`` field,
    this function decompresses the gzipped payload and returns the parsed JSON dictionary.

    If the request body is not compressed, it is returned as-is.

    Args:
        request_body: The parsed request body as a dictionary.

    Returns:
        The decompressed and parsed callback request dictionary.

    Raises:
        ValueError: If the compressed data is invalid or cannot be decompressed.
    """
    if COMPRESSED_PAYLOAD_FIELD not in request_body:
        # return the original request body if it does not contain the compressed payload marker
        return request_body

    # Extract and decode the compressed data
    compressed_data_b64_encoded = request_body.get(COMPRESSED_PAYLOAD_FIELD)
    if not compressed_data_b64_encoded:
        raise ValueError("Failed to decompress callback payload.")

    try:
        compressed_data_binary = base64.b64decode(compressed_data_b64_encoded)
        # fflate's gzipSync produces gzip format, so we need to signal to zlib that it's gzip by using 16 + MAX_WBITS
        decompressed_data_binary = zlib.decompress(compressed_data_binary, zlib.MAX_WBITS | 16)
        decompressed_body = json.loads(decompressed_data_binary.decode("utf-8"))

        return decompressed_body

    except Exception as e:
        raise ValueError(
            "Failed to decompress callback payload."
        ) from e
