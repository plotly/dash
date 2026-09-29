"""Shared storage in real Dash apps, driven through a browser with dash_duo.

Each test starts a real server and clicks real buttons. The core scenario proves
the app-facing contract: one callback writes shared state, a *different* callback
reads it back, and the value survives across independent requests. The same
scenario runs on each backend (Local, Diskcache, Redis-when-reachable) to prove
the wiring end to end.
"""
import os
import uuid

import pytest

from dash import Dash, Input, Output, ctx, html
from dash._shared_storage import (
    DiskcacheSharedStorage,
    LocalSharedStorage,
    RedisSharedStorage,
    SharedStorageError,
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")


def _redis_available():
    try:
        import redis  # pylint: disable=import-outside-toplevel

        client = redis.Redis.from_url(REDIS_URL)
        client.ping()
        client.close()
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def _counter_app(storage):
    """A two-callback app: 'bump' increments a shared counter, 'read' (a separate
    callback) shows the current shared value."""
    app = Dash(__name__, shared_storage=storage)
    app.layout = html.Div(
        [
            html.Button("bump", id="bump"),
            html.Button("read", id="read"),
            html.Div(id="count"),
            html.Div(id="readout"),
        ]
    )

    @app.callback(
        Output("count", "children"),
        Input("bump", "n_clicks"),
        prevent_initial_call=True,
    )
    def bump(_n):
        total = ctx.shared_storage.get("count", 0) + 1
        ctx.shared_storage.set("count", total)
        return str(total)

    @app.callback(
        Output("readout", "children"),
        Input("read", "n_clicks"),
        prevent_initial_call=True,
    )
    def read(_n):
        return f"count={ctx.shared_storage.get('count', 0)}"

    return app


def _drive_counter(dash_duo):
    """Click through the counter scenario and assert on the rendered DOM."""
    dash_duo.find_element("#bump").click()
    dash_duo.wait_for_text_to_equal("#count", "1")
    dash_duo.find_element("#bump").click()
    dash_duo.wait_for_text_to_equal("#count", "2")

    # A different callback reads the value the bump callback wrote.
    dash_duo.find_element("#read").click()
    dash_duo.wait_for_text_to_equal("#readout", "count=2")

    assert dash_duo.get_logs() == []


def test_counter_shared_across_callbacks_local(dash_duo):
    dash_duo.start_server(
        _counter_app(LocalSharedStorage(namespace=f"duo-{uuid.uuid4().hex[:12]}"))
    )
    _drive_counter(dash_duo)


def test_counter_shared_across_callbacks_local_persist(dash_duo, tmp_path):
    dash_duo.start_server(
        _counter_app(
            LocalSharedStorage(
                namespace=f"duo-{uuid.uuid4().hex[:12]}",
                mode="persist",
                path=str(tmp_path / "ss"),
            )
        )
    )
    _drive_counter(dash_duo)
    # The write-through store landed on disk.
    assert (tmp_path / "ss" / "index.msgpack").exists()


def test_counter_shared_across_callbacks_diskcache(dash_duo, tmp_path):
    dash_duo.start_server(
        _counter_app(DiskcacheSharedStorage(directory=str(tmp_path / "ss")))
    )
    _drive_counter(dash_duo)


def test_counter_shared_across_callbacks_redis(dash_duo):
    if not _redis_available():
        pytest.skip("no Redis reachable at REDIS_URL")
    dash_duo.start_server(
        _counter_app(
            RedisSharedStorage(
                url=REDIS_URL, key_prefix=f"dash:duo:{uuid.uuid4().hex[:12]}"
            )
        )
    )
    _drive_counter(dash_duo)


def test_disabled_shared_storage_errors_the_callback(dash_duo):
    """With shared_storage=None, a callback touching ctx.shared_storage fails;
    the app surfaces a callback error rather than updating the output."""
    app = Dash(__name__, shared_storage=None)
    app.layout = html.Div([html.Button("go", id="go"), html.Div(id="out")])

    @app.callback(
        Output("out", "children"), Input("go", "n_clicks"), prevent_initial_call=True
    )
    def cb(_n):
        return ctx.shared_storage.get("x")

    dash_duo.start_server(app)
    dash_duo.find_element("#go").click()
    # The output never fills in, and the server logged the SharedStorageError.
    dash_duo.wait_for_text_to_equal("#out", "")
    assert dash_duo.get_logs()  # an error was logged

    with pytest.raises(SharedStorageError):
        app.shared_storage  # noqa: B018
