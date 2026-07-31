"""Shared storage wired into real Dash apps, exercised through the callback
dispatch pipeline.

Shared storage has no clientside surface, so an HTTP dispatch through the real
``/_dash-update-component`` route exercises the same path a browser click would.
Every scenario runs against all three backends (Local always; Diskcache always;
Redis when one is reachable) via the ``storage_factory`` fixture, so the app
sees identical behavior regardless of backend.
"""
import json
import os
import uuid
from functools import partial

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


@pytest.fixture(params=["local", "diskcache", "redis"])
def storage_factory(request, tmp_path):
    """A factory that builds fresh backend handles onto one shared store.

    Each call returns a new instance pointing at the same underlying store
    (same namespace / directory / key prefix), so a test can stand up two app
    instances that genuinely share state. All handles are closed at teardown.
    """
    kind = request.param
    if kind == "local":
        make = partial(LocalSharedStorage, namespace=f"itest-{uuid.uuid4().hex[:12]}")
    elif kind == "diskcache":
        make = partial(DiskcacheSharedStorage, directory=str(tmp_path / "ss"))
    else:
        if not _redis_available():
            pytest.skip("no Redis reachable at REDIS_URL")
        make = partial(
            RedisSharedStorage,
            url=REDIS_URL,
            key_prefix=f"dash:itest:{uuid.uuid4().hex[:12]}",
        )

    created = []

    def factory():
        storage = make()
        created.append(storage)
        return storage

    yield factory
    for storage in created:
        storage.close()


def _dispatch(app, output_id, input_id, prop="children", value=1):
    """POST one callback through the real dispatch route; return its response."""
    body = {
        "output": f"{output_id}.{prop}",
        "outputs": {"id": output_id, "property": prop},
        "inputs": [{"id": input_id, "property": "n_clicks", "value": value}],
        "changedPropIds": [f"{input_id}.n_clicks"],
    }
    resp = app.server.test_client().post("/_dash-update-component", json=body)
    return resp


def _dispatch_ok(app, output_id, input_id, **kwargs):
    resp = _dispatch(app, output_id, input_id, **kwargs)
    assert resp.status_code == 200, resp.get_data(as_text=True)
    return json.loads(resp.get_data(as_text=True))["response"][output_id]["children"]


def test_kv_roundtrip_in_callback(storage_factory):
    """A callback writes then reads its own value, visible on the app handle."""
    storage = storage_factory()
    app = Dash(__name__, shared_storage=storage)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def cb(n):
        ctx.shared_storage.set("hits", n)
        return f"stored {ctx.shared_storage.get('hits')}"

    assert _dispatch_ok(app, "out", "btn", value=3) == "stored 3"
    assert storage.get("hits") == 3


def test_state_shared_across_two_callbacks(storage_factory):
    """One callback writes; a different callback reads the same key."""
    storage = storage_factory()
    app = Dash(__name__, shared_storage=storage)
    app.layout = html.Div(
        [
            html.Button(id="writer-btn"),
            html.Div(id="writer-out"),
            html.Button(id="reader-btn"),
            html.Div(id="reader-out"),
        ]
    )

    @app.callback(Output("writer-out", "children"), Input("writer-btn", "n_clicks"))
    def write(_n):
        ctx.shared_storage.set("msg", {"greeting": "hello"})
        return "written"

    @app.callback(Output("reader-out", "children"), Input("reader-btn", "n_clicks"))
    def read(_n):
        return (ctx.shared_storage.get("msg") or {}).get("greeting", "nothing")

    # Reader sees nothing before the writer runs, the shared value after.
    assert _dispatch_ok(app, "reader-out", "reader-btn") == "nothing"
    assert _dispatch_ok(app, "writer-out", "writer-btn") == "written"
    assert _dispatch_ok(app, "reader-out", "reader-btn") == "hello"


def test_state_persists_across_dispatches(storage_factory):
    """A shared counter accumulates across independent callback requests."""
    storage = storage_factory()
    app = Dash(__name__, shared_storage=storage)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def bump(_n):
        count = ctx.shared_storage.get("count", 0) + 1
        ctx.shared_storage.set("count", count)
        return str(count)

    assert _dispatch_ok(app, "out", "btn") == "1"
    assert _dispatch_ok(app, "out", "btn") == "2"
    assert _dispatch_ok(app, "out", "btn") == "3"
    assert storage.get("count") == 3


def test_two_apps_share_state(storage_factory):
    """Two separate Dash apps on the same backend store see each other's writes
    -- the multi-worker / multi-instance case."""
    writer_storage = storage_factory()
    reader_storage = storage_factory()

    writer_app = Dash(__name__, shared_storage=writer_storage)
    writer_app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    reader_app = Dash(__name__, shared_storage=reader_storage)
    reader_app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @writer_app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def write(_n):
        ctx.shared_storage.set("cross", [1, 2, 3])
        return "written"

    @reader_app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def read(_n):
        return json.dumps(ctx.shared_storage.get("cross"))

    assert _dispatch_ok(writer_app, "out", "btn") == "written"
    assert _dispatch_ok(reader_app, "out", "btn") == "[1, 2, 3]"


def test_shared_storage_disabled_raises_in_callback():
    """With shared_storage=None, touching ctx.shared_storage errors the callback
    (dispatch returns non-200) and the app handle raises directly."""
    app = Dash(__name__, shared_storage=None)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def cb(_n):
        return ctx.shared_storage.get("x")

    assert _dispatch(app, "out", "btn").status_code != 200
    with pytest.raises(SharedStorageError):
        app.shared_storage  # noqa: B018


def test_default_shared_storage_is_enabled():
    app = Dash(__name__)
    assert isinstance(app.shared_storage, LocalSharedStorage)
    app.shared_storage.close()
