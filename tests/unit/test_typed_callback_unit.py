"""Unit tests for typed_callback - no browser required."""
import dash
from dash import Input, Output, State, typed_callback, callback


def test_typed_callback_returns_callable():
    """Test that typed_callback returns a callable decorator."""
    decorator = typed_callback(Output("output", "children"), Input("input", "value"))
    assert callable(decorator)


def test_typed_callback_decorates_function():
    """Test that typed_callback can decorate a function."""
    @typed_callback(Output("output", "children"), Input("input", "value"))
    def my_callback(value):
        return f"Value: {value}"
    
    assert callable(my_callback)
    assert my_callback.__name__ == "my_callback"


def test_typed_callback_signature_matches_callback():
    """Test that typed_callback has the same signature as callback."""
    import inspect
    
    typed_sig = inspect.signature(typed_callback)
    callback_sig = inspect.signature(callback)
    
    # Both should have the same parameters
    assert typed_sig.parameters.keys() == callback_sig.parameters.keys()


def test_typed_callback_with_multiple_inputs():
    """Test typed_callback with multiple inputs."""
    @typed_callback(
        Output("output", "children"),
        Input("input1", "value"),
        Input("input2", "value"),
    )
    def multi_input_callback(val1, val2):
        return f"{val1} + {val2}"
    
    assert callable(multi_input_callback)


def test_typed_callback_with_state():
    """Test typed_callback with State."""
    @typed_callback(
        Output("output", "children"),
        Input("input", "value"),
        State("state", "value"),
    )
    def callback_with_state(input_val, state_val):
        return f"{input_val} - {state_val}"
    
    assert callable(callback_with_state)


def test_typed_callback_with_multiple_outputs():
    """Test typed_callback with multiple outputs."""
    @typed_callback(
        Output("output1", "children"),
        Output("output2", "children"),
        Input("input", "value"),
    )
    def multi_output_callback(value):
        return value, f"Copy: {value}"
    
    assert callable(multi_output_callback)


def test_typed_callback_preserves_docstring():
    """Test that typed_callback preserves the wrapped function's docstring."""
    @typed_callback(Output("output", "children"), Input("input", "value"))
    def documented_callback(value):
        """This is a documented callback."""
        return value
    
    assert documented_callback.__doc__ == "This is a documented callback."


def test_typed_callback_with_prevent_initial_call():
    """Test typed_callback with prevent_initial_call parameter."""
    @typed_callback(
        Output("output", "children"),
        Input("input", "value"),
        prevent_initial_call=True,
    )
    def callback_no_initial(value):
        return value
    
    assert callable(callback_no_initial)


def test_typed_callback_with_background_params():
    """Test that typed_callback accepts background callback parameters."""
    # Just test that the decorator accepts these parameters
    # Full background callback testing requires integration tests
    decorator = typed_callback(
        Output("output", "children"),
        Input("input", "value"),
        background=False,
        interval=1000,
    )
    assert callable(decorator)


def test_typed_callback_module_export():
    """Test that typed_callback is properly exported from dash module."""
    assert hasattr(dash, "typed_callback")
    assert dash.typed_callback is typed_callback
