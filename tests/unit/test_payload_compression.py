"""
Unit tests for dash._compression.decompress_payload.
"""

import json
import base64
import zlib
import pytest

from dash._compression import decompress_payload, COMPRESSED_PAYLOAD_FIELD


def _compress(payload: dict) -> dict:
    """Helper: compress a dict and wrap it for decompress_payload."""
    compressed = zlib.compress(json.dumps(payload).encode())
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

    def test_empty_compressed_field_raises(self):
        with pytest.raises(ValueError):
            decompress_payload({COMPRESSED_PAYLOAD_FIELD: None})

    def test_invalid_base64_raises(self):
        with pytest.raises(ValueError):
            decompress_payload({COMPRESSED_PAYLOAD_FIELD: "not-valid-base64!@#"})

    def test_invalid_gzip_raises(self):
        with pytest.raises(ValueError):
            decompress_payload(
                {COMPRESSED_PAYLOAD_FIELD: base64.b64encode(b"not gzip").decode()}
            )
