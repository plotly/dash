"""Dash MCP (Model Context Protocol) server integration."""

from dash.mcp._configure import configure_mcp_server
from dash.mcp._decorator import mcp_enabled
from dash.mcp._server import enable_mcp_server

__all__ = [
    "configure_mcp_server",
    "enable_mcp_server",
    "mcp_enabled",
]
