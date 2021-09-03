from . import BaseLongCallbackManager

_pending_value = "__$pending__"


class DiskcacheLongCallbackManager(BaseLongCallbackManager):
    def __init__(self, cache, cache_by=None, expire=None):
        """
        Long callback manager that runs callback logic in a subprocess and stores
        results on disk using diskcache

        :param cache:
            A diskcache.Cache or diskcache.FanoutCache instance. See the diskcache
            documentation for information on configuration options.
        :param cache_by:
            A list of zero-argument functions.  When provided, caching is enabled and
            the return values of these functions are combined with the callback
            function's input arguments and source code to generate cache keys.
        :param expire:
            If provided, a cache entry will be removed when it has not been accessed
            for ``expire`` seconds.  If not provided, the lifetime of cache entries
            is determined by the default behavior of the ``cache`` instance.
        """
        try:
            import diskcache  # pylint: disable=import-outside-toplevel
            import psutil  # noqa: F401,E402 pylint: disable=import-outside-toplevel,unused-import,unused-variable,import-error
            import multiprocess  # noqa: F401,E402 pylint: disable=import-outside-toplevel,unused-import,unused-variable
        except ImportError as missing_imports:
            raise ImportError(
                """\
DiskcacheLongCallbackManager requires the multiprocess, diskcache, and psutil packages
which can be installed using pip...

    $ pip install multiprocess diskcache psutil

or conda.

    $ conda install -c conda-forge multiprocess diskcache psutil\n"""
            ) from missing_imports

        if not isinstance(cache, (diskcache.Cache, diskcache.FanoutCache)):
            raise ValueError("First argument must be a diskcache.Cache object")
        super().__init__(cache_by)
        self.handle = cache
        self.expire = expire

    def terminate_job(self, job):
        import psutil  # pylint: disable=import-outside-toplevel,import-error

        if job is None:
            return

        # Use diskcache transaction so multiple process don't try to kill the
        # process at the same time
        with self.handle.transact():
            if psutil.pid_exists(job):
                process = psutil.Process(job)

                for proc in process.children(recursive=True):
                    try:
                        proc.kill()
                    except psutil.NoSuchProcess:
                        pass

                try:
                    process.kill()
                except psutil.NoSuchProcess:
                    pass

                try:
                    process.wait(0.5)
                except (psutil.TimeoutExpired, psutil.NoSuchProcess):
                    pass

    def terminate_unhealthy_job(self, job):
        import psutil  # pylint: disable=import-outside-toplevel,import-error

        if job and psutil.pid_exists(job):
            if not self.job_running(job):
                self.terminate_job(job)
                return True

        return False

    def job_running(self, job):
        import psutil  # pylint: disable=import-outside-toplevel,import-error

        if job and psutil.pid_exists(job):
            proc = psutil.Process(job)
            return proc.status() != psutil.STATUS_ZOMBIE
        return False

    def make_job_fn(self, fn, progress, args_deps):
        return _make_job_fn(fn, self.handle, progress, args_deps)

    def clear_cache_entry(self, key):
        self.handle.delete(key)

    def call_job_fn(self, key, job_fn, args):
        # pylint: disable-next=import-outside-toplevel,no-name-in-module,import-error
        from multiprocess import Process

        # pylint: disable-next=not-callable
        proc = Process(target=job_fn, args=(key, self._make_progress_key(key), args))
        proc.start()
        return proc.pid

    def get_progress(self, key):
        progress_key = self._make_progress_key(key)
        return self.handle.get(progress_key)

    def result_ready(self, key):
        return self.handle.get(key) is not None

    def get_result(self, key, job):
        # Get result value
        result = self.handle.get(key)
        if result is None:
            return None

        # Clear result if not caching
        if self.cache_by is None:
            self.clear_cache_entry(key)
        else:
            if self.expire:
                self.handle.touch(key, expire=self.expire)

        self.clear_cache_entry(self._make_progress_key(key))

        self.terminate_job(job)
        return result


def _make_job_fn(fn, cache, progress, args_deps):
    def job_fn(result_key, progress_key, user_callback_args):
        def _set_progress(progress_value):
            cache.set(progress_key, progress_value)

        maybe_progress = [_set_progress] if progress else []
        if isinstance(args_deps, dict):
            user_callback_output = fn(*maybe_progress, **user_callback_args)
        elif isinstance(args_deps, (list, tuple)):
            user_callback_output = fn(*maybe_progress, *user_callback_args)
        else:
            user_callback_output = fn(*maybe_progress, user_callback_args)
        cache.set(result_key, user_callback_output)

    return job_fn
