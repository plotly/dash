"""
WebSocket set_props and get_props tests.

Tests:
- set_props streaming during long-running callback
- get_prop reads current component value
- async set_prop method
"""

import asyncio
from dash import Dash, html, Input, Output
from dash._callback_context import set_props
from dash.exceptions import PreventUpdate


def test_ws030_set_props_streaming(dash_duo):
    """Test that set_props streams updates during callback execution."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Start", id="btn"),
            html.Div("0%", id="progress"),
            html.Div("waiting", id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def long_task(n):
        if not n:
            raise PreventUpdate

        for i in range(1, 6):
            set_props("progress", {"children": f"{i * 20}%"})
            await asyncio.sleep(0.1)

        return "Done"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#progress", "0%")
    dash_duo.wait_for_text_to_equal("#result", "waiting")

    dash_duo.find_element("#btn").click()

    # Should see progress updates and final result
    dash_duo.wait_for_text_to_equal("#result", "Done", timeout=10)
    # Final progress should be 100%
    dash_duo.wait_for_text_to_equal("#progress", "100%")

    assert dash_duo.get_logs() == []


def test_ws031_set_props_multiple_components(dash_duo):
    """Test set_props updating multiple components during callback."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update All", id="btn"),
            html.Div("A: initial", id="output-a"),
            html.Div("B: initial", id="output-b"),
            html.Div("C: initial", id="output-c"),
            html.Div("result", id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def update_all(n):
        if not n:
            raise PreventUpdate

        set_props("output-a", {"children": f"A: updated {n}"})
        await asyncio.sleep(0.05)
        set_props("output-b", {"children": f"B: updated {n}"})
        await asyncio.sleep(0.05)
        set_props("output-c", {"children": f"C: updated {n}"})

        return f"All updated {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#output-a", "A: updated 1", timeout=10)
    dash_duo.wait_for_text_to_equal("#output-b", "B: updated 1")
    dash_duo.wait_for_text_to_equal("#output-c", "C: updated 1")
    dash_duo.wait_for_text_to_equal("#result", "All updated 1")

    assert dash_duo.get_logs() == []


def test_ws032_set_props_with_complex_values(dash_duo):
    """Test set_props with various value types."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Test Values", id="btn"),
            html.Div(id="text-output"),
            html.Div(id="number-output"),
            html.Div(id="list-output"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def test_values(n):
        if not n:
            raise PreventUpdate

        # String
        set_props("text-output", {"children": "Hello World"})
        await asyncio.sleep(0.02)

        # Number as string
        set_props("number-output", {"children": str(42)})
        await asyncio.sleep(0.02)

        # List of strings
        set_props("list-output", {"children": ["Item 1", " - ", "Item 2"]})

        return "Values set"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#text-output", "Hello World", timeout=10)
    dash_duo.wait_for_text_to_equal("#number-output", "42")
    dash_duo.wait_for_text_to_equal("#list-output", "Item 1 - Item 2")
    dash_duo.wait_for_text_to_equal("#result", "Values set")

    assert dash_duo.get_logs() == []


def test_ws033_set_props_sync_callback(dash_duo):
    """Test set_props in synchronous callback with WebSocket."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Sync Update", id="btn"),
            html.Div("before", id="side-effect"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    def sync_update(n):
        if not n:
            raise PreventUpdate

        # set_props should work in sync callback too
        set_props("side-effect", {"children": f"Side effect {n}"})
        return f"Result {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#result", "Result 1", timeout=10)
    dash_duo.wait_for_text_to_equal("#side-effect", "Side effect 1")

    assert dash_duo.get_logs() == []


def test_ws034_get_prop_reads_value(dash_duo):
    """Test that get_prop can read current component values."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Div("Source Value", id="source"),
            html.Button("Read", id="btn"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def read_prop(n):
        if not n:
            raise PreventUpdate

        from dash import ctx

        ws = ctx.get_websocket
        if ws:
            value = await ws.get_prop("source", "children")
            return f"Read: {value}"
        return "No WebSocket"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#result", "Read: Source Value", timeout=10)

    assert dash_duo.get_logs() == []


def test_ws035_websocket_set_prop_method(dash_duo):
    """Test using ws.set_prop() method directly."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Set via WS", id="btn"),
            html.Div("original", id="target"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def set_via_ws(n):
        if not n:
            raise PreventUpdate

        from dash import ctx

        ws = ctx.get_websocket
        if ws:
            await ws.set_prop("target", "children", f"Set via WebSocket {n}")
            return "Set complete"
        return "No WebSocket"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#target", "Set via WebSocket 1", timeout=10)
    dash_duo.wait_for_text_to_equal("#result", "Set complete")

    assert dash_duo.get_logs() == []


def test_ws036_set_props_dict_component_id(dash_duo):
    """Test set_props with dict component ID (pattern matching)."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update", id="btn"),
            html.Div("initial", id={"type": "output", "index": 0}),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def update_with_dict_id(n):
        if not n:
            raise PreventUpdate

        set_props({"type": "output", "index": 0}, {"children": f"Updated {n}"})
        return f"Done {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    # Use attribute selector for the dict ID
    dash_duo.wait_for_text_to_equal(
        '[id=\'{"index":0,"type":"output"}\']', "Updated 1", timeout=10
    )
    dash_duo.wait_for_text_to_equal("#result", "Done 1")

    assert dash_duo.get_logs() == []
