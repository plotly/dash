"""Shared storage wired into a Dash app and reachable from a callback."""
import json
import uuid

import pytest

from dash import Dash, Input, Output, ctx, html
from dash._shared_storage import LocalSharedStorage, SharedStorageError


def _dispatch(app, output_id="out", prop="children", input_id="btn"):
    body = {
        "output": f"{output_id}.{prop}",
        "outputs": {"id": output_id, "property": prop},
        "inputs": [{"id": input_id, "property": "n_clicks", "value": 3}],
        "changedPropIds": [f"{input_id}.n_clicks"],
    }
    resp = app.server.test_client().post("/_dash-update-component", json=body)
    assert resp.status_code == 200
    return json.loads(resp.get_data(as_text=True))


def _app():
    # Unique namespace per app so tests don't share one owner/store.
    storage = LocalSharedStorage(namespace=f"itest-{uuid.uuid4().hex[:12]}")
    app = Dash(__name__, shared_storage=storage)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])
    return app, storage


def test_ctx_shared_storage_roundtrip_in_callback():
    app, storage = _app()

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def cb(n):
        ctx.shared_storage.set("hits", n)
        return f"stored {ctx.shared_storage.get('hits')}"

    out = _dispatch(app)
    assert out["response"]["out"]["children"] == "stored 3"
    # Value is visible on the app's storage handle outside the callback too.
    assert storage.get("hits") == 3
    storage.close()


def test_shared_storage_disabled_raises_in_callback():
    app = Dash(__name__, shared_storage=None)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    def cb(n):
        return ctx.shared_storage.get("x")

    # The callback error surfaces; storage access without a backend is rejected.
    with pytest.raises(SharedStorageError):
        app.shared_storage  # noqa: B018


def test_default_shared_storage_is_enabled():
    app = Dash(__name__)
    assert isinstance(app.shared_storage, LocalSharedStorage)
    app.shared_storage.close()
