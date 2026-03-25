"""Integration tests for typed_callback functionality."""
import dash
from dash import Input, Output, State, dcc, html, typed_callback


def test_tcb001_basic_typed_callback(dash_duo):
    """Test that typed_callback works identically to callback for basic usage."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial"),
            html.Div(id="output-typed"),
            html.Div(id="output-regular"),
        ]
    )

    @typed_callback(Output("output-typed", "children"), Input("input", "value"))
    def update_typed(value):
        return f"Typed: {value}"

    @dash.callback(Output("output-regular", "children"), Input("input", "value"))
    def update_regular(value):
        return f"Regular: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output-typed", "Typed: initial")
    dash_duo.wait_for_text_to_equal("#output-regular", "Regular: initial")

    input_element = dash_duo.find_element("#input")
    dash_duo.clear_input(input_element)
    input_element.send_keys("test")

    dash_duo.wait_for_text_to_equal("#output-typed", "Typed: test")
    dash_duo.wait_for_text_to_equal("#output-regular", "Regular: test")

    assert not dash_duo.get_logs()


def test_tcb002_typed_callback_multi_input(dash_duo):
    """Test typed_callback with multiple inputs."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input1", value="Hello"),
            dcc.Input(id="input2", value="World"),
            html.Div(id="output"),
        ]
    )

    @typed_callback(
        Output("output", "children"),
        Input("input1", "value"),
        Input("input2", "value"),
    )
    def combine_inputs(val1, val2):
        return f"{val1} {val2}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "Hello World")

    input1 = dash_duo.find_element("#input1")
    dash_duo.clear_input(input1)
    input1.send_keys("Goodbye")

    dash_duo.wait_for_text_to_equal("#output", "Goodbye World")

    assert not dash_duo.get_logs()


def test_tcb003_typed_callback_with_state(dash_duo):
    """Test typed_callback with State dependencies."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input1", value="stored"),
            dcc.Input(id="input2", value="trigger"),
            html.Button("Submit", id="button"),
            html.Div(id="output"),
        ]
    )

    @typed_callback(
        Output("output", "children"),
        Input("button", "n_clicks"),
        State("input1", "value"),
        State("input2", "value"),
    )
    def update_with_state(n_clicks, state1, state2):
        if n_clicks is None:
            return "Not clicked"
        return f"Click {n_clicks}: {state1} + {state2}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "Not clicked")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#output", "Click 1: stored + trigger")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#output", "Click 2: stored + trigger")

    assert not dash_duo.get_logs()


def test_tcb004_typed_callback_multi_output(dash_duo):
    """Test typed_callback with multiple outputs."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="test"),
            html.Div(id="output1"),
            html.Div(id="output2"),
            html.Div(id="output3"),
        ]
    )

    @typed_callback(
        Output("output1", "children"),
        Output("output2", "children"),
        Output("output3", "children"),
        Input("input", "value"),
    )
    def update_multiple(value):
        return f"First: {value}", f"Second: {value}", f"Third: {value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output1", "First: test")
    dash_duo.wait_for_text_to_equal("#output2", "Second: test")
    dash_duo.wait_for_text_to_equal("#output3", "Third: test")

    input_element = dash_duo.find_element("#input")
    dash_duo.clear_input(input_element)
    input_element.send_keys("changed")

    dash_duo.wait_for_text_to_equal("#output1", "First: changed")
    dash_duo.wait_for_text_to_equal("#output2", "Second: changed")
    dash_duo.wait_for_text_to_equal("#output3", "Third: changed")

    assert not dash_duo.get_logs()


def test_tcb005_typed_callback_prevent_initial_call(dash_duo):
    """Test typed_callback with prevent_initial_call parameter."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial"),
            html.Div(id="output", children="default"),
        ]
    )

    @typed_callback(
        Output("output", "children"),
        Input("input", "value"),
        prevent_initial_call=True,
    )
    def update_no_initial(value):
        return f"Updated: {value}"

    dash_duo.start_server(app)
    # Should remain "default" because prevent_initial_call=True
    dash_duo.wait_for_text_to_equal("#output", "default")

    input_element = dash_duo.find_element("#input")
    input_element.send_keys("x")

    dash_duo.wait_for_text_to_equal("#output", "Updated: initialx")

    assert not dash_duo.get_logs()


def test_tcb006_typed_callback_mixed_with_regular(dash_duo):
    """Test that typed_callback and regular callback can coexist."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Div(id="output1"),
            html.Div(id="output2"),
            html.Div(id="output3"),
            html.Div(id="output4"),
        ]
    )

    # Using typed_callback (global style)
    @typed_callback(Output("output1", "children"), Input("input", "value"))
    def update_1(value):
        return f"Typed global: {value}"

    # Using dash.callback (global style)
    @dash.callback(Output("output2", "children"), Input("input", "value"))
    def update_2(value):
        return f"Regular global: {value}"

    # Using app.callback (app instance style)
    @app.callback(Output("output3", "children"), Input("input", "value"))
    def update_3(value):
        return f"App callback: {value}"

    # Another typed_callback
    @typed_callback(Output("output4", "children"), Input("input", "value"))
    def update_4(value):
        return f"Typed global 2: {value}"

    dash_duo.start_server(app)

    input_element = dash_duo.find_element("#input")
    input_element.send_keys("test")

    dash_duo.wait_for_text_to_equal("#output1", "Typed global: test")
    dash_duo.wait_for_text_to_equal("#output2", "Regular global: test")
    dash_duo.wait_for_text_to_equal("#output3", "App callback: test")
    dash_duo.wait_for_text_to_equal("#output4", "Typed global 2: test")

    assert not dash_duo.get_logs()


def test_tcb007_typed_callback_with_no_update(dash_duo):
    """Test typed_callback with no_update."""
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="0"),
            html.Div(id="output1"),
            html.Div(id="output2"),
        ]
    )

    @typed_callback(
        Output("output1", "children"),
        Output("output2", "children"),
        Input("input", "value"),
    )
    def selective_update(value):
        num = int(value) if value and value.isdigit() else 0
        if num % 2 == 0:
            return f"Even: {num}", dash.no_update
        else:
            return dash.no_update, f"Odd: {num}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output1", "Even: 0")

    input_element = dash_duo.find_element("#input")
    dash_duo.clear_input(input_element)
    input_element.send_keys("1")
    dash_duo.wait_for_text_to_equal("#output2", "Odd: 1")

    dash_duo.clear_input(input_element)
    input_element.send_keys("2")
    dash_duo.wait_for_text_to_equal("#output1", "Even: 2")

    assert not dash_duo.get_logs()
