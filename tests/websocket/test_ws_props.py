"""
WebSocket set_props and get_props tests.

Tests:
- set_props streaming during long-running callback
- get_prop reads current component value
- async set_prop method
- set_props with Patch objects (bug fix for component property updates)
- set_props with pattern-matching components triggering MATCH callbacks
"""

import asyncio
from dash import Dash, html, Input, Output, State, set_props, MATCH
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

        ws = ctx.websocket
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

        ws = ctx.websocket
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


def test_ws045_set_props_component_prop_children(dash_duo):
    """Test set_props updating component props like Div's children with component."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update Children", id="btn"),
            html.Div(id="container"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def update_children(n):
        if not n:
            raise PreventUpdate

        set_props(
            "container",
            {
                "children": html.Div(
                    [
                        html.Span(f"Updated {n}"),
                        html.B(" - Bold Text"),
                    ]
                )
            },
        )
        return f"Children updated {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#container span", "Updated 1", timeout=10)
    dash_duo.wait_for_text_to_equal("#container b", "- Bold Text")
    dash_duo.wait_for_text_to_equal("#result", "Children updated 1")

    assert dash_duo.get_logs() == []


def test_ws046_set_props_nested_component_children(dash_duo):
    """Test set_props with nested component in children prop."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update Nested", id="btn"),
            html.Div(id="wrapper"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def update_nested(n):
        if not n:
            raise PreventUpdate

        set_props(
            "wrapper",
            {
                "children": html.Div(
                    [
                        html.Ul(
                            [
                                html.Li(f"Item {n}.1"),
                                html.Li(f"Item {n}.2"),
                            ]
                        )
                    ]
                )
            },
        )
        return f"Nested updated {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal(
        "#wrapper ul li:first-child", "Item 1.1", timeout=10
    )
    dash_duo.wait_for_text_to_equal("#wrapper ul li:last-child", "Item 1.2")
    dash_duo.wait_for_text_to_equal("#result", "Nested updated 1")

    assert dash_duo.get_logs() == []


def test_ws047_set_props_children_with_list(dash_duo):
    """Test set_props with list of components wrapped in a single component."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update List", id="btn"),
            html.Div(id="list-container"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def update_list(n):
        if not n:
            raise PreventUpdate

        set_props(
            "list-container",
            {
                "children": html.Div(
                    [
                        html.Div(f"Item 1 - {n}"),
                        html.Div(f"Item 2 - {n}"),
                        html.Div(f"Item 3 - {n}"),
                    ]
                )
            },
        )
        return f"List updated {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#result", "List updated 1", timeout=10)
    assert "Item 1 - 1" in dash_duo.find_element("#list-container").text
    assert "Item 2 - 1" in dash_duo.find_element("#list-container").text
    assert "Item 3 - 1" in dash_duo.find_element("#list-container").text

    assert dash_duo.get_logs() == []


def test_ws047b_set_props_batch_many_updates(dash_duo):
    """Test that many rapid set_props calls are batched and all arrive correctly."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Update Many", id="btn"),
            *[html.Div("0", id=f"output-{i}") for i in range(10)],
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("btn", "n_clicks"))
    async def update_many(n):
        if not n:
            raise PreventUpdate

        # Rapid-fire set_props calls without any await between them
        # These should be batched together by the server
        for i in range(10):
            set_props(f"output-{i}", {"children": f"{n}"})

        return f"Done {n}"

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()

    # All outputs should be updated
    dash_duo.wait_for_text_to_equal("#result", "Done 1", timeout=10)
    for i in range(10):
        dash_duo.wait_for_text_to_equal(f"#output-{i}", "1")

    # Click again to verify batching works consistently
    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#result", "Done 2", timeout=10)
    for i in range(10):
        dash_duo.wait_for_text_to_equal(f"#output-{i}", "2")

    assert dash_duo.get_logs() == []


def test_ws048_set_props_dynamic_match_callback(dash_duo):
    """Test set_props injecting components with pattern-matching IDs that trigger MATCH callbacks."""
    app = Dash(__name__, backend="fastapi", websocket_callbacks=True)

    app.layout = html.Div(
        [
            html.Button("Add Component", id="add-btn"),
            html.Div(id="container"),
            html.Div("waiting", id="match-result"),
            html.Div(id="result"),
        ]
    )

    @app.callback(Output("result", "children"), Input("add-btn", "n_clicks"))
    async def add_component(n):
        if not n:
            raise PreventUpdate

        # Inject component with pattern-matching ID via set_props
        set_props(
            "container",
            {
                "children": html.Div(
                    [
                        html.Span("Hello"),
                        html.Button("Click me", id={"type": "dynamic", "index": 0}),
                    ]
                )
            },
        )
        return f"Component added {n}"

    @app.callback(
        Output("match-result", "children"),
        Input({"type": "dynamic", "index": MATCH}, "n_clicks"),
        State({"type": "dynamic", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def handle_dynamic_click(n_clicks, btn_id):
        if not n_clicks:
            raise PreventUpdate
        return f"Clicked button index {btn_id['index']} - {n_clicks} times"

    dash_duo.start_server(app)

    # Initial state
    dash_duo.wait_for_text_to_equal("#match-result", "waiting")

    # Add the dynamic component
    dash_duo.find_element("#add-btn").click()
    dash_duo.wait_for_text_to_equal("#result", "Component added 1", timeout=10)

    # Verify the component was added
    dash_duo.wait_for_text_to_equal("#container span", "Hello", timeout=5)

    # Click the dynamically added button with pattern-matching ID
    dash_duo.find_element('[id=\'{"index":0,"type":"dynamic"}\']').click()

    # Verify the MATCH callback fired
    dash_duo.wait_for_text_to_equal(
        "#match-result", "Clicked button index 0 - 1 times", timeout=10
    )

    # Click again to verify it continues to work
    dash_duo.find_element('[id=\'{"index":0,"type":"dynamic"}\']').click()
    dash_duo.wait_for_text_to_equal(
        "#match-result", "Clicked button index 0 - 2 times", timeout=10
    )

    assert dash_duo.get_logs() == []
