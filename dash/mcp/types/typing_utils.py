"""Shared typing utilities for the MCP layer."""

from __future__ import annotations

import typing
from typing import Any


def is_nullable(annotation: Any) -> bool:
    """Check if a type annotation includes NoneType (is nullable/Optional)."""
    origin = getattr(annotation, "__origin__", None)
    args = getattr(annotation, "__args__", ())

    _is_union = origin is typing.Union
    if not _is_union:
        try:
            import types as _types  # pylint: disable=import-outside-toplevel

            if isinstance(annotation, _types.UnionType):
                _is_union = True
                args = annotation.__args__
        except AttributeError:
            pass

    if _is_union and args:
        return type(None) in args

    return False
