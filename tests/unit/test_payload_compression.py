"""
Unit tests for dash._compression.decompress_payload.
"""

import json
import gzip

import pytest

from dash._compression import decompress_payload


def _gzip(payload: dict) -> bytes:
    """Helper: gzip-compress a dict to raw bytes."""
    return gzip.compress(json.dumps(payload).encode())


class TestDecompressPayload:
    def test_compressed_roundtrip(self):
        original = {
            "output": "out",
            "inputs": [{"id": "a", "property": "value", "value": "x"}],
            "changedPropIds": [],
        }
        assert decompress_payload(_gzip(original)) == original

    def test_decompressed_payload_exceeds_size_limit(self):
        payload = {"value": "x" * 1_000}

        large_compressed_payload = _gzip(payload)
        with pytest.raises(ValueError):
            decompress_payload(large_compressed_payload, max_size=100)

    @pytest.mark.parametrize(
        "bad_data",
        [b"", b"not gzip at all", b"\x1f\x8b\x00truncated"],
    )
    def test_decompress_invalid_raises(self, bad_data):
        with pytest.raises(ValueError):
            decompress_payload(bad_data)

    def test_decompress_valid_gzip_invalid_json_raises(self):
        bad_json = gzip.compress(b"not json")
        with pytest.raises(ValueError):
            decompress_payload(bad_json)
