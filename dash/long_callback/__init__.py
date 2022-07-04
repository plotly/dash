from .managers.celery_manager import CeleryLongCallbackManager  # noqa: F401,E402
from .managers.diskcache_manager import DiskcacheLongCallbackManager  # noqa: F401,E402


# Renamed without `LongCallback`


class DiskcacheBackgroundExecutor(DiskcacheLongCallbackManager):
    """Manage the background execution of callbacks with subprocesses and a diskcache result backend."""


class CeleryBackgroundExecutor(CeleryLongCallbackManager):
    """Manage background execution of callbacks with a celery queue."""
