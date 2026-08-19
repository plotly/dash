"""
WebSocket callback dispatch tests: async callbacks run on the event loop, sync
callbacks run on the shared threadpool.

Tests:
- Many long-lived async (persistent-style) callbacks do not exhaust the worker
  threadpool, so regular callbacks still respond (thread-exhaustion regression).
- A synchronous persistent (no-output) callback warns at registration.
"""

import asyncio

import pytest

from dash import Dash, html, Input, Output, ctx, set_props
from dash.exceptions import PreventUpdate


def test_ws050_async_callbacks_do_not_exhaust_threadpool(dash_duo):
    """Many long-lived async callbacks must not starve regular callbacks.

    On the old dispatch, every async callback ran via ``asyncio.run`` inside a
    worker thread, so a long-lived (never-returning) async callback pinned one of
    the ``max_workers=4`` threads for the whole connection. Five of them filled the
    pool and wedged regular callbacks ("Loading…"). Async callbacks now run as tasks
    on the connection event loop, so they cost ~nothing and the threadpool stays
    free for sync callbacks.
    """
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    n_long = 6  # > default max_workers (4)

    app.layout = html.Div(
        [
            html.Button("Start long tasks", id="start", n_clicks=0),
            html.Button("Regular", id="reg-btn", n_clicks=0),
            html.Div("idle", id="reg-out"),
            *[html.Div("idle", id=f"long-{i}") for i in range(n_long)],
        ]
    )

    def make_long_callback(i):
        @app.callback(
            Output(f"long-{i}", "children"),
            Input("start", "n_clicks"),
            prevent_initial_call=True,
        )
        async def _long(n):
            ws = ctx.websocket
            set_props(f"long-{i}", {"children": "running"})
            # Long-lived: loops for ~12s, yielding the loop on every iteration.
            for _ in range(60):
                if ws and ws.is_shutdown:
                    raise PreventUpdate
                await asyncio.sleep(0.2)
            return "done"

    for i in range(n_long):
        make_long_callback(i)

    # A regular synchronous callback that must keep responding while the long
    # async callbacks are running.
    @app.callback(
        Output("reg-out", "children"),
        Input("reg-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def regular(n):
        return f"ok {n}"

    dash_duo.start_server(app)

    # Kick off all the long-lived async callbacks.
    dash_duo.find_element("#start").click()
    # They should all reach the "running" state (would not all start on dev with
    # only 4 worker threads if they pinned threads).
    for i in range(n_long):
        dash_duo.wait_for_text_to_equal(f"#long-{i}", "running", timeout=10)

    # The regular callback must still respond promptly while the long tasks run.
    dash_duo.find_element("#reg-btn").click()
    dash_duo.wait_for_text_to_equal("#reg-out", "ok 1", timeout=5)

    assert dash_duo.get_logs() == []


def test_ws051_sync_persistent_callback_warns():
    """A synchronous persistent (no-output) callback warns at registration.

    Registered on a local app (not the global registry) so it can't leak phantom
    callbacks into later tests.
    """
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    with pytest.warns(RuntimeWarning, match="persistent=True"):

        @app.callback(
            Input("trigger", "n_clicks"),
            persistent=True,
            websocket=True,
        )
        def _sync_persistent(n):  # pragma: no cover - never executed
            set_props("out", {"children": "x"})


def test_ws052_async_persistent_callback_does_not_warn(recwarn):
    """An async persistent (no-output) callback must not warn."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    @app.callback(
        Input("trigger2", "n_clicks"),
        persistent=True,
        websocket=True,
    )
    async def _async_persistent(n):  # pragma: no cover - never executed
        set_props("out", {"children": "x"})

    assert not [w for w in recwarn.list if issubclass(w.category, RuntimeWarning)]
