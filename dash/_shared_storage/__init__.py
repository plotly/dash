"""Backend-agnostic shared state + pub/sub (state manager).

Exposes the ``BaseSharedStorage`` interface and its backends:

- ``LocalSharedStorage`` (default): in-memory, owner-elected -- one container.
- ``DiskcacheSharedStorage``: on a ``diskcache.Cache`` -- one machine, not pods.
- ``RedisSharedStorage``: on Redis -- across processes and containers.
"""

from .base import (
    BaseSharedStorage,
    SharedStorageError,
    SharedStorageGap,
    Subscription,
)
from .diskcache import DiskcacheSharedStorage
from .local import LocalSharedStorage
from .redis import RedisSharedStorage

__all__ = [
    "BaseSharedStorage",
    "DiskcacheSharedStorage",
    "LocalSharedStorage",
    "RedisSharedStorage",
    "SharedStorageError",
    "SharedStorageGap",
    "Subscription",
]
