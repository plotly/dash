import typing as _t

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


def route(name=None, methods=("GET",)):
    """
    Add a route to the Dash server.
    """

    def wrap(func):
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
        def __init__(self, original, hooks):
            self.original = original
            self.hooks = hooks

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

        import importlib.metadata  # pylint: disable=import-outside-toplevel

        for dist in importlib.metadata.distributions():
            for entry in dist.entry_points:
                if entry.group != "dash":
                    continue
                entry.load()
