"""
Unit tests for dash._compression.decompress_payload.
"""

import base64
import json
import zlib

import pytest

from dash._compression import COMPRESSED_PAYLOAD_FIELD, decompress_payload


def _compress(payload: dict) -> dict:
    """Helper: compress a dict and wrap it for decompress_payload."""
    compressed = zlib.compress(json.dumps(payload).encode(), wbits=zlib.MAX_WBITS + 16)
    return {COMPRESSED_PAYLOAD_FIELD: base64.b64encode(compressed).decode()}


class TestDecompressPayload:
    def test_uncompressed_passthrough(self):
        payload = {"output": "out", "inputs": [], "changedPropIds": []}
        assert decompress_payload(payload) == payload

    def test_compressed_roundtrip(self):
        original = {
            "output": "out",
            "inputs": [{"id": "a", "property": "value", "value": "x"}],
            "changedPropIds": [],
        }
        assert decompress_payload(_compress(original)) == original

    @pytest.mark.parametrize(
        "compressed_payload",
        [None, "", "not-valid-base64!@#", base64.b64encode(b"not gzip").decode()],
    )
    def test_decompress_payload_raises(self, compressed_payload):
        payload = {COMPRESSED_PAYLOAD_FIELD: compressed_payload}
        with pytest.raises(ValueError):
            decompress_payload(payload)
