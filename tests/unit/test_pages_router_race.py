"""Regression test for gh-3971: pages ``router_sync`` / ``router_async`` TOCTOU race.

Both hooks used to set ``_got_first_request["pages"]`` at their top and only
then register the ``_ID_CONTENT`` router callback and build
``validation_layout``. Under a multi-threaded WSGI worker (for the sync
hook) or an ASGI worker with multiple concurrent tasks (for the async
one), a second request arriving mid-setup could observe the flag already
set, skip setup, then serve a request against a callback that was not
yet registered.

The tests here reproduce the window by pausing setup inside the guarded
region and driving the hook concurrently. The state observed at the
moment each caller returns must reflect a fully completed setup.
"""

import asyncio
import threading
import time

import dash
from dash import Dash, dependencies, html

ROUTER_OUTPUT_ID = "_pages_content"


def _grab_before_request(app):
    """Capture the ``before_request`` closure that ``enable_pages`` installs."""
    captured = {}
    original = app.backend.before_request

    def capture(fn):
        captured["fn"] = fn

    app.backend.before_request = capture  # type: ignore[method-assign]
    try:
        app.enable_pages()
    finally:
        app.backend.before_request = original  # type: ignore[method-assign]
    return captured["fn"]


def test_router_sync_is_atomic_under_concurrent_requests(clear_pages_state):
    app = Dash(use_pages=True, pages_folder="")
    dash.register_page("home_page", path="/", layout=html.Div("home"))
    app.layout = html.Div([dash.page_container])
    app._use_async = False

    original_input_init = dependencies.Input.__init__
    slowed = {"first": True}
    slow_lock = threading.Lock()

    def slow_input_init(self, component_id, component_property):
        # Widen the window between "flag is set" and "router callback is
        # registered" so a stock CPython scheduler reliably lets other
        # threads through the pages guard while the winning thread is
        # still building its Input arguments.
        with slow_lock:
            need_sleep = slowed["first"]
            slowed["first"] = False
        if need_sleep:
            time.sleep(0.1)
        original_input_init(self, component_id, component_property)

    dependencies.Input.__init__ = slow_input_init  # type: ignore[assignment]
    try:
        router_sync = _grab_before_request(app)

        thread_count = 4
        barrier = threading.Barrier(thread_count)
        callback_maps_seen = []
        errors = []
        lock = threading.Lock()

        def worker():
            barrier.wait()
            try:
                router_sync()
            except Exception as e:  # noqa: BLE001
                with lock:
                    errors.append(e)
                return
            # Snapshot ``callback_map`` at the moment this thread's call
            # returns. A raced-in thread that skipped setup on the old
            # (buggy) code path would return here with the map empty of
            # the router callback.
            with lock:
                callback_maps_seen.append(dict(app.callback_map))

        threads = [threading.Thread(target=worker) for _ in range(thread_count)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
    finally:
        dependencies.Input.__init__ = original_input_init  # type: ignore[assignment]

    assert not errors, f"router_sync raised under concurrent callers: {errors}"
    assert len(callback_maps_seen) == thread_count
    for cm in callback_maps_seen:
        router_entries = [k for k in cm if ROUTER_OUTPUT_ID in k]
        assert router_entries, (
            "A thread returned from router_sync before the router callback "
            "was registered; callback_map was still missing the entry. "
            "(Before the fix, threads that raced past the guard would see "
            "the flag set but no callback yet.)"
        )
    winning_map = callback_maps_seen[-1]
    router_entries = [k for k in winning_map if ROUTER_OUTPUT_ID in k]
    assert len(router_entries) == 1


def test_router_async_is_atomic_under_concurrent_tasks(clear_pages_state):
    async def slow_home_layout():
        # Force an await inside the guarded region (via ``get_layouts()``)
        # so a concurrent task can slip past the pages guard while this
        # one is still building ``validation_layout``.
        await asyncio.sleep(0.05)
        return html.Div("home")

    app = Dash(use_pages=True, pages_folder="")
    dash.register_page("home_page", path="/", layout=slow_home_layout)
    app.layout = html.Div([dash.page_container])
    app._use_async = True

    router_async = _grab_before_request(app)

    async def wrapped():
        await router_async()
        # Snapshot the state at the moment this task's call returns.
        # Before the fix, a task that raced past the guard would return
        # here with ``validation_layout`` still unset.
        return (
            [k for k in app.callback_map if ROUTER_OUTPUT_ID in k],
            getattr(app, "validation_layout", None),
        )

    async def run_two_racing_tasks():
        return await asyncio.gather(wrapped(), wrapped(), return_exceptions=True)

    results = asyncio.run(run_two_racing_tasks())

    for r in results:
        assert not isinstance(
            r, Exception
        ), f"router_async raised under concurrent callers: {r!r}"

    for router_entries, vlayout in results:
        assert router_entries, (
            "A task returned from router_async before the router callback "
            "was registered."
        )
        assert vlayout is not None, (
            "A task returned from router_async before validation_layout "
            "was built. Before the fix, a raced-in task would return here "
            "while the winning task was still awaiting ``get_layouts()``."
        )

    router_entries = [k for k in app.callback_map if ROUTER_OUTPUT_ID in k]
    assert len(router_entries) == 1
