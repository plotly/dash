from . import BaseLongCallbackManager


class DiskcacheLongCallbackManager(BaseLongCallbackManager):
    def __init__(self, cache, cache_by=None, expire=None):
        try:
            import diskcache  # pylint: disable=import-outside-toplevel
            from multiprocess import (  # pylint: disable=import-outside-toplevel
                Process,
            )
        except ImportError:
            raise ImportError(
                """\
DiskcacheLongCallbackManager requires the multiprocess and diskcache packages which
can be installed using pip...

    $ pip install multiprocess diskcache

or conda.

    $ conda install -c conda-forge multiprocess diskcache\n"""
            )

        if not isinstance(cache, diskcache.Cache):
            raise ValueError("First argument must be a diskcache.Cache object")
        super().__init__(cache_by)

        self.Process = Process
        self.cache = cache
        self.callback_futures = dict()
        self.expire = expire

    def delete_future(self, key):
        if key in self.callback_futures:
            future = self.callback_futures.pop(key, None)
            if future:
                future.terminate()
                future.join()
                return True
        return False

    def clear_cache_entry(self, key):
        self.cache.delete(key)

    def terminate_unhealthy_future(self, key):
        return False

    def has_future(self, key):
        return self.callback_futures.get(key, None) is not None

    def get_future(self, key, default=None):
        return self.callback_futures.get(key, default)

    def make_background_fn(self, fn, progress=False):
        return make_update_cache(fn, self.cache, progress, self.expire)

    @staticmethod
    def _make_progress_key(key):
        return key + "-progress"

    def call_and_register_background_fn(self, key, background_fn, args):
        self.delete_future(key)
        future = self.Process(
            target=background_fn, args=(key, self._make_progress_key(key), args)
        )
        future.start()
        self.callback_futures[key] = future

    def get_progress(self, key):
        future = self.get_future(key)
        if future is not None:
            progress_key = self._make_progress_key(key)
            return self.cache.get(progress_key)
        return None

    def result_ready(self, key):
        return self.cache.get(key) not in (None, "__undefined__")

    def get_result(self, key):
        # Get result value
        result = self.cache.get(key)
        if result == "__undefined__":
            result = None

        # Clear result if not caching
        if self.cache_by is None and result is not None:
            self.clear_cache_entry(key)

        # Always delete_future (even if we didn't clear cache) so that we can
        # handle the case where cache entry is cleared externally.
        self.delete_future(key)
        return result


def make_update_cache(fn, cache, progress, expire):
    def _callback(result_key, progress_key, user_callback_args):
        def _set_progress(progress_value):
            cache.set(progress_key, progress_value)

        maybe_progress = [_set_progress] if progress else []
        if isinstance(user_callback_args, dict):
            user_callback_output = fn(*maybe_progress, **user_callback_args)
        elif isinstance(user_callback_args, (list, tuple)):
            user_callback_output = fn(*maybe_progress, *user_callback_args)
        else:
            user_callback_output = fn(*maybe_progress, user_callback_args)
        cache.set(result_key, user_callback_output, expire=expire)

    return _callback
