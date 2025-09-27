"""Unit tests for Store compression managers."""

import pytest
import json
import base64

from dash._compression import (
    BaseStoreCompressionManager,
    GzipCompressionManager,
    DeflateCompressionManager,
    BrotliCompressionManager,
    StoreCompressionManager,
    get_compression_manager_from_kwargs,
)


class TestCompressionManagerCreation:
    """Test compression manager instantiation and configuration."""

    def test_gzip_manager_creation(self):
        """Test GzipCompressionManager can be created with default settings."""
        manager = GzipCompressionManager()
        assert manager.algorithm_name == "gzip"
        assert manager.level == 6
        assert manager.threshold == 0

    def test_deflate_manager_creation(self):
        """Test DeflateCompressionManager can be created with default settings."""
        manager = DeflateCompressionManager()
        assert manager.algorithm_name == "deflate"
        assert manager.level == 6
        assert manager.threshold == 0

    def test_brotli_manager_creation(self):
        """Test BrotliCompressionManager creation (if brotli available)."""
        try:
            manager = BrotliCompressionManager()
            assert manager.algorithm_name == "brotli"
            assert manager.level == 6
            assert manager.threshold == 0
        except ImportError:
            # Brotli not available, this is expected behavior
            with pytest.raises(ImportError, match="Brotli compression requires"):
                BrotliCompressionManager()

    def test_custom_parameters(self):
        """Test compression managers with custom parameters."""
        manager = GzipCompressionManager(level=9, threshold=2048)
        assert manager.level == 9
        assert manager.threshold == 2048

    def test_level_validation(self):
        """Test compression level validation."""
        # Valid levels
        GzipCompressionManager(level=1)
        GzipCompressionManager(level=9)

        # Invalid levels
        with pytest.raises(ValueError, match="Compression level must be 1-9"):
            GzipCompressionManager(level=0)
        with pytest.raises(ValueError, match="Compression level must be 1-9"):
            GzipCompressionManager(level=10)

    def test_brotli_level_validation(self):
        """Test brotli-specific level validation (0-11)."""
        try:
            # Valid brotli levels
            BrotliCompressionManager(level=0)
            BrotliCompressionManager(level=11)

            # Invalid brotli levels
            with pytest.raises(ValueError, match="Brotli compression level must be 0-11"):
                BrotliCompressionManager(level=12)
        except ImportError:
            # Brotli not available, skip test
            pytest.skip("Brotli not available")

    def test_convenience_alias(self):
        """Test that StoreCompressionManager is an alias for GzipCompressionManager."""
        manager = StoreCompressionManager()
        assert isinstance(manager, GzipCompressionManager)
        assert manager.algorithm_name == "gzip"


class TestCompressionThreshold:
    """Test compression threshold behavior."""

    def test_should_compress_none(self):
        """Test that None data is not compressed."""
        manager = GzipCompressionManager()
        assert not manager.should_compress(None)

    def test_should_compress_small_data(self):
        """Test that small data below threshold is not compressed."""
        manager = GzipCompressionManager(threshold=1000)
        small_data = {"key": "value"}  # Much smaller than 1000 bytes
        assert not manager.should_compress(small_data)

    def test_should_compress_large_data(self):
        """Test that large data above threshold is compressed."""
        manager = GzipCompressionManager(threshold=100)
        large_data = {"key": "x" * 200}  # Larger than 100 bytes when JSON serialized
        assert manager.should_compress(large_data)

    def test_should_compress_unserializable(self):
        """Test that unserializable data is not compressed."""
        manager = GzipCompressionManager()

        class UnserializableClass:
            pass

        unserializable = UnserializableClass()
        assert not manager.should_compress(unserializable)


class TestCompressionRoundTrip:
    """Test compression and decompression round-trip behavior."""

    @pytest.mark.parametrize("manager_class", [GzipCompressionManager, DeflateCompressionManager])
    def test_basic_round_trip(self, manager_class):
        """Test basic compression/decompression round trip."""
        manager = manager_class(threshold=10)  # Low threshold to ensure compression

        # Create data large enough to ensure compression
        original_data = {
            "numbers": list(range(100)),  # Much larger dataset
            "text": "Hello, world! " * 50,  # Repeat text to make it larger
            "nested": {"key": "value" * 20, "count": 42}
        }

        # Compress
        compressed = manager.compress_store_data(original_data)

        # Should return compressed payload
        assert isinstance(compressed, dict)
        assert compressed.get("compressed") is True
        assert "algorithm" in compressed
        assert "data" in compressed
        assert "original_size" in compressed
        assert "compressed_size" in compressed

        # Decompress
        decompressed = manager.decompress_store_data(compressed)

        # Should match original
        assert decompressed == original_data

    def test_brotli_round_trip(self):
        """Test brotli compression round trip (if available)."""
        try:
            manager = BrotliCompressionManager(threshold=10)

            original_data = {"test": "data" * 50}  # Ensure it's above threshold

            compressed = manager.compress_store_data(original_data)
            assert compressed.get("algorithm") == "brotli"

            decompressed = manager.decompress_store_data(compressed)
            assert decompressed == original_data

        except ImportError:
            pytest.skip("Brotli not available")

    def test_compression_effectiveness(self):
        """Test that compression actually reduces size for compressible data."""
        manager = GzipCompressionManager(threshold=10)

        # Highly repetitive data should compress well
        repetitive_data = {"repeated": "A" * 1000}

        compressed = manager.compress_store_data(repetitive_data)

        assert compressed.get("compressed") is True
        assert compressed["compressed_size"] < compressed["original_size"]

    def test_incompressible_data_fallback(self):
        """Test fallback when compression doesn't reduce size."""
        manager = GzipCompressionManager(threshold=10)

        # Create data that might not compress well
        # Note: This test might be flaky as gzip can compress almost anything
        # We're testing the logic path, even if compression is usually effective
        small_random_data = {"x": 42}

        result = manager.compress_store_data(small_random_data)

        # Either compressed or original data should be returned
        if isinstance(result, dict) and result.get("compressed"):
            # Was compressed
            assert "algorithm" in result
        else:
            # Fell back to original
            assert result == small_random_data


class TestCompressionErrorHandling:
    """Test error handling and graceful fallbacks."""

    def test_compression_error_fallback(self):
        """Test graceful fallback when compression fails."""
        manager = GzipCompressionManager(threshold=10)

        # Mock a compression failure by overriding _compress_bytes
        original_compress = manager._compress_bytes
        def failing_compress(data):
            raise OSError("Compression failed")
        manager._compress_bytes = failing_compress

        data = {"test": "data" * 50}
        result = manager.compress_store_data(data)

        # Should fall back to original data
        assert result == data

        # Restore original method
        manager._compress_bytes = original_compress

    def test_decompression_error_fallback(self):
        """Test graceful fallback when decompression fails."""
        manager = GzipCompressionManager()

        # Create invalid compressed payload
        invalid_payload = {
            "compressed": True,
            "algorithm": "gzip",
            "data": "invalid_base64_data!!!",
            "original_size": 100,
            "compressed_size": 50
        }

        result = manager.decompress_store_data(invalid_payload)

        # Should fall back to original payload
        assert result == invalid_payload

    def test_algorithm_mismatch_fallback(self):
        """Test fallback when algorithm doesn't match."""
        gzip_manager = GzipCompressionManager()

        # Create payload with different algorithm
        mismatched_payload = {
            "compressed": True,
            "algorithm": "deflate",  # Wrong algorithm
            "data": base64.b64encode(b"test").decode("ascii"),
            "original_size": 100,
            "compressed_size": 50
        }

        result = gzip_manager.decompress_store_data(mismatched_payload)

        # Should fall back to original payload
        assert result == mismatched_payload

    def test_non_compressed_payload_passthrough(self):
        """Test that non-compressed data passes through unchanged."""
        manager = GzipCompressionManager()

        regular_data = {"normal": "data"}
        result = manager.decompress_store_data(regular_data)

        assert result == regular_data


class TestCallbackIntegration:
    """Test callback-level compression and decompression methods."""

    def test_compress_callback_outputs_single(self):
        """Test compressing single callback output."""
        manager = GzipCompressionManager(threshold=10)

        output_value = {"large": "data" * 100}
        output_spec = [{"type": "Store", "property": "data"}]

        result = manager.compress_callback_outputs(output_value, output_spec)

        # Should be compressed
        assert isinstance(result, dict)
        assert result.get("compressed") is True

    def test_compress_callback_outputs_multiple(self):
        """Test compressing multiple callback outputs."""
        manager = GzipCompressionManager(threshold=10)

        output_value = [
            {"store": "data" * 100},  # Should be compressed
            {"graph": "figure_data"}  # Should not be compressed (not Store)
        ]
        output_spec = [
            {"type": "Store", "property": "data"},
            {"type": "Graph", "property": "figure"}
        ]

        result = manager.compress_callback_outputs(output_value, output_spec)

        assert isinstance(result, list)
        assert len(result) == 2

        # First should be compressed (Store)
        assert isinstance(result[0], dict)
        assert result[0].get("compressed") is True

        # Second should be unchanged (not Store)
        assert result[1] == {"graph": "figure_data"}

    def test_decompress_callback_inputs(self):
        """Test decompressing callback inputs."""
        manager = GzipCompressionManager(threshold=10)

        # Create compressed data
        original_data = {"input": "data" * 100}
        compressed_data = manager.compress_store_data(original_data)

        func_args = (compressed_data, "other_arg")
        input_spec = [
            {"type": "Store", "property": "data"},
            {"type": "Input", "property": "value"}
        ]

        result = manager.decompress_callback_inputs(func_args, input_spec)

        assert isinstance(result, tuple)
        assert len(result) == 2

        # First should be decompressed
        assert result[0] == original_data

        # Second should be unchanged
        assert result[1] == "other_arg"

    def test_non_store_components_ignored(self):
        """Test that non-Store components are ignored during compression."""
        manager = GzipCompressionManager(threshold=10)

        output_value = [
            {"data": "value1"},
            {"data": "value2"}
        ]
        output_spec = [
            {"type": "Input", "property": "value"},
            {"type": "Div", "property": "children"}
        ]

        result = manager.compress_callback_outputs(output_value, output_spec)

        # Should be unchanged since no Store components
        assert result == output_value


class TestKwargsHelperFunction:
    """Test the get_compression_manager_from_kwargs helper function."""

    def test_get_manager_from_kwargs_present(self):
        """Test extracting compression manager when present in kwargs."""
        manager = GzipCompressionManager()
        kwargs = {"compression_manager": manager, "other_param": "value"}

        result = get_compression_manager_from_kwargs(kwargs)
        assert result is manager

    def test_get_manager_from_kwargs_absent(self):
        """Test extracting compression manager when not present in kwargs."""
        kwargs = {"other_param": "value"}

        result = get_compression_manager_from_kwargs(kwargs)
        assert result is None

    def test_get_manager_from_kwargs_empty(self):
        """Test extracting compression manager from empty kwargs."""
        kwargs = {}

        result = get_compression_manager_from_kwargs(kwargs)
        assert result is None


class TestStoreComponentDetection:
    """Test Store component detection logic."""

    def test_is_store_output_positive(self):
        """Test detecting Store output components."""
        manager = GzipCompressionManager()

        store_spec = {"type": "Store", "property": "data"}
        assert manager._is_store_output(store_spec)

    def test_is_store_output_negative(self):
        """Test rejecting non-Store output components."""
        manager = GzipCompressionManager()

        non_store_specs = [
            {"type": "Input", "property": "value"},
            {"type": "Store", "property": "clear_data"},  # Wrong property
            {"type": "Div", "property": "children"}
        ]

        for spec in non_store_specs:
            assert not manager._is_store_output(spec)

    def test_is_store_input_positive(self):
        """Test detecting Store input components."""
        manager = GzipCompressionManager()

        store_spec = {"type": "Store", "property": "data"}
        assert manager._is_store_input(store_spec)

    def test_is_store_input_negative(self):
        """Test rejecting non-Store input components."""
        manager = GzipCompressionManager()

        non_store_specs = [
            {"type": "Input", "property": "value"},
            {"type": "Store", "property": "modified_timestamp"},  # Wrong property
            {"type": "State", "property": "data"}
        ]

        for spec in non_store_specs:
            assert not manager._is_store_input(spec)


class TestCompressionPayloadStructure:
    """Test the structure of compressed payloads."""

    def test_compressed_payload_structure(self):
        """Test that compressed payloads have the expected structure."""
        manager = GzipCompressionManager(threshold=10)

        data = {"test": "data" * 100}
        compressed = manager.compress_store_data(data)

        # Check required fields
        required_fields = ["compressed", "algorithm", "level", "data", "original_size", "compressed_size"]
        for field in required_fields:
            assert field in compressed

        # Check field types and values
        assert compressed["compressed"] is True
        assert isinstance(compressed["algorithm"], str)
        assert isinstance(compressed["level"], int)
        assert isinstance(compressed["data"], str)  # Base64 encoded
        assert isinstance(compressed["original_size"], int)
        assert isinstance(compressed["compressed_size"], int)

        # Check that base64 data is valid
        try:
            base64.b64decode(compressed["data"])
        except Exception:
            pytest.fail("Invalid base64 data in compressed payload")

    def test_is_compressed_payload_detection(self):
        """Test detection of compressed vs uncompressed payloads."""
        manager = GzipCompressionManager()

        # Valid compressed payload
        compressed_payload = {
            "compressed": True,
            "algorithm": "gzip",
            "data": "eJzLSM3JyVcozy/KSVEEABxJBD4=",
            "original_size": 20,
            "compressed_size": 15
        }
        assert manager._is_compressed_payload(compressed_payload)

        # Invalid payloads
        invalid_payloads = [
            {"compressed": False, "algorithm": "gzip", "data": "test"},
            {"algorithm": "gzip", "data": "test"},  # Missing compressed field
            {"compressed": True, "data": "test"},   # Missing algorithm
            {"compressed": True, "algorithm": "gzip"},  # Missing data
            "not_a_dict",
            None,
            {"regular": "data"}
        ]

        for payload in invalid_payloads:
            assert not manager._is_compressed_payload(payload)