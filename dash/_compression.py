"""Store compression managers for Dash callbacks.

This module provides compression managers that follow the same pattern as
BaseBackgroundCallbackManager, enabling callback-level compression for
Store components to reduce network payload sizes.
"""

from abc import ABC, abstractmethod
import base64
import json
import gzip
import zlib
import logging
from typing import Any, Dict, List, Union, Tuple

try:
    import brotli

    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

logger = logging.getLogger(__name__)


class BaseStoreCompressionManager(ABC):
    """
    Abstract base class for Store compression managers.
    """

    def __init__(
        self,
        level: int = 6,
        threshold: int = 1024,
        cache_enabled: bool = False,
        cache_size: int = 100,
    ):
        """Initialize compression manager.

        Args:
            level: Compression level (1-9, algorithm dependent)
            threshold: Minimum data size to compress (bytes)
            cache_enabled: Whether to cache compressed data
            cache_size: Maximum cache entries
        """
        self.level = self._validate_level(level)
        self.threshold = threshold
        self.cache_enabled = cache_enabled
        self.cache_size = cache_size
        self._cache: Dict[str, bytes] = {} if cache_enabled else None

    def _validate_level(self, level: int) -> int:
        """Validate compression level for this algorithm."""
        if not isinstance(level, int) or level < 1 or level > 9:
            raise ValueError(f"Compression level must be 1-9, got {level}")
        return level

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Return the algorithm name for payload metadata."""

    @abstractmethod
    def _compress_bytes(self, data: bytes) -> bytes:
        """Compress raw bytes using algorithm-specific method."""

    @abstractmethod
    def _decompress_bytes(self, data: bytes) -> bytes:
        """Decompress raw bytes using algorithm-specific method."""

    def should_compress(self, data: Any) -> bool:
        """Check if data meets compression threshold.

        Args:
            data: Data to potentially compress

        Returns:
            True if data should be compressed
        """
        if data is None:
            return False

        # Convert to JSON to estimate size
        try:
            json_str = json.dumps(data, default=str)
            return len(json_str.encode("utf-8")) >= self.threshold
        except (TypeError, ValueError):
            # If we can't serialize, don't compress
            return False

    def compress_store_data(self, data: Any) -> Union[Dict[str, Any], Any]:
        """Compress Store data with metadata for later decompression.

        Args:
            data: Python object to compress

        Returns:
            Compressed payload dict or original data if compression failed/skipped
        """
        try:
            # Check if we should compress
            if not self.should_compress(data):
                return data

            # Serialize to JSON
            json_str = json.dumps(data, default=str)
            json_bytes = json_str.encode("utf-8")
            original_size = len(json_bytes)

            # Check cache if enabled
            cache_key = None
            if self.cache_enabled:
                cache_key = self._make_cache_key(json_str)
                if cache_key in self._cache:
                    compressed_bytes = self._cache[cache_key]
                else:
                    compressed_bytes = self._compress_bytes(json_bytes)
                    self._update_cache(cache_key, compressed_bytes)
            else:
                compressed_bytes = self._compress_bytes(json_bytes)

            compressed_size = len(compressed_bytes)

            # Only return compressed if we actually saved space
            if compressed_size >= original_size:
                logger.debug(
                    "Compression ineffective: %d -> %d", original_size, compressed_size
                )
                return data

            # Return structured payload
            return {
                "compressed": True,
                "algorithm": self.algorithm_name,
                "level": self.level,
                "data": base64.b64encode(compressed_bytes).decode("ascii"),
                "original_size": original_size,
                "compressed_size": compressed_size,
            }

        except (TypeError, ValueError, OSError, UnicodeError) as e:
            # Graceful fallback on compression failure
            logger.warning("Store compression failed: %s", e)
            return data

    def decompress_store_data(self, payload: Any) -> Any:
        """Decompress Store data payload.

        Args:
            payload: Data that may be compressed payload or original data

        Returns:
            Decompressed Python object or original payload
        """
        # Check if this is a compressed payload
        if not self._is_compressed_payload(payload):
            return payload

        try:
            algorithm = payload["algorithm"]
            if algorithm != self.algorithm_name:
                logger.error(
                    "🚨 Algorithm mismatch: expected %s, got %s",
                    self.algorithm_name,
                    algorithm,
                )
                return payload

            # Decode and decompress
            compressed_bytes = base64.b64decode(payload["data"])
            json_bytes = self._decompress_bytes(compressed_bytes)
            json_str = json_bytes.decode("utf-8")

            return json.loads(json_str)

        except (TypeError, ValueError, OSError, UnicodeError, KeyError) as e:
            logger.error("🚨 Store decompression failed: %s", e)
            # Return original payload as fallback
            return payload

    def _is_compressed_payload(self, payload: Any) -> bool:
        """Check if payload is a compressed data structure."""
        return (
            isinstance(payload, dict)
            and payload.get("compressed") is True
            and "algorithm" in payload
            and "data" in payload
        )

    def _make_cache_key(self, json_str: str) -> str:
        """Generate cache key for JSON string."""
        import hashlib  # pylint: disable=import-outside-toplevel

        return hashlib.md5(json_str.encode("utf-8")).hexdigest()

    def _update_cache(self, key: str, compressed_bytes: bytes) -> None:
        """Update cache with LRU eviction."""
        if not self.cache_enabled:
            return

        # Simple LRU: remove oldest if at capacity
        if len(self._cache) >= self.cache_size:
            # Remove first (oldest) item
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[key] = compressed_bytes

    def compress_callback_outputs(
        self, output_value: Any, output_spec: List[Dict[str, Any]]
    ) -> Any:
        """Compress ALL Store outputs in this callback with same settings.

        Args:
            output_value: Callback return value (single value or tuple/list)
            output_spec: List of output specifications

        Returns:
            Processed output_value with Store data compressed
        """
        if not output_spec:
            return output_value

        # Handle single output
        if not isinstance(output_value, (list, tuple)):
            if self._is_store_output(output_spec[0]):
                return self.compress_store_data(output_value)
            return output_value

        # Handle multiple outputs
        processed_outputs = []
        for data, spec in zip(output_value, output_spec):
            if self._is_store_output(spec):
                processed_outputs.append(self.compress_store_data(data))
            else:
                processed_outputs.append(data)

        return type(output_value)(processed_outputs)

    def decompress_callback_inputs(
        self, func_args: Tuple[Any, ...], input_spec: List[Dict[str, Any]]
    ) -> Tuple[Any, ...]:
        """Decompress ALL Store inputs in this callback.

        Args:
            func_args: Function arguments tuple
            input_spec: List of input+state specifications

        Returns:
            Processed func_args with Store data decompressed
        """
        if not input_spec or not func_args:
            return func_args

        processed_args = []
        for arg, spec in zip(func_args, input_spec):
            if self._is_store_input(spec):
                processed_args.append(self.decompress_store_data(arg))
            else:
                processed_args.append(arg)

        return tuple(processed_args)

    def _is_store_output(self, output_spec: Dict[str, Any]) -> bool:
        """Check if output is a Store component data property."""
        return (
            output_spec.get("type") == "Store" and output_spec.get("property") == "data"
        )

    def _is_store_input(self, input_spec: Dict[str, Any]) -> bool:
        """Check if input is a Store component data property."""
        return (
            input_spec.get("type") == "Store" and input_spec.get("property") == "data"
        )


class GzipCompressionManager(BaseStoreCompressionManager):
    """Gzip compression manager for Store components.

    Provides good balance of compression ratio and speed.
    Most widely supported compression algorithm.
    """

    @property
    def algorithm_name(self) -> str:
        return "gzip"

    def _compress_bytes(self, data: bytes) -> bytes:
        """Compress using gzip algorithm."""
        return gzip.compress(data, compresslevel=self.level)

    def _decompress_bytes(self, data: bytes) -> bytes:
        """Decompress using gzip algorithm."""
        return gzip.decompress(data)


class DeflateCompressionManager(BaseStoreCompressionManager):
    """Deflate compression manager for Store components.

    Faster than gzip with slightly less compression.
    Good for real-time applications where speed matters.
    """

    @property
    def algorithm_name(self) -> str:
        return "deflate"

    def _compress_bytes(self, data: bytes) -> bytes:
        """Compress using deflate algorithm."""
        return zlib.compress(data, level=self.level)

    def _decompress_bytes(self, data: bytes) -> bytes:
        """Decompress using deflate algorithm."""
        return zlib.decompress(data)


class BrotliCompressionManager(BaseStoreCompressionManager):
    """Brotli compression manager for Store components.

    Best compression ratio but slower than gzip/deflate.
    Ideal for large datasets where compression ratio is most important.
    """

    def __init__(self, *args, **kwargs):
        if not BROTLI_AVAILABLE:
            raise ImportError(
                "Brotli compression requires the 'brotli' package. "
                "Install with: pip install brotli"
            )
        super().__init__(*args, **kwargs)

    @property
    def algorithm_name(self) -> str:
        return "brotli"

    def _validate_level(self, level: int) -> int:
        """Validate brotli compression level (0-11)."""
        if not isinstance(level, int) or level < 0 or level > 11:
            raise ValueError(f"Brotli compression level must be 0-11, got {level}")
        return level

    def _compress_bytes(self, data: bytes) -> bytes:
        """Compress using brotli algorithm."""
        return brotli.compress(data, quality=self.level)

    def _decompress_bytes(self, data: bytes) -> bytes:
        """Decompress using brotli algorithm."""
        return brotli.decompress(data)


# Convenience alias - most common manager
StoreCompressionManager = GzipCompressionManager
