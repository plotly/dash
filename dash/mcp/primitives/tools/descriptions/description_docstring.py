"""Callback docstring for tool descriptions."""

from __future__ import annotations

from typing import Any


def callback_docstring(
    outputs: list[dict[str, Any]],
    docstring: str | None = None,
) -> list[str]:
    """Return the callback's docstring as description lines."""
    if docstring:
        return ["", docstring.strip()]
    return []
