"""Unit tests for streaming (generator) callbacks - no browser required."""
import asyncio
import contextvars
import json
import signal
import time

import pytest

from dash import Dash, Input, Output, Patch, callback, html, no_update, set_props
from dash._callback import GLOBAL_CALLBACK_LIST, GLOBAL_CALLBACK_MAP
from dash._stream_hub import apump_to_storage, install_stream_shutdown_handler
from dash._streaming import (
    StreamedCallbackResponse,
    _keepalive_frames,
    _shutdown,
    andjson_lines,
    keepalive_seconds,
    marker_ndjson_aiter,
    sync_iter_asyncgen,
)
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


def post_stream_raw(app, body):
    """POST a callback request and return the raw NDJSON body."""
    client = app.server.test_client()
    resp = client.post("/_dash-update-component", json=body)
    assert resp.status_code == 200
    assert resp.headers.get("Content-Type") == "application/x-ndjson"
    return resp.get_data(as_text=True)


def post_stream(app, body):
    """POST a callback request and return the parsed NDJSON frames."""
    data = post_stream_raw(app, body)
    return [json.loads(line) for line in data.splitlines() if line.strip()]


def test_stcb001_non_generator_is_not_streamed():
    @callback(Output("stcb001", "children"), Input("in", "value"))
    def not_a_generator(value):
        return value

    assert GLOBAL_CALLBACK_MAP["stcb001.children"]["stream"] is False


def test_stcb002_generator_streams_without_a_keyword():
    @callback(Output("stcb002", "children"), Input("in", "value"))
    async def a_generator(value):
        yield value

    assert GLOBAL_CALLBACK_MAP["stcb002.children"]["stream"] is True


def test_stcb003_stream_incompatible_kwargs():
    with pytest.raises(BackgroundCallbackError):

        @callback(
            Output("stcb003a", "children"),
            Input("in", "value"),
            background=True,
        )
        async def bg(value):
            yield value

    with pytest.raises(StreamCallbackError, match="mcp_enabled"):

        @callback(
            Output("stcb003b", "children"),
            Input("in", "value"),
            mcp_enabled=True,
        )
        async def mcp(value):
            yield value

    with pytest.raises(StreamCallbackError, match="api_endpoint"):

        @callback(
            Output("stcb003c", "children"),
            Input("in", "value"),
            api_endpoint="/stream",
        )
        async def api(value):
            yield value


def test_stcb005_sync_generator_forbidden():
    with pytest.raises(StreamCallbackError, match="synchronous generator"):

        @callback(Output("stcb005", "children"), Input("in", "value"))
        def sync_gen(value):
            yield value


def test_stcb006_async_generator_allowed(recwarn):
    @callback(Output("stcb006", "children"), Input("in", "value"))
    async def async_gen(value):
        yield value

    assert GLOBAL_CALLBACK_MAP["stcb006.children"]["stream"] is True
    assert not [w for w in recwarn.list if issubclass(w.category, RuntimeWarning)]


def test_stcb007_stream_wrapper_registered():
    @callback(Output("stcb007", "children"), Input("in", "value"))
    async def async_gen(value):
        yield value

    assert GLOBAL_CALLBACK_MAP["stcb007.children"]["stream"] is True

    # The client spec carries a server-inferred stream flag. The client still
    # detects streaming at runtime from the response (NDJSON content type /
    # stream frames); the scheduler reads this flag only to keep long-lived
    # streams out of its concurrent-request budget.
    spec = [s for s in GLOBAL_CALLBACK_LIST if s["output"] == "stcb007.children"][-1]
    assert spec["stream"] is True


def test_stcb008_flask_ndjson_frames():
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="btn"), html.Div(id="out"), html.Div(id="side")]
    )

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream_cb(n):
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


def test_stcb009_stream_error_frame():
    app = Dash(__name__)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def err_cb(n):
        yield "one"
        raise ValueError("boom")

    frames = post_stream(app, make_body("out", "children"))
    assert frames[0]["response"] == {"out": {"children": "one"}}
    assert frames[1]["done"] is True
    assert "boom" in frames[1]["error"]["message"]


def test_stcb010_stream_on_error_handler():
    app = Dash(__name__)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    def handle(err):
        return f"handled: {err}"

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        on_error=handle,
    )
    async def err_cb(n):
        yield "one"
        raise ValueError("boom")

    frames = post_stream(app, make_body("out", "children"))
    assert frames[0]["response"] == {"out": {"children": "one"}}
    assert frames[1]["response"] == {"out": {"children": "handled: boom"}}
    assert frames[2] == {"done": True}


def test_stcb011_prevent_update_and_no_update_yields():
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="btn"), html.Div(id="out"), html.Div(id="out2")]
    )

    @app.callback(
        Output("out", "children"),
        Output("out2", "children"),
        Input("btn", "n_clicks"),
    )
    async def stream_cb(n):
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
        time.sleep(0.01)
    assert closed == [True]


def test_stcb015_keepalive_seconds_normalization():
    assert keepalive_seconds(15000) == 15.0
    assert keepalive_seconds(None) is None
    assert keepalive_seconds(0) is None
    assert keepalive_seconds(-1) is None


def test_stcb016_flask_keepalive_between_slow_yields():
    app = Dash(__name__, stream_keepalive_interval=50)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream_cb(n):
        await asyncio.sleep(0.3)
        yield "start"
        await asyncio.sleep(0.3)
        yield "final"

    raw = post_stream_raw(app, make_body("out", "children"))
    # Blank keepalive lines while the callback is between yields.
    assert len([line for line in raw.splitlines() if not line.strip()]) >= 2
    # The frames themselves are unaffected.
    frames = [json.loads(line) for line in raw.splitlines() if line.strip()]
    assert frames[0]["response"] == {"out": {"children": "start"}}
    assert frames[1]["response"] == {"out": {"children": "final"}}
    assert frames[2] == {"done": True}


def test_stcb017_flask_keepalive_disabled():
    app = Dash(__name__, stream_keepalive_interval=None)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"))
    async def stream_cb(n):
        await asyncio.sleep(0.2)
        yield "only"

    raw = post_stream_raw(app, make_body("out", "children"))
    assert [line for line in raw.splitlines() if not line.strip()] == []


def test_stcb018_async_keepalive_does_not_cancel_source():
    async def agen():
        await asyncio.sleep(0.3)
        yield {"multi": True}
        await asyncio.sleep(0.3)
        yield {"done": True}

    async def collect():
        return [line async for line in andjson_lines(agen(), keepalive=0.05)]

    lines = asyncio.run(collect())
    assert lines.count("\n") >= 2
    # Holding the pending __anext__ across keepalives means both frames still
    # arrive; a bare wait_for would have cancelled the generator mid-step.
    assert [json.loads(line) for line in lines if line.strip()] == [
        {"multi": True},
        {"done": True},
    ]


def test_stcb020_async_keepalive_over_sync_generator():
    """marker_ndjson_aiter with is_async=False: sync generator, ASGI backend."""

    def frames():
        time.sleep(0.3)
        yield {"multi": True}
        yield {"done": True}

    marker = StreamedCallbackResponse(
        frames(), is_async=False, ctx=contextvars.copy_context()
    )

    async def collect():
        return [line async for line in marker_ndjson_aiter(marker, keepalive=0.05)]

    lines = asyncio.run(collect())
    assert lines.count("\n") >= 2
    assert [json.loads(line) for line in lines if line.strip()] == [
        {"multi": True},
        {"done": True},
    ]


def test_stcb019_keepalive_frames_closes_generator_when_consumer_leaves():
    closed = []

    def frames():
        try:
            while True:
                yield {"multi": True}
        finally:
            closed.append(True)

    marker = StreamedCallbackResponse(
        frames(), is_async=False, ctx=contextvars.copy_context()
    )
    gen = _keepalive_frames(marker, 0.05)
    assert next(gen) == {"multi": True}
    gen.close()
    # The pump thread owns the generator, so cleanup happens once it notices
    # the stop flag rather than at the consumer's close().
    for _ in range(200):
        if closed:
            break
        time.sleep(0.01)
    assert closed == [True]


def test_stcb021_shutdown_flag_stops_keepalive_generator():
    """_shutdown event makes _keepalive_frames exit within one poll cycle."""
    from dash._streaming import _shutdown

    _shutdown.clear()

    def frames():
        while True:
            yield {"multi": True}
            time.sleep(0.05)

    marker = StreamedCallbackResponse(
        frames(), is_async=False, ctx=contextvars.copy_context()
    )
    gen = _keepalive_frames(marker, keepalive=60)
    assert next(gen) == {"multi": True}

    _shutdown.set()
    t0 = time.monotonic()
    remaining = list(gen)
    elapsed = time.monotonic() - t0
    _shutdown.clear()

    assert elapsed < 2, f"generator took {elapsed:.1f}s to stop (expected <2s)"
    assert len(remaining) <= 2


def test_stcb022_shutdown_active_streams_sets_flag_and_closes_subs():
    """shutdown_active_streams sets the _shutdown flag and closes subs."""
    from dash._streaming import _shutdown
    from dash._stream_hub import (
        _active_subscriptions,
        _registry_lock,
        shutdown_active_streams,
    )

    _shutdown.clear()

    class FakeSub:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    sub = FakeSub()
    with _registry_lock:
        _active_subscriptions.add(sub)

    try:
        shutdown_active_streams()
        assert _shutdown.is_set()
        assert sub.closed
    finally:
        _shutdown.clear()
        with _registry_lock:
            _active_subscriptions.discard(sub)


def test_stcb023_install_shutdown_handler_wraps_current_handler():
    """Installing over a foreign handler sets the flag, then chains to it."""
    saved = {sig: signal.getsignal(sig) for sig in (signal.SIGINT, signal.SIGTERM)}
    calls = []

    def foreign(sig, _frame):
        calls.append((sig, _shutdown.is_set()))

    try:
        signal.signal(signal.SIGINT, foreign)
        signal.signal(signal.SIGTERM, foreign)
        _shutdown.clear()

        install_stream_shutdown_handler()
        installed = signal.getsignal(signal.SIGINT)
        assert installed is not foreign

        installed(signal.SIGINT, None)
        assert _shutdown.is_set()
        assert calls == [(signal.SIGINT, True)]

        install_stream_shutdown_handler()
        assert signal.getsignal(signal.SIGINT) is installed
        assert signal.getsignal(signal.SIGTERM) is not foreign
    finally:
        _shutdown.clear()
        for sig, handler in saved.items():
            signal.signal(sig, handler)


def test_stcb024_cancelled_pump_publishes_terminal_error():
    """A pump cancelled by shutdown leaves a terminal error frame in the store."""
    published = []

    class FakeStorage:
        def publish(self, topic, message):
            published.append((topic, message))

    async def frames():
        yield {"multi": True, "response": {"out": {"children": 1}}}
        await asyncio.sleep(10)
        yield {"done": True}

    async def scenario():
        marker = StreamedCallbackResponse(
            frames(), is_async=True, ctx=contextvars.copy_context()
        )
        task = asyncio.ensure_future(
            apump_to_storage(FakeStorage(), "conn", "rid", marker)
        )
        await asyncio.sleep(0.05)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(scenario())
    assert [m["frame"] for _, m in published] == [
        {"multi": True, "response": {"out": {"children": 1}}},
        {
            "done": True,
            "error": {
                "message": "Streaming callback interrupted: "
                "the server shut down while it was running"
            },
        },
    ]
    assert all(m["rid"] == "rid" for _, m in published)
