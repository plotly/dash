import typing as _t

from importlib import metadata as _importlib_metadata

from .exceptions import HookError
from .resources import ResourceType
from ._callback import ClientsideFuncType

if _t.TYPE_CHECKING:
    from .dash import Dash
    from .development.base_component import Component

    ComponentType = _t.TypeVar("ComponentType", bound=Component)
    LayoutType = _t.Union[ComponentType, _t.List[ComponentType]]
else:
    LayoutType = None
    ComponentType = None
    Dash = None


HookDataType = _t.TypeVar("HookDataType")
DevtoolPosition = _t.Literal["right", "left"]


# pylint: disable=too-few-public-methods
class _Hook(_t.Generic[HookDataType]):
    def __init__(
        self, func, priority=0, final=False, data: _t.Optional[HookDataType] = None
    ):
        self.func = func
        self.final = final
        self.data = data
        self.priority = priority

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class _Hooks:
    """
    Extend every Dash app from a separate package, through ``dash.hooks``.

    Hooks are registered at import time, usually in a plugin package, and
    apply to every ``Dash`` app created after they are registered. To load a
    plugin without importing it in the app, declare a ``dash_hooks`` entry
    point that points to the module registering the hooks::

        # pyproject.toml
        [project.entry-points.dash_hooks]
        my_plugin = "my_plugin"

    Example::

        from dash import hooks, html

        @hooks.layout()
        def add_footer(layout):
            return [layout, html.Footer("Powered by my_plugin")]

    Decorator hooks take ``priority`` and ``final``. Hooks with a higher
    ``priority`` run first; without one, hooks run in the order they were
    registered. A ``final`` hook always runs last, and only one ``final``
    hook is allowed per hook type.
    """

    def __init__(self) -> None:
        self._ns: _t.Dict[str, _t.List[_t.Any]] = {
            "setup": [],
            "layout": [],
            "routes": [],
            "error": [],
            "callback": [],
            "index": [],
            "custom_data": [],
            "dev_tools": [],
            "websocket_connect": [],
            "websocket_message": [],
        }
        self._js_dist: _t.List[_t.Any] = []
        self._css_dist: _t.List[_t.Any] = []
        self._clientside_callbacks: _t.List[
            _t.Tuple[ClientsideFuncType, _t.Any, _t.Any]
        ] = []

        # final hooks are a single hook added to the end of regular hooks.
        self._finals: _t.Dict[str, _t.Any] = {}

    def add_hook(
        self,
        hook: str,
        func: _t.Callable,
        priority: _t.Optional[int] = None,
        final: bool = False,
        data: _t.Optional[HookDataType] = None,
    ):
        if final:
            existing = self._finals.get(hook)
            if existing:
                raise HookError("Final hook already present")
            self._finals[hook] = _Hook(func, final, data=data)
            return
        hks = self._ns.get(hook, [])

        p = priority or 0
        if not priority and len(hks):
            # Take the minimum value and remove 1 to keep the order.
            priority_min = min(h.priority for h in hks)
            p = priority_min - 1

        hks.append(_Hook(func, priority=p, data=data))
        self._ns[hook] = sorted(hks, reverse=True, key=lambda h: h.priority)

    def get_hooks(self, hook: str) -> _t.List[_Hook]:
        final = self._finals.get(hook, None)
        if final:
            final = [final]
        else:
            final = []
        return self._ns.get(hook, []) + final

    def layout(self, priority: _t.Optional[int] = None, final: bool = False):
        """
        Modify the layout each time it is served.

        The function receives the current layout and returns the new one.
        Layout hooks are chained, each one receives the result of the
        previous one.

        Example::

            @hooks.layout()
            def wrap(layout):
                return html.Div([html.Header("My org"), layout])
        """

        def _wrap(func: _t.Callable[[LayoutType], LayoutType]):
            self.add_hook("layout", func, priority=priority, final=final)
            return func

        return _wrap

    def setup(self, priority: _t.Optional[int] = None, final: bool = False):
        """
        Run a function with the app instance once it is created.

        Called during ``Dash.__init__``, before the server routes are set
        up, with the ``Dash`` app as its only argument. The return value is
        ignored.

        Example::

            @hooks.setup()
            def on_setup(app):
                app.config.suppress_callback_exceptions = True
        """

        def _setup(func: _t.Callable[[Dash], None]):
            self.add_hook("setup", func, priority=priority, final=final)
            return func

        return _setup

    def route(
        self,
        name: _t.Optional[str] = None,
        methods: _t.Sequence[str] = ("GET",),
        priority: _t.Optional[int] = None,
        final: bool = False,
    ):
        """
        Add a route to the Dash server.

        ``name`` is the url path, relative to ``routes_pathname_prefix``. It
        defaults to the function name. ``methods`` lists the allowed HTTP
        methods. The function takes no arguments and its return value is
        the response.

        The route function can be ``async def``; with the Flask backend this
        requires ``flask[async]``. Read the request with
        ``dash.get_app().backend.request_adapter()``.

        Example::

            @hooks.route("my-plugin/status", methods=("GET",))
            def status():
                return {"ok": True}
        """

        def wrap(func: _t.Callable[[], _t.Any]):
            _name = name or func.__name__
            self.add_hook(
                "routes",
                func,
                priority=priority,
                final=final,
                data=dict(name=_name, methods=methods),
            )
            return func

        return wrap

    def error(self, priority: _t.Optional[int] = None, final: bool = False):
        """
        Handle exceptions raised in callbacks.

        The function receives the exception, the same way as the app
        ``on_error`` argument. It runs after the app ``on_error`` handler
        if one is set. A value returned by either is used as the callback
        output, the app handler result taking precedence.

        Example::

            @hooks.error()
            def log_error(err):
                logger.exception(err)
        """

        def _error(func: _t.Callable[[Exception], _t.Any]):
            self.add_hook("error", func, priority=priority, final=final)
            return func

        return _error

    def callback(
        self, *args, priority: _t.Optional[int] = None, final: bool = False, **kwargs
    ):
        """
        Add a callback to every app.

        Takes the same arguments as ``dash.callback``. The components it
        uses must be in the app layout, usually added with a layout hook.

        Example::

            @hooks.callback(Output("plugin-out", "children"), Input("plugin-btn", "n_clicks"))
            def on_click(n_clicks):
                return f"Clicked {n_clicks} times"
        """

        def wrap(func):
            self.add_hook(
                "callback",
                func,
                priority=priority,
                final=final,
                data=(list(args), dict(kwargs)),
            )
            return func

        return wrap

    def clientside_callback(
        self, clientside_function: ClientsideFuncType, *args, **kwargs
    ):
        """
        Add a clientside callback to every app.

        Takes the same arguments as ``dash.clientside_callback``. Unlike
        the other hooks, this is a plain call, not a decorator.

        Example::

            hooks.clientside_callback(
                "function(n) { return n || 0; }",
                Output("plugin-count", "children"),
                Input("plugin-btn", "n_clicks"),
            )
        """
        self._clientside_callbacks.append((clientside_function, args, kwargs))

    def script(self, distribution: _t.List[ResourceType]):
        """
        Add JavaScript files to every app.

        ``distribution`` is a list of resources in the same format as a
        component library ``_js_dist``: dicts with ``relative_package_path``,
        ``external_url``, ``namespace``, and so on.

        Example::

            hooks.script([{
                "external_url": "https://cdn.example.com/plugin.js",
                "namespace": "my_plugin",
            }])
        """
        self._js_dist.extend(distribution)

    def stylesheet(self, distribution: _t.List[ResourceType]):
        """
        Add stylesheets to every app.

        ``distribution`` is a list of resources in the same format as a
        component library ``_css_dist``. See ``hooks.script``.
        """
        self._css_dist.extend(distribution)

    def index(self, priority: _t.Optional[int] = None, final=False):
        """
        Modify the HTML of the index page.

        The function receives the rendered index as a string and returns
        the new one. The result must still contain the Dash entry points,
        or serving the page raises an error.

        Example::

            @hooks.index()
            def add_banner(index):
                return index.replace("<body>", "<body><div>Beta</div>")
        """

        def wrap(func):
            self.add_hook(
                "index",
                func,
                priority=priority,
                final=final,
            )
            return func

        return wrap

    def custom_data(
        self, namespace: str, priority: _t.Optional[int] = None, final=False
    ):
        """
        Add data to ``callback_context.custom_data`` under ``namespace``.

        Runs before each callback. The function receives the callback
        context value and its return value is stored under ``namespace``.
        It runs inside the request, so it can read it with
        ``dash.get_app().backend.request_adapter()``.

        Example::

            @hooks.custom_data("auth")
            def user(_ctx):
                req = dash.get_app().backend.request_adapter()
                return {"user": req.headers.get("X-User")}

            # in a callback: ctx.custom_data.auth["user"]
        """

        def wrap(func: _t.Callable[[_t.Dict], _t.Any]):
            self.add_hook(
                "custom_data",
                func,
                priority=priority,
                final=final,
                data={"namespace": namespace},
            )
            return func

        return wrap

    def devtool(
        self,
        namespace: str,
        component_type: str,
        props=None,
        position: DevtoolPosition = "right",
    ):
        """
        Add a component to be rendered inside the dev tools.

        ``namespace`` and ``component_type`` name the component, as in its
        ``_namespace`` and ``_type``. ``position`` is ``"right"`` or
        ``"left"`` in the dev tools bar. Only shown when the dev tools UI is
        on (``debug=True``).

        If it's a dash component, it can be used in callbacks provided
        that it has an id and the dependency is set with ``allow_optional=True``.

        ``props`` can be a function, in which case it will be called before
        sending the component to the frontend.

        Example::

            hooks.devtool(
                "dash_html_components", "Div",
                props={"id": "plugin-devtool", "children": "my_plugin"},
            )
        """
        self._ns["dev_tools"].append(
            {
                "namespace": namespace,
                "type": component_type,
                "props": props or {},
                "position": position,
            }
        )

    def websocket_connect(self, priority: _t.Optional[int] = None, final: bool = False):
        """
        Register a WebSocket connection validation hook.

        The hook receives the WebSocket object and should return:
        - True (or any truthy value): Allow the connection
        - False: Reject with default code (4001) and reason
        - tuple (code, reason): Reject with custom close code and reason

        Hooks can be sync or async.

        Example:
            @hooks.websocket_connect()
            async def validate_session(websocket):
                session_id = websocket.cookies.get("session_id")
                if not session_id:
                    return (4001, "No session cookie")
                if not await is_valid_session(session_id):
                    return (4002, "Invalid session")
                return True
        """

        def decorator(func: _t.Callable):
            self.add_hook("websocket_connect", func, priority=priority, final=final)
            return func

        return decorator

    def websocket_message(self, priority: _t.Optional[int] = None, final: bool = False):
        """
        Register a WebSocket message validation hook.

        The hook receives the WebSocket object and message dict, and should return:
        - True (or any truthy value): Allow the message
        - False: Disconnect with default code (4001) and reason
        - tuple (code, reason): Disconnect with custom close code and reason

        Hooks can be sync or async.

        Example:
            @hooks.websocket_message()
            async def validate_session(websocket, message):
                session_id = websocket.cookies.get("session_id")
                if not await is_session_active(session_id):
                    return (4002, "Session expired")
                return True
        """

        def decorator(func: _t.Callable):
            self.add_hook("websocket_message", func, priority=priority, final=final)
            return func

        return decorator


hooks = _Hooks()


class HooksManager:
    # Flag to only run `register_setuptools` once
    _registered = False
    hooks = hooks

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

    @classmethod
    def get_hooks(cls, hook: str):
        return cls.hooks.get_hooks(hook)

    @classmethod
    def register_setuptools(cls):
        if cls._registered:
            # Only have to register once.
            return

        for dist in _importlib_metadata.distributions():
            for entry in dist.entry_points:
                # Look for setup.py entry points named `dash_hooks`
                if entry.group != "dash_hooks":
                    continue
                entry.load()
