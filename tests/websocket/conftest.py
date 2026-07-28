import pytest
from dash import hooks


@pytest.fixture
def ws_hook_cleanup():
    """Clean up WebSocket hooks after each test."""
    yield
    hooks._ns["websocket_connect"] = []
    hooks._ns["websocket_message"] = []
    hooks._finals.pop("websocket_connect", None)
    hooks._finals.pop("websocket_message", None)
