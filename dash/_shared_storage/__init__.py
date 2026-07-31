"""Backend-agnostic shared state + pub/sub (state manager).

Exposes the ``BaseSharedStorage`` interface and the default
``LocalSharedStorage`` backend (owner-elected, cross-process).
"""

from .base import (
    BaseSharedStorage,
    SharedStorageError,
    SharedStorageGap,
    Subscription,
)
from .local import LocalSharedStorage

__all__ = [
    "BaseSharedStorage",
    "LocalSharedStorage",
    "SharedStorageError",
    "SharedStorageGap",
    "Subscription",
]
