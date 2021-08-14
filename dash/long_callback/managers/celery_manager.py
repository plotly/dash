import json
import inspect
import hashlib

from _plotly_utils.utils import PlotlyJSONEncoder
from dash.long_callback.managers import BaseLongCallbackManager


class CeleryLongCallbackManager(BaseLongCallbackManager):
    def __init__(self, celery_app, cache_by=None, expire=None):
        import celery  # pylint: disable=import-outside-toplevel

        if not isinstance(celery_app, celery.Celery):
            raise ValueError("First argument must be a celery.Celery object")

        super().__init__(cache_by)
        self.handle = celery_app
        self.expire = expire

    def terminate_job(self, job):
        if job is None:
            return

        self.handle.control.terminate(job)

    def terminate_unhealthy_job(self, job):
        task = self.get_task(job)
        if task and task.status in ("FAILURE", "REVOKED"):
            return self.terminate_job(job)
        return False

    def job_running(self, job):
        future = self.get_task(job)
        return future and future.status in (
            "PENDING",
            "RECEIVED",
            "STARTED",
            "RETRY",
            "PROGRESS",
        )

    def make_job_fn(self, fn, progress=False):
        return _make_job_fn(fn, self.handle, progress)

    def get_task(self, job):
        if job:
            return self.handle.AsyncResult(job)

        return None

    def clear_cache_entry(self, key):
        self.handle.backend.delete(key)

    def call_job_fn(self, key, job_fn, args):
        task = job_fn.delay(key, self._make_progress_key(key), args)
        return task.task_id

    def get_progress(self, key):
        progress_key = self._make_progress_key(key)
        progress_data = self.handle.backend.get(progress_key)
        if progress_data:
            return json.loads(progress_data)

        return None

    def result_ready(self, key):
        return self.handle.backend.get(key) is not None

    def get_result(self, key, job):
        # Get result value
        result = self.handle.backend.get(key)
        if result is None:
            return None

        result = json.loads(result)

        # Clear result if not caching
        if self.cache_by is None:
            self.clear_cache_entry(key)
        else:
            if self.expire:
                # Set/update expiration time
                self.handle.backend.expire(key, self.expire)
        self.clear_cache_entry(self._make_progress_key(key))

        self.terminate_job(job)
        return result


def _make_job_fn(fn, celery_app, progress):
    cache = celery_app.backend

    # Hash function source and module to create a unique (but stable) celery task name
    fn_source = inspect.getsource(fn)
    fn_module = fn.__module__
    fn_str = fn_module + "\n" + fn_source
    fn_hash = hashlib.sha1(fn_str.encode("utf-8")).hexdigest()

    @celery_app.task(name=fn_hash)
    def job_fn(result_key, progress_key, user_callback_args, fn=fn):
        def _set_progress(progress_value):
            cache.set(progress_key, json.dumps(progress_value, cls=PlotlyJSONEncoder))

        maybe_progress = [_set_progress] if progress else []
        if isinstance(user_callback_args, dict):
            user_callback_output = fn(*maybe_progress, **user_callback_args)
        elif isinstance(user_callback_args, list):
            user_callback_output = fn(*maybe_progress, *user_callback_args)
        else:
            user_callback_output = fn(*maybe_progress, user_callback_args)

        cache.set(result_key, json.dumps(user_callback_output, cls=PlotlyJSONEncoder))

    return job_fn
