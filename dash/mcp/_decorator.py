"""Decorator to expose plain Python functions as MCP tools."""

from __future__ import annotations

import functools
from typing import Any, Callable, Optional

from typing_extensions import TypedDict


class MCPToolRegistration(TypedDict):
    fn: Callable[..., Any]
    expose_docstring: Optional[bool]


MCP_DECORATED_FUNCTIONS: dict[str, MCPToolRegistration] = {}


def mcp_enabled(
    func: Callable[..., Any] | None = None,
    *,
    name: str | None = None,
    expose_docstring: Optional[bool] = None,
) -> Callable[..., Any]:
    """Mark a function as an MCP tool.

    Supports both bare and parameterised usage::

        @mcp_enabled
        def my_tool(x: int) -> str: ...

        @mcp_enabled(name="custom_name", expose_docstring=True)
        def my_tool(x: int) -> str: ...
    """

    def _wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
        tool_name = name if name else fn.__name__
        MCP_DECORATED_FUNCTIONS[tool_name] = MCPToolRegistration(
            fn=fn,
            expose_docstring=expose_docstring,
        )

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        return wrapper

    if func is not None:
        return _wrap(func)
    return _wrap
