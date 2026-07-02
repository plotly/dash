import pytest

from dash.exceptions import WebSocketCallbackError
from dash._validate import validate_websocket_callback_request


class TestWebsocketCallbackRequestValidation:
    """Tests for runtime WebSocket callback request validation."""

    def test_global_enabled_allows_any_callback(self):
        """When websocket_callbacks=True globally, any callback can use WebSocket."""
        callback_map = {
            "out1.children": {"websocket": False},
            "out2.children": {},  # no websocket key
        }
        # Should not raise - global setting allows all
        validate_websocket_callback_request("out1.children", callback_map, True)
        validate_websocket_callback_request("out2.children", callback_map, True)

    def test_per_callback_websocket_enabled_passes(self):
        """Callback with websocket=True should pass when global is False."""
        callback_map = {
            "out1.children": {"websocket": True},
        }
        # Should not raise
        validate_websocket_callback_request("out1.children", callback_map, False)

    def test_per_callback_websocket_disabled_raises(self):
        """Callback without websocket=True should raise when global is False."""
        callback_map = {
            "out1.children": {"websocket": False},
        }

        with pytest.raises(WebSocketCallbackError) as exc_info:
            validate_websocket_callback_request("out1.children", callback_map, False)

        assert "out1.children" in str(exc_info.value)
        assert "websocket=True" in str(exc_info.value)

    def test_callback_without_websocket_key_raises(self):
        """Callback without websocket key should raise when global is False."""
        callback_map = {
            "out1.children": {},  # no websocket key
        }

        with pytest.raises(WebSocketCallbackError) as exc_info:
            validate_websocket_callback_request("out1.children", callback_map, False)

        assert "out1.children" in str(exc_info.value)

    def test_unknown_callback_raises(self):
        """Unknown callback ID should raise when global is False."""
        callback_map = {}

        with pytest.raises(WebSocketCallbackError) as exc_info:
            validate_websocket_callback_request("unknown.children", callback_map, False)

        assert "unknown.children" in str(exc_info.value)
