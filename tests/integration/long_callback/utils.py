import os


def get_long_callback_manager():
    """
    Get the long callback mangaer configured by environment variables
    """
    if os.environ.get("LONG_CALLBACK_MANAGER", None) == "celery":
        from dash.long_callback import CeleryLongCallbackManager
        from celery import Celery

        celery_app = Celery(
            __name__,
            broker="redis://localhost:6379/0",
            backend="redis://localhost:6379/1",
        )
        long_callback_manager = CeleryLongCallbackManager(celery_app)
    elif os.environ.get("LONG_CALLBACK_MANAGER", None) == "diskcache":
        from dash.long_callback import DiskcacheLongCallbackManager
        import diskcache

        cache = diskcache.Cache(os.environ.get("DISKCACHE_DIR"))
        long_callback_manager = DiskcacheLongCallbackManager(cache)
    else:
        raise ValueError(
            "Invalid long callback manager specified as LONG_CALLBACK_MANAGER "
            "environment variable"
        )

    return long_callback_manager
