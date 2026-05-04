"""Dash MCP (Model Context Protocol) server integration."""

from dash.mcp._decorator import mcp_enabled
from dash.mcp._server import enable_mcp_server

__all__ = [
    "enable_mcp_server",
    "mcp_enabled",
]
