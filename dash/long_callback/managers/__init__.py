from abc import ABC
import inspect
import hashlib


class BaseLongCallbackManager(ABC):
    def __init__(self, cache_by):
        if cache_by is not None and not isinstance(cache_by, list):
            cache_by = [cache_by]

        self.cache_by = cache_by

    def delete_future(self, key):
        raise NotImplementedError

    def terminate_unhealthy_future(self, key):
        raise NotImplementedError

    def has_future(self, key):
        raise NotImplementedError

    def get_future(self, key, default=None):
        raise NotImplementedError

    def make_background_fn(self, fn, progress):
        raise NotImplementedError

    def call_and_register_background_fn(self, key, background_fn, args):
        raise NotImplementedError

    def get_progress(self, key):
        raise NotImplementedError

    def result_ready(self, key):
        raise NotImplementedError

    def get_result(self, key):
        raise NotImplementedError

    def build_cache_key(self, fn, args):
        fn_source = inspect.getsource(fn)
        hash_dict = dict(args=args, fn_source=fn_source)

        if self.cache_by is not None:
            # Caching enabled
            for i, cache_item in enumerate(self.cache_by):
                # Call cache function
                hash_dict[f"cache_key_{i}"] = cache_item()

        return hashlib.sha1(str(hash_dict).encode("utf-8")).hexdigest()
