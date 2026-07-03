"""Unit tests for the async background callback job functions.

These tests reproduce the ``UnboundLocalError`` that occurred when an async
background callback raised ``PreventUpdate`` or another exception before
``user_callback_output`` was assigned. They exercise the generated job
function directly, so they require neither a browser nor a running Celery or
Diskcache backend.
"""
import json

import pytest

from dash.exceptions import PreventUpdate
from dash.background_callback.managers.celery_manager import (
    _make_job_fn as make_celery_job_fn,
)
from dash.background_callback.managers.diskcache_manager import (
    _make_job_fn as make_diskcache_job_fn,
)


class FakeCache:
    """Minimal in-memory stand-in for a Diskcache/Celery result backend."""

    def __init__(self):
        self.store = {}

    def set(self, key, value):
        self.store[key] = value

    def get(self, key, default=None):
        return self.store.get(key, default)


class FakeCeleryApp:
    """Minimal Celery application exposing a backend and a task decorator."""

    def __init__(self):
        self.backend = FakeCache()

    def task(self, *_args, **_kwargs):
        def decorator(func):
            return func

        return decorator


def _run_diskcache_job(fn):
    cache = FakeCache()
    job_fn = make_diskcache_job_fn(fn, cache, progress=False)
    job_fn("result-key", "progress-key", ["input"], {})
    return cache.store.get("result-key")


def _run_celery_job(fn):
    celery_app = FakeCeleryApp()
    job_fn = make_celery_job_fn(fn, celery_app, progress=False, key="test")
    job_fn("result-key", "progress-key", ["input"], {})
    stored = celery_app.backend.store.get("result-key")
    return json.loads(stored) if stored is not None else None


def test_diskcache_async_job_fn_exception_is_reported():
    """A raised exception is cached as a background_callback_error, not masked."""

    async def fn(_value):
        raise ValueError("boom")

    result = _run_diskcache_job(fn)
    assert "background_callback_error" in result
    assert result["background_callback_error"]["msg"] == "boom"


def test_diskcache_async_job_fn_prevent_update_is_reported():
    """Raising PreventUpdate caches a no-update result without raising."""

    async def fn(_value):
        raise PreventUpdate

    result = _run_diskcache_job(fn)
    assert result == {"_dash_no_update": "_dash_no_update"}


def test_diskcache_async_job_fn_success_is_reported():
    """A successful async callback caches its return value."""

    async def fn(value):
        return f"processed {value}"

    result = _run_diskcache_job(fn)
    assert result == "processed input"


def test_celery_async_job_fn_exception_is_reported():
    """A raised exception is cached as a background_callback_error, not masked."""

    async def fn(_value):
        raise ValueError("boom")

    result = _run_celery_job(fn)
    assert "background_callback_error" in result
    assert result["background_callback_error"]["msg"] == "boom"


def test_celery_async_job_fn_prevent_update_is_reported():
    """Raising PreventUpdate caches a no-update result without raising."""

    async def fn(_value):
        raise PreventUpdate

    result = _run_celery_job(fn)
    assert result == {"_dash_no_update": "_dash_no_update"}


def test_celery_async_job_fn_success_is_reported():
    """A successful async callback caches its return value."""

    async def fn(value):
        return f"processed {value}"

    result = _run_celery_job(fn)
    assert result == "processed input"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
