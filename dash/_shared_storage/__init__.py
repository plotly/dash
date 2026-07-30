"""Backend-agnostic shared state + pub/sub (state manager).

Public surface grows as backends land. Today: the interface and the in-memory
engine; ``LocalSharedStorage`` (owner-elected, cross-process) and the Dash
wiring come next.
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
