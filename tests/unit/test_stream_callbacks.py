"""Unit tests for stream=True callbacks - no browser required."""
import asyncio
import contextvars
import json

import pytest

from dash import Dash, Input, Output, Patch, callback, html, no_update, set_props
from dash._callback import GLOBAL_CALLBACK_LIST, GLOBAL_CALLBACK_MAP
from dash._streaming import sync_iter_asyncgen
from dash.exceptions import (
    BackgroundCallbackError,
    PreventUpdate,
    StreamCallbackError,
)


def make_body(output_id, prop, input_id="btn"):
    return {
        "output": f"{output_id}.{prop}",
        "outputs": {"id": output_id, "property": prop},
        "inputs": [{"id": input_id, "property": "n_clicks", "value": 1}],
        "changedPropIds": [f"{input_id}.n_clicks"],
    }


def post_stream(app, body):
    """POST a callback request and return the parsed NDJSON frames."""
    client = app.server.test_client()
    resp = client.post("/_dash-update-component", json=body)
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type") == "application/x-ndjson"
    data = resp.get_data(as_text=True)
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def test_stcb001_stream_requires_generator():
    with pytest.raises(StreamCallbackError, match="must be a generator"):

        @callback(Output("stcb001", "children"), Input("in", "value"), stream=True)
        def not_a_generator(value):
            return value


def test_stcb002_generator_requires_stream():
    with pytest.raises(StreamCallbackError, match="stream=True"):

        @callback(Output("stcb002", "children"), Input("in", "value"))
        def a_generator(value):
            yield value


def test_stcb003_stream_incompatible_kwargs():
    with pytest.raises(BackgroundCallbackError):

        @callback(
            Output("stcb003a", "children"),
            Input("in", "value"),
            stream=True,
            background=True,
        )
        def bg(value):
            yield value

    with pytest.raises(StreamCallbackError, match="mcp_enabled"):

        @callback(
            Output("stcb003b", "children"),
            Input("in", "value"),
            stream=True,
            mcp_enabled=True,
        )
        def mcp(value):
            yield value

    with pytest.raises(StreamCallbackError, match="api_endpoint"):

        @callback(
            Output("stcb003c", "children"),
            Input("in", "value"),
            stream=True,
            api_endpoint="/stream",
        )
        def api(value):
            yield value


def test_stcb004_stream_not_clientside():
    app = Dash(__name__)
    with pytest.raises(StreamCallbackError, match="clientside"):
        app.clientside_callback(
            "function(v) { return v; }",
            Output("stcb004", "children"),
            Input("in", "value"),
            stream=True,
        )


def test_stcb005_sync_generator_warns():
    with pytest.warns(RuntimeWarning, match="synchronous generator"):

        @callback(Output("stcb005", "children"), Input("in", "value"), stream=True)
        def sync_gen(value):
            yield value


def test_stcb006_async_generator_no_warning(recwarn):
    @callback(Output("stcb006", "children"), Input("in", "value"), stream=True)
    async def async_gen(value):
        yield value

    assert not [w for w in recwarn.list if issubclass(w.category, RuntimeWarning)]


def test_stcb007_stream_flag_in_spec_and_map():
    @callback(Output("stcb007", "children"), Input("in", "value"), stream=True)
    async def async_gen(value):
        yield value

    spec = [s for s in GLOBAL_CALLBACK_LIST if s["output"] == "stcb007.children"][-1]
    assert spec["stream"] is True
    assert GLOBAL_CALLBACK_MAP["stcb007.children"]["stream"] is True

    @callback(Output("stcb007b", "children"), Input("in", "value"))
    def regular(value):
        return value

    spec = [s for s in GLOBAL_CALLBACK_LIST if s["output"] == "stcb007b.children"][-1]
    assert spec["stream"] is False


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_stcb008_flask_ndjson_frames():
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="btn"), html.Div(id="out"), html.Div(id="side")]
    )

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"), stream=True)
    def stream_cb(n):
        yield "start"
        patch = Patch()
        patch += " token"
        set_props("side", {"children": "side-value"})
        yield patch
        yield "final"

    frames = post_stream(app, make_body("out", "children"))
    assert frames[0] == {"multi": True, "response": {"out": {"children": "start"}}}
    # Patch value serialized with set_props folded into the same frame,
    # and cleared so it is not resent with the next frame.
    assert frames[1]["sideUpdate"] == {"side": {"children": "side-value"}}
    assert (
        frames[1]["response"]["out"]["children"]["__dash_patch_update"]
        == "__dash_patch_update"
    )
    assert frames[2] == {"multi": True, "response": {"out": {"children": "final"}}}
    assert frames[3] == {"done": True}


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_stcb009_stream_error_frame():
    app = Dash(__name__)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"), stream=True)
    def err_cb(n):
        yield "one"
        raise ValueError("boom")

    frames = post_stream(app, make_body("out", "children"))
    assert frames[0]["response"] == {"out": {"children": "one"}}
    assert frames[1]["done"] is True
    assert "boom" in frames[1]["error"]["message"]


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_stcb010_stream_on_error_handler():
    app = Dash(__name__)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    def handle(err):
        return f"handled: {err}"

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        stream=True,
        on_error=handle,
    )
    def err_cb(n):
        yield "one"
        raise ValueError("boom")

    frames = post_stream(app, make_body("out", "children"))
    assert frames[0]["response"] == {"out": {"children": "one"}}
    assert frames[1]["response"] == {"out": {"children": "handled: boom"}}
    assert frames[2] == {"done": True}


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_stcb011_prevent_update_and_no_update_yields():
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="btn"), html.Div(id="out"), html.Div(id="out2")]
    )

    @app.callback(
        Output("out", "children"),
        Output("out2", "children"),
        Input("btn", "n_clicks"),
        stream=True,
    )
    def stream_cb(n):
        yield "a", no_update
        yield no_update, no_update  # produces no frame
        yield no_update, "b"
        raise PreventUpdate  # ends the stream cleanly

    body = {
        "output": "..out.children...out2.children..",
        "outputs": [
            {"id": "out", "property": "children"},
            {"id": "out2", "property": "children"},
        ],
        "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
        "changedPropIds": ["btn.n_clicks"],
    }
    frames = post_stream(app, body)
    assert frames[0]["response"] == {"out": {"children": "a"}}
    assert frames[1]["response"] == {"out2": {"children": "b"}}
    assert frames[2] == {"done": True}
    assert len(frames) == 3


def test_stcb012_sync_iter_asyncgen():
    var = contextvars.ContextVar("stcb012")

    async def agen():
        var.set("inside")
        for i in range(3):
            await asyncio.sleep(0.001)
            # The whole generator runs on a single task, so context set
            # inside persists across steps.
            assert var.get() == "inside"
            yield i

    assert list(sync_iter_asyncgen(agen())) == [0, 1, 2]


def test_stcb013_sync_iter_asyncgen_error_propagates():
    async def agen():
        yield 1
        raise RuntimeError("kaput")

    gen = sync_iter_asyncgen(agen())
    assert next(gen) == 1
    with pytest.raises(RuntimeError, match="kaput"):
        next(gen)


def test_stcb014_sync_iter_asyncgen_close_cancels():
    closed = []

    async def agen():
        try:
            for i in range(100):
                await asyncio.sleep(0.001)
                yield i
        finally:
            closed.append(True)

    gen = sync_iter_asyncgen(agen())
    assert next(gen) == 0
    gen.close()
    # The consumer task is cancelled on a background thread; give it a moment.
    for _ in range(100):
        if closed:
            break
        import time

        time.sleep(0.01)
    assert closed == [True]
