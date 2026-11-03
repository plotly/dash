import functools
import inspect

from contextvars import ContextVar, copy_context
from textwrap import dedent
from typing import Any, Optional

from dash.exceptions import AppNotFoundError

APP: Optional[Any] = None

app_context: ContextVar[Any] = ContextVar("dash_app_context")


def with_app_context(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        app_context.set(self)
        ctx = copy_context()
        return ctx.run(func, self, *args, **kwargs)

    return wrap


def with_app_context_async(func):
    @functools.wraps(func)
    async def wrap(self, *args, **kwargs):
        app_context.set(self)
        ctx = copy_context()
        return await ctx.run(func, self, *args, **kwargs)

    return wrap


def with_app_context_factory(func, app):
    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrap(*args, **kwargs):
            # The coroutine runs in the awaiting task's context, so set the app
            # there and restore it after, rather than in a copied context.
            token = app_context.set(app)
            try:
                return await func(*args, **kwargs)
            finally:
                app_context.reset(token)

        return async_wrap

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        # Set the app in the copy only, so it doesn't leak to the caller.
        ctx = copy_context()
        ctx.run(app_context.set, app)
        return ctx.run(func, *args, **kwargs)

    return wrap


def get_app():
    """
    Return the current Dash app instance.

    Useful in multi-page apps when Python files within the `pages/` folder
    need to reference the `app` object but importing it directly would cause
    a circular import error.
    """
    try:
        ctx_app = app_context.get()
        if ctx_app is not None:
            return ctx_app
    except LookupError:
        pass

    if APP is None:
        raise AppNotFoundError(
            dedent(
                """
                App object is not yet defined.  `app = dash.Dash()` needs to be run
                before `dash.get_app()`.

                `dash.get_app()` is used to get around circular import issues when Python files
                within the pages/` folder need to reference the `app` object.
                """
            )
        )
    return APP
