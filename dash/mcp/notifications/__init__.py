"""Server-initiated MCP notifications."""

from .notification_tools_changed import broadcast_tools_changed

__all__ = [
    "broadcast_tools_changed",
]
