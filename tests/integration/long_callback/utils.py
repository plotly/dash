import os

from dash.long_callback import DiskcacheManager

manager = None


class TestDiskCacheManager(DiskcacheManager):
    def __init__(self, cache=None, cache_by=None, expire=None):
        super().__init__(cache=cache, cache_by=cache_by, expire=expire)
        self.running_jobs = []

    def call_job_fn(self, key, job_fn, args, context):
        pid = super().call_job_fn(key, job_fn, args, context)
        self.running_jobs.append(pid)
        return pid


def get_long_callback_manager():
    """
    Get the long callback mangaer configured by environment variables
    """
    if os.environ.get("LONG_CALLBACK_MANAGER", None) == "celery":
        from dash.long_callback import CeleryLongCallbackManager
        from celery import Celery
        import redis

        celery_app = Celery(
            __name__,
            broker=os.environ.get("CELERY_BROKER"),
            backend=os.environ.get("CELERY_BACKEND"),
        )
        long_callback_manager = CeleryLongCallbackManager(celery_app)
        redis_conn = redis.Redis(host="localhost", port=6379, db=1)
        long_callback_manager.test_lock = redis_conn.lock("test-lock")
    elif os.environ.get("LONG_CALLBACK_MANAGER", None) == "diskcache":
        import diskcache

        cache = diskcache.Cache(os.environ.get("DISKCACHE_DIR"))
        long_callback_manager = TestDiskCacheManager(cache)
        long_callback_manager.test_lock = diskcache.Lock(cache, "test-lock")
    else:
        raise ValueError(
            "Invalid long callback manager specified as LONG_CALLBACK_MANAGER "
            "environment variable"
        )

    global manager
    manager = long_callback_manager

    return long_callback_manager
