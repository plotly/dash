import os


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
        from dash.long_callback import DiskcacheLongCallbackManager
        import diskcache

        cache = diskcache.Cache(os.environ.get("DISKCACHE_DIR"))
        long_callback_manager = DiskcacheLongCallbackManager(cache)
        long_callback_manager.test_lock = diskcache.Lock(cache, "test-lock")
    else:
        raise ValueError(
            "Invalid long callback manager specified as LONG_CALLBACK_MANAGER "
            "environment variable"
        )

    return long_callback_manager
