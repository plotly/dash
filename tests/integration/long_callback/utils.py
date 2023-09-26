import os
import shutil
import subprocess
import tempfile
import time
from contextlib import contextmanager

import psutil
import redis

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


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


@contextmanager
def setup_long_callback_app(manager_name, app_name):
    from dash.testing.application_runners import import_app

    if manager_name == "celery":
        os.environ["LONG_CALLBACK_MANAGER"] = "celery"
        redis_url = os.environ["REDIS_URL"].rstrip("/")
        os.environ["CELERY_BROKER"] = f"{redis_url}/0"
        os.environ["CELERY_BACKEND"] = f"{redis_url}/1"

        # Clear redis of cached values
        redis_conn = redis.Redis(host="localhost", port=6379, db=1)
        cache_keys = redis_conn.keys()
        if cache_keys:
            redis_conn.delete(*cache_keys)

        worker = subprocess.Popen(
            [
                "celery",
                "-A",
                f"tests.integration.long_callback.{app_name}:handle",
                "worker",
                "-P",
                "prefork",
                "--concurrency",
                "2",
                "--loglevel=info",
            ],
            preexec_fn=os.setpgrp,
            stderr=subprocess.PIPE,
        )
        # Wait for the worker to be ready, if you cancel before it is ready, the job
        # will still be queued.
        for line in iter(worker.stderr.readline, ""):
            if "ready" in line.decode():
                break

        try:
            yield import_app(f"tests.integration.long_callback.{app_name}")
        finally:
            # Interval may run one more time after settling on final app state
            # Sleep for 1 interval of time
            time.sleep(0.5)
            os.environ.pop("LONG_CALLBACK_MANAGER")
            os.environ.pop("CELERY_BROKER")
            os.environ.pop("CELERY_BACKEND")
            kill(worker.pid)
            from dash import page_registry

            page_registry.clear()

    elif manager_name == "diskcache":
        os.environ["LONG_CALLBACK_MANAGER"] = "diskcache"
        cache_directory = tempfile.mkdtemp(prefix="lc-diskcache-")
        print(cache_directory)
        os.environ["DISKCACHE_DIR"] = cache_directory
        try:
            app = import_app(f"tests.integration.long_callback.{app_name}")
            yield app
        finally:
            # Interval may run one more time after settling on final app state
            # Sleep for a couple of intervals
            time.sleep(2.0)

            for job in manager.running_jobs:
                manager.terminate_job(job)

            shutil.rmtree(cache_directory, ignore_errors=True)
            os.environ.pop("LONG_CALLBACK_MANAGER")
            os.environ.pop("DISKCACHE_DIR")
            from dash import page_registry

            page_registry.clear()
