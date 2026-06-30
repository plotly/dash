import json
from unittest import mock

import pytest

from dash import _callback
from dash._callback import _setup_background_callback, context_value
from dash._utils import AttributeDict


class FakeMultiDict:
    """Minimal multi-dict standing in for a backend query-params object.

    It mimics ``starlette.datastructures.QueryParams`` for these tests: it is
    convertible to a ``dict`` and exposes ``getlist``, but is **not** a ``dict``
    subclass and is **not** JSON serialisable.

    Parameters
    ----------
    items : list of tuple
        The ``(key, value)`` pairs held by the multi-dict.
    """

    def __init__(self, items):
        self._items = list(items)

    def getlist(self, key):
        """Return all values stored under ``key``."""
        return [value for stored_key, value in self._items if stored_key == key]

    def keys(self):
        """Return the keys, enabling ``dict(self)`` coercion."""
        return [key for key, _ in self._items]

    def __getitem__(self, key):
        for stored_key, value in self._items:
            if stored_key == key:
                return value
        raise KeyError(key)


def _make_context(args_value):
    """Build a minimal callback context containing ``args``.

    Parameters
    ----------
    args_value : Any
        The value to store under the ``args`` key.

    Returns
    -------
    AttributeDict
        A context with the keys ``_setup_background_callback`` expects to find
        and pop.
    """
    return AttributeDict(
        args=args_value,
        background_callback_manager=object(),
        dash_response=object(),
    )


class _CapturingManager:
    """Background callback manager stub that captures the dispatched context."""

    def __init__(self):
        self.captured_context = None
        self.func_registry = mock.Mock()
        self.func_registry.get.return_value = object()

    def build_cache_key(self, *_args, **_kwargs):
        """Return a deterministic cache key."""
        return "cache-key"

    def call_job_fn(self, _cache_key, _job_fn, _func_args, context):
        """Capture the context that would be dispatched to the worker."""
        self.captured_context = context
        return "job-id"


@pytest.fixture(name="patched_app")
def fixture_patched_app():
    """Patch ``get_app`` so ``_get_callback_manager`` can resolve an adapter."""
    adapter = mock.Mock()
    adapter.args.getlist.return_value = []
    app = mock.Mock()
    app.backend.request_adapter.return_value = adapter
    with mock.patch.object(_callback, "get_app", return_value=app):
        yield app


def _run_setup(manager, args_value):
    """Run ``_setup_background_callback`` with ``args_value`` on the context.

    Parameters
    ----------
    manager : _CapturingManager
        The manager whose ``call_job_fn`` captures the dispatched context.
    args_value : Any
        The value to place under the context ``args`` key.
    """
    token = context_value.set(_make_context(args_value))
    try:
        _setup_background_callback(
            kwargs={},
            background={"manager": manager},
            background_key="bg-key",
            func=lambda: None,
            func_args=[],
            func_kwargs={},
            callback_ctx=AttributeDict(),
        )
    finally:
        context_value.reset(token)


def test_non_dict_args_coerced_to_serialisable_dict(patched_app):
    """A non-dict ``args`` is coerced to a JSON-serialisable ``dict``."""
    manager = _CapturingManager()
    args_value = FakeMultiDict([("foo", "bar"), ("baz", "qux")])

    _run_setup(manager, args_value)

    dispatched_args = manager.captured_context["args"]
    assert isinstance(dispatched_args, dict)
    assert dispatched_args == {"foo": "bar", "baz": "qux"}
    # Must not raise; the worker dispatch relies on this being serialisable.
    json.dumps(dispatched_args)


def test_dict_args_left_unchanged(patched_app):
    """An ``args`` value that is already a ``dict`` is preserved as-is."""
    manager = _CapturingManager()
    args_value = {"foo": "bar"}

    _run_setup(manager, args_value)

    dispatched_args = manager.captured_context["args"]
    assert dispatched_args == {"foo": "bar"}
    json.dumps(dispatched_args)


def test_none_args_left_as_none(patched_app):
    """A missing/``None`` ``args`` value does not raise and stays ``None``."""
    manager = _CapturingManager()

    _run_setup(manager, None)

    assert manager.captured_context["args"] is None


def test_starlette_query_params_coerced(patched_app):
    """A real ``starlette`` ``QueryParams`` is coerced to a serialisable dict."""
    query_params = pytest.importorskip("starlette.datastructures").QueryParams

    manager = _CapturingManager()
    _run_setup(manager, query_params("foo=bar&baz=qux"))

    dispatched_args = manager.captured_context["args"]
    assert isinstance(dispatched_args, dict)
    assert dispatched_args == {"foo": "bar", "baz": "qux"}
    json.dumps(dispatched_args)
