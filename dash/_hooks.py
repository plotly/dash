import typing as _t
from importlib import metadata as _importlib_metadata

import flask as _f

_ns = {
    "setup": [],
    "layout": [],
    "routes": [],
    "error": [],
    "callback": [],
}


def layout(func):
    """
    Run a function when serving the layout, the return value
    will be used as the layout.
    """
    _ns["layout"].append(func)
    return func


def setup(func):
    """
    Can be used to get a reference to the app after it is instantiated.
    """
    _ns["setup"].append(func)
    return func


def route(name: _t.Optional[str] = None, methods: _t.Sequence[str] = ("GET",)):
    """
    Add a route to the Dash server.
    """

    def wrap(func: _t.Callable[[], _f.Response]):
        _name = name or func.__name__
        _ns["routes"].append((_name, func, methods))
        return func

    return wrap


def error(func: _t.Callable[[Exception], _t.Any]):
    """Automatically add an error handler to the dash app."""
    _ns["error"].append(func)
    return func


def callback(*args, **kwargs):
    """
    Add a callback to all the apps with the hook installed.
    """

    def wrap(func):
        _ns["callback"].append((list(args), dict(kwargs), func))
        return func

    return wrap


class HooksManager:
    _registered = False

    # pylint: disable=too-few-public-methods
    class HookErrorHandler:
        def __init__(self, original):
            self.original = original

        def __call__(self, err: Exception):
            result = None
            if self.original:
                result = self.original(err)
            hook_result = None
            for hook in HooksManager.get_hooks("error"):
                hook_result = hook(err)
            return result or hook_result

    @staticmethod
    def get_hooks(hook: str):
        return _ns.get(hook, []).copy()

    @classmethod
    def register_setuptools(cls):
        if cls._registered:
            return

        for dist in _importlib_metadata.distributions():
            for entry in dist.entry_points:
                if entry.group != "dash":
                    continue
                entry.load()
