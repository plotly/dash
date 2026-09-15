"""Browser integration tests for streaming callbacks over HTTP (NDJSON)."""
import asyncio
import time

from dash import (
    Dash,
    Input,
    Output,
    Patch,
    html,
    no_update,
    set_props,
)
from dash.testing.wait import until


def test_stst001_stream_progressive_render(dash_duo):
    """Intermediate yields render before the stream completes."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="out", children="idle"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        # Each step stays up well past the driver's 0.5s poll interval, so
        # the wait below cannot miss it.
        yield "step-1"
        await asyncio.sleep(1.0)
        yield "step-2"
        await asyncio.sleep(1.0)
        yield "done"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    # Each yield renders while the callback is still running.
    dash_duo.wait_for_text_to_equal("#out", "step-1")
    dash_duo.wait_for_text_to_equal("#out", "step-2")
    dash_duo.wait_for_text_to_equal("#out", "done")
    assert dash_duo.get_logs() == []


def test_stst002_stream_patch_appends_once(dash_duo):
    """Patch yields apply exactly once (token streaming)."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="out", children=""),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        yield "->"
        for token in ["alpha", "beta", "gamma"]:
            await asyncio.sleep(0.2)
            patch = Patch()
            patch += token
            yield patch

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    # Exact concatenation catches both double-apply and dropped frames.
    dash_duo.wait_for_text_to_equal("#out", "->alphabetagamma")
    # Give any straggler updates a chance to (incorrectly) re-apply.
    time.sleep(0.5)
    assert dash_duo.find_element("#out").text == "->alphabetagamma"
    assert dash_duo.get_logs() == []


def test_stst003_stream_multi_output_and_set_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="a", children=""),
            html.Div(id="b", children=""),
            html.Div(id="side", children=""),
        ]
    )

    @app.callback(
        Output("a", "children"),
        Output("b", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        yield "a1", no_update
        await asyncio.sleep(0.3)
        set_props("side", {"children": "from-set-props"})
        yield no_update, "b1"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#a", "a1")
    dash_duo.wait_for_text_to_equal("#b", "b1")
    dash_duo.wait_for_text_to_equal("#side", "from-set-props")
    assert dash_duo.get_logs() == []


def test_stst004_stream_triggers_downstream_callback(dash_duo):
    """The final streamed value triggers dependent callbacks."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="out", children=""),
            html.Div(id="downstream", children=""),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        yield "one"
        await asyncio.sleep(0.2)
        yield "two"

    @app.callback(
        Output("downstream", "children"),
        Input("out", "children"),
        prevent_initial_call=True,
    )
    def downstream(value):
        return f"saw: {value}"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#downstream", "saw: two")
    assert dash_duo.get_logs() == []


def test_stst005_stream_error_shows_in_devtools(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="out", children=""),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        yield "before-error"
        raise ValueError("stream blew up")

    dash_duo.start_server(app, debug=True, use_reloader=False, use_debugger=True)
    dash_duo.find_element("#btn").click()
    # The frame before the error stays applied.
    dash_duo.wait_for_text_to_equal("#out", "before-error")
    # And the error surfaces in the devtools error count.
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "1")


def test_stst006_stream_loading_state(dash_duo):
    """The callback stays in loading state for the whole stream."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="out", children="idle"),
        ]
    )

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_cb(n):
        yield "working"
        await asyncio.sleep(1.5)
        yield "finished"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#out", "working")
    # An intermediate frame rendered but the callback is still running:
    # the loading state stays on (document title shows "Updating...").
    until(lambda: dash_duo.driver.title == "Updating...", timeout=3)
    assert dash_duo.redux_state_is_loading
    dash_duo.wait_for_text_to_equal("#out", "finished")
    # After the terminal frame the loading state clears.
    until(lambda: dash_duo.driver.title != "Updating...", timeout=3)
    assert not dash_duo.redux_state_is_loading
    assert dash_duo.get_logs() == []


def test_stst020_multiplexed_transport_over_shared_storage(dash_duo):
    """Streaming over the multiplexed transport (shared storage enabled).

    Exercises the whole multiplexed path in a real browser: the renderer echoes
    the signed endId, the server derives the connection id from it, pumps frames
    onto that topic, and the single downlink relays them back. If the endId did
    not verify end to end, the uplink would fall back to inline NDJSON (which the
    stream client rejects) and the downlink would 403, so nothing would render.
    Two callbacks share the one downlink, so this also covers multiplexing.
    """
    from dash._shared_storage import LocalSharedStorage

    app = Dash(__name__, shared_storage=LocalSharedStorage())
    app.layout = html.Div(
        [
            html.Button("Start", id="btn", n_clicks=0),
            html.Div(id="a", children="idle"),
            html.Div(id="b", children="idle"),
        ]
    )

    @app.callback(
        Output("a", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_a(n):
        yield "a1"
        await asyncio.sleep(0.4)
        yield "a2"

    @app.callback(
        Output("b", "children"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    async def stream_b(n):
        yield "b1"
        await asyncio.sleep(0.4)
        yield "b2"

    dash_duo.start_server(app)
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#a", "a2")
    dash_duo.wait_for_text_to_equal("#b", "b2")


def _downlink_connections(app):
    """Record the endIds the downlink is polled with: the SharedWorker gives one
    browser one connection (keyed on the first tab's endId), however many tabs
    it has."""
    from flask import request

    seen = set()

    @app.server.before_request
    def _record():
        if request.path.endswith("_dash-update-component"):
            body = request.get_json(silent=True) or {}
            if "streamDownlink" in body:
                seen.add(request.args.get("endId"))

    return seen


def _open_tab(dash_duo):
    dash_duo.driver.switch_to.new_window("tab")
    dash_duo.driver.get(dash_duo.server_url)


def test_stst010_many_tabs_share_one_downlink(dash_duo):
    """Browsers cap connections per host (~6); with the downlink hosted in a
    SharedWorker, eight streaming tabs share one and all keep streaming."""
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="out", children="idle")])

    @app.callback(Output("out", "children"), Input("out", "id"))
    async def stream_cb(_):
        for i in range(120):
            yield f"tick {i}"
            await asyncio.sleep(0.5)

    connections = _downlink_connections(app)
    dash_duo.start_server(app)
    dash_duo.wait_for_contains_text("#out", "tick")
    for _ in range(7):
        _open_tab(dash_duo)
        # Every new tab streams -- the sixth and later would stall with a
        # downlink per tab.
        dash_duo.wait_for_contains_text("#out", "tick")
    assert len(connections) == 1  # one shared downlink for the whole browser
    assert dash_duo.get_logs() == []


def test_stst011_closing_a_tab_cancels_its_stream(dash_duo):
    """A tab closing while others keep the shared downlink open cancels that
    tab's callback server-side instead of running it to completion."""
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="out", children="idle")])
    events = []

    @app.callback(Output("out", "children"), Input("out", "id"))
    async def stream_cb(_):
        try:
            for i in range(120):
                yield f"tick {i}"
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            events.append("cancelled")
            raise

    dash_duo.start_server(app)
    dash_duo.wait_for_contains_text("#out", "tick")
    first = dash_duo.driver.current_window_handle
    _open_tab(dash_duo)
    dash_duo.wait_for_contains_text("#out", "tick")

    dash_duo.driver.close()  # the second tab goes away
    dash_duo.driver.switch_to.window(first)
    until(lambda: events == ["cancelled"], timeout=10)
    # The surviving tab keeps streaming on the shared downlink.
    before = dash_duo.find_element("#out").text
    until(lambda: dash_duo.find_element("#out").text != before, timeout=5)
    assert dash_duo.get_logs() == []
