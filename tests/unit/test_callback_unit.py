"""Unit tests for callback decorator behavior - no browser required."""
import inspect

import dash
from dash import Input, Output, State, callback


def test_callback_returns_callable():
    """Test that callback returns a callable decorator."""
    decorator = callback(Output("output", "children"), Input("input", "value"))
    assert callable(decorator)


def test_callback_decorates_function():
    """Test that callback can decorate a function."""

    @callback(Output("output", "children"), Input("input", "value"))
    def my_callback(value):
        return f"Value: {value}"

    assert callable(my_callback)
    assert my_callback.__name__ == "my_callback"


def test_callback_signature_includes_typed_options():
    """Test that callback exposes the expected decorator keyword arguments."""
    sig = inspect.signature(callback)

    expected = {
        "background",
        "interval",
        "progress",
        "progress_default",
        "running",
        "cancel",
        "manager",
        "cache_args_to_ignore",
        "cache_ignore_triggered",
        "on_error",
        "api_endpoint",
        "optional",
        "hidden",
    }
    assert expected.issubset(set(sig.parameters))


def test_callback_with_multiple_inputs():
    """Test callback with multiple inputs."""

    @callback(
        Output("output", "children"),
        Input("input1", "value"),
        Input("input2", "value"),
    )
    def multi_input_callback(val1, val2):
        return f"{val1} + {val2}"

    assert callable(multi_input_callback)


def test_callback_with_state():
    """Test callback with State."""

    @callback(
        Output("output", "children"),
        Input("input", "value"),
        State("state", "value"),
    )
    def callback_with_state(input_val, state_val):
        return f"{input_val} - {state_val}"

    assert callable(callback_with_state)


def test_callback_with_multiple_outputs():
    """Test callback with multiple outputs."""

    @callback(
        Output("output1", "children"),
        Output("output2", "children"),
        Input("input", "value"),
    )
    def multi_output_callback(value):
        return value, f"Copy: {value}"

    assert callable(multi_output_callback)


def test_callback_preserves_docstring():
    """Test that callback preserves the wrapped function's docstring."""

    @callback(Output("output", "children"), Input("input", "value"))
    def documented_callback(value):
        """This is a documented callback."""
        return value

    assert documented_callback.__doc__ == "This is a documented callback."


def test_callback_with_prevent_initial_call():
    """Test callback with prevent_initial_call parameter."""

    @callback(
        Output("output", "children"),
        Input("input", "value"),
        prevent_initial_call=True,
    )
    def callback_no_initial(value):
        return value

    assert callable(callback_no_initial)


def test_callback_with_background_params():
    """Test that callback accepts background callback parameters."""
    decorator = callback(
        Output("output", "children"),
        Input("input", "value"),
        background=False,
        interval=1000,
    )
    assert callable(decorator)


def test_callback_module_export():
    """Test that callback is properly exported from dash module."""
    assert hasattr(dash, "callback")
    assert dash.callback is callback
