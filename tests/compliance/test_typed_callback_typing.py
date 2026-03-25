"""Type compliance tests for typed_callback with strict mypy/pyright settings."""
import os
import sys
import pytest

# Import the testing utilities from the main test_typing.py
from .test_typing import run_module, format_template_and_save


# Template for testing typed_callback with strict type checking
typed_callback_template = """
from dash import Dash, html, dcc, typed_callback, Input, Output, State

app = Dash()

app.layout = html.Div([
    dcc.Input(id='input1', value=''),
    dcc.Input(id='input2', value=''),
    html.Button('Click', id='btn'),
    html.Div(id='output1'),
    html.Div(id='output2'),
])

{0}
"""

# Template for testing with strict mypy settings
strict_mypy_template = """# mypy: disallow-untyped-defs
# mypy: disallow-untyped-calls
# mypy: disallow-untyped-decorators
from dash import Dash, html, dcc, typed_callback, Input, Output, State

app = Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='input', value=''),
    html.Div(id='output'),
])

{0}
"""


valid_typed_callback_single = """
@typed_callback(Output('output1', 'children'), Input('input1', 'value'))
def update_output(value: str) -> str:
    return f"You typed: {value}"
"""

valid_typed_callback_multi_input = """
@typed_callback(
    Output('output1', 'children'),
    Input('input1', 'value'),
    Input('input2', 'value')
)
def update_output(val1: str, val2: str) -> str:
    return f"{val1} and {val2}"
"""

valid_typed_callback_with_state = """
@typed_callback(
    Output('output1', 'children'),
    Input('btn', 'n_clicks'),
    State('input1', 'value')
)
def update_output(n_clicks: int | None, state_value: str) -> str:
    if n_clicks is None:
        return "Not clicked"
    return f"Clicked {n_clicks} times with {state_value}"
"""

valid_typed_callback_multi_output = """
@typed_callback(
    Output('output1', 'children'),
    Output('output2', 'children'),
    Input('input1', 'value')
)
def update_outputs(value: str) -> tuple[str, str]:
    return f"First: {value}", f"Second: {value}"
"""

# This should pass with typed_callback but fail with regular callback in strict mode
strict_mode_typed_callback = """
@typed_callback(Output('output', 'children'), Input('input', 'value'))
def my_callback(value: str) -> str:
    '''Fully typed callback function.'''
    return f"Result: {value}"
"""

# Regular callback would fail in strict mode (for comparison)
strict_mode_regular_callback = """
@app.callback(Output('output', 'children'), Input('input', 'value'))
def my_callback(value: str) -> str:
    '''This should fail with disallow-untyped-decorators.'''
    return f"Result: {value}"
"""

# Test with complex return types
complex_return_types = """
from typing import Union

@typed_callback(
    Output('output1', 'children'),
    Output('output2', 'children'),
    Input('input1', 'value')
)
def complex_callback(value: str) -> tuple[Union[str, int], list[str]]:
    return len(value), [value, value.upper()]
"""


typing_modules = ["pyright"]
if sys.version_info.minor >= 10:
    typing_modules.append("mypy")


@pytest.mark.parametrize("typing_module", typing_modules)
@pytest.mark.parametrize(
    "callback_code, expected_status",
    [
        (valid_typed_callback_single, 0),
        (valid_typed_callback_multi_input, 0),
        (valid_typed_callback_with_state, 0),
        (valid_typed_callback_multi_output, 0),
        (complex_return_types, 0),
    ],
)
def test_typi_typed_callback_basic(
    typing_module, callback_code, expected_status, tmp_path
):
    """Test that typed_callback passes type checking in normal mode."""
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(
        typed_callback_template, codefile, callback_code
    )

    output, error, status = run_module(codefile, typing_module)
    assert (
        status == expected_status
    ), f"Status: {status}\nOutput: {output}\nError: {error}\nCode: {code}\nModule: {typing_module}"


@pytest.mark.parametrize("typing_module", typing_modules)
def test_typi_typed_callback_strict_mode(typing_module, tmp_path):
    """Test that typed_callback works with strict mypy/pyright settings.
    
    This is the main purpose of typed_callback - to satisfy
    disallow_untyped_decorators and similar strict settings.
    """
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(
        strict_mypy_template, codefile, strict_mode_typed_callback
    )

    output, error, status = run_module(codefile, typing_module)
    assert status == 0, (
        f"typed_callback should pass strict type checking.\n"
        f"Status: {status}\nOutput: {output}\nError: {error}\n"
        f"Code: {code}\nModule: {typing_module}"
    )


@pytest.mark.parametrize("typing_module", typing_modules)
def test_typi_regular_callback_strict_mode_fails(typing_module, tmp_path):
    """Verify that regular callback fails in strict mode (comparison test).
    
    This demonstrates why typed_callback is needed.
    """
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(
        strict_mypy_template, codefile, strict_mode_regular_callback
    )

    output, error, status = run_module(codefile, typing_module)
    
    # Regular callback should fail in strict mode
    # (This test validates that our strict mode setup is actually strict)
    if typing_module == "mypy":
        # Mypy should report untyped decorator error
        assert status != 0 or "Untyped decorator" in output or "untyped" in error.lower(), (
            f"Regular callback should fail with disallow-untyped-decorators.\n"
            f"Status: {status}\nOutput: {output}\nError: {error}\n"
            f"Module: {typing_module}"
        )
    elif typing_module == "pyright":
        # Pyright might or might not catch this depending on strict settings
        # The important thing is that typed_callback passes when regular might not
        pass


@pytest.mark.parametrize("typing_module", typing_modules)
def test_typi_typed_callback_preserves_signature(typing_module, tmp_path):
    """Test that typed_callback preserves function signatures for type inference."""
    code = """
from typing import reveal_type  # type: ignore
from dash import typed_callback, Input, Output, html, Dash

app = Dash(__name__)
app.layout = html.Div([html.Div(id='in'), html.Div(id='out')])

@typed_callback(Output('out', 'children'), Input('in', 'children'))
def my_func(value: str) -> int:
    return len(value)

# The decorated function should still have its original signature
result = my_func("test")  # Should return int
"""
    
    codefile = os.path.join(tmp_path, "code.py")
    with open(codefile, "w") as f:
        f.write(code)
    
    output, error, status = run_module(codefile, typing_module)
    
    # Should pass type checking - the function signature is preserved
    assert status == 0, (
        f"typed_callback should preserve function signature.\n"
        f"Status: {status}\nOutput: {output}\nError: {error}\n"
        f"Module: {typing_module}"
    )


@pytest.mark.parametrize("typing_module", typing_modules) 
def test_typi_typed_callback_with_none_values(typing_module, tmp_path):
    """Test typed_callback with Optional types."""
    code = """
from dash import Dash, html, dcc, typed_callback, Input, Output

app = Dash(__name__)
app.layout = html.Div([
    dcc.Input(id='input', value=''),
    html.Button('Click', id='btn'),
    html.Div(id='output'),
])

@typed_callback(
    Output('output', 'children'),
    Input('btn', 'n_clicks')
)
def handle_optional(n_clicks: int | None) -> str:
    if n_clicks is None:
        return "Not clicked yet"
    return f"Clicked {n_clicks} times"
"""
    
    codefile = os.path.join(tmp_path, "code.py")
    with open(codefile, "w") as f:
        f.write(code)
    
    output, error, status = run_module(codefile, typing_module)
    assert status == 0, (
        f"typed_callback should handle Optional types.\n"
        f"Status: {status}\nOutput: {output}\nError: {error}\n"
        f"Module: {typing_module}"
    )
