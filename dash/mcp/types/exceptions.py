"""MCP error types with JSON-RPC error codes."""

from __future__ import annotations


class MCPError(Exception):
    """Base MCP error carrying a JSON-RPC error code."""

    code = -32603

    def __init__(self, message: str):
        super().__init__(message)


class ToolNotFoundError(MCPError):
    """Tool name not found in the callback registry."""

    code = -32601


class InvalidParamsError(MCPError):
    """Invalid or missing parameters for a tool call."""

    code = -32602


class CallbackExecutionError(MCPError):
    """Callback raised an exception during execution."""

    pass
