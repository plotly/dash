from contextlib import contextmanager

from .._callback_context import context_value as _ctx
from .._utils import AttributeDict as _AD


@contextmanager
def ignore_register_page():
    previous = _ctx.get()
    copied = _AD(previous)
    copied.ignore_register_page = True
    _ctx.set(copied)

    try:
        yield
    finally:
        _ctx.set(previous)
