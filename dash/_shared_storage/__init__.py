"""Backend-agnostic shared state + pub/sub (state manager).

Exposes the ``BaseSharedStorage`` interface and its backends:

- ``LocalSharedStorage``: in-memory, owner-elected -- one container.
- ``ClusterSharedStorage``: the same, owner elected across replicas -- pods,
  with no external service.
- ``DiskcacheSharedStorage``: on a ``diskcache.Cache`` -- one machine, not pods.
- ``RedisSharedStorage``: on Redis -- across processes and containers.
"""

from .base import (
    BaseSharedStorage,
    SharedStorageError,
    SharedStorageGap,
    Subscription,
)
from .cluster import ClusterSharedStorage
from .diskcache import DiskcacheSharedStorage
from .local import LocalSharedStorage
from .redis import RedisSharedStorage

__all__ = [
    "BaseSharedStorage",
    "ClusterSharedStorage",
    "DiskcacheSharedStorage",
    "LocalSharedStorage",
    "RedisSharedStorage",
    "SharedStorageError",
    "SharedStorageGap",
    "Subscription",
]
