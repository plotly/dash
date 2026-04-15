"""Type compliance tests for callback with strict mypy/pyright settings."""
import os
import sys

import pytest  # type: ignore

from .test_typing import format_template_and_save, run_module


callback_template = """
from dash import Dash, html, dcc, callback, Input, Output, State

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

strict_mypy_template = """# mypy: disallow-untyped-defs
# mypy: disallow-untyped-calls
# mypy: disallow-untyped-decorators
from dash import Dash, html, dcc, callback, Input, Output, State

app = Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='input', value=''),
    html.Div(id='output'),
])

{0}
"""


valid_callback_single = """
@callback(Output('output1', 'children'), Input('input1', 'value'))
def update_output(value: str) -> str:
    return f"You typed: {value}"
"""

valid_callback_multi_input = """
@callback(
    Output('output1', 'children'),
    Input('input1', 'value'),
    Input('input2', 'value')
)
def update_output(val1: str, val2: str) -> str:
    return f"{val1} and {val2}"
"""

valid_callback_with_state = """
@callback(
    Output('output1', 'children'),
    Input('btn', 'n_clicks'),
    State('input1', 'value')
)
def update_output(n_clicks: int | None, state_value: str) -> str:
    if n_clicks is None:
        return "Not clicked"
    return f"Clicked {n_clicks} times with {state_value}"
"""

valid_callback_multi_output = """
@callback(
    Output('output1', 'children'),
    Output('output2', 'children'),
    Input('input1', 'value')
)
def update_outputs(value: str) -> tuple[str, str]:
    return f"First: {value}", f"Second: {value}"
"""

strict_mode_callback = """
@callback(Output('output', 'children'), Input('input', 'value'))
def my_callback(value: str) -> str:
    '''Fully typed callback function.'''
    return f"Result: {value}"
"""

complex_return_types = """
from typing import Union

@callback(
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
        (valid_callback_single, 0),
        (valid_callback_multi_input, 0),
        (valid_callback_with_state, 0),
        (valid_callback_multi_output, 0),
        (complex_return_types, 0),
    ],
)
def test_typi_callback_basic(typing_module, callback_code, expected_status, tmp_path):
    """Test that callback passes type checking in normal mode."""
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(callback_template, codefile, callback_code)

    output, error, status = run_module(codefile, typing_module)
    assert (
        status == expected_status
    ), f"Status: {status}\nOutput: {output}\nError: {error}\nCode: {code}\nModule: {typing_module}"


@pytest.mark.parametrize("typing_module", typing_modules)
def test_typi_callback_strict_mode(typing_module, tmp_path):
    """Test that callback works with strict mypy/pyright settings."""
    codefile = os.path.join(tmp_path, "code.py")
    code = format_template_and_save(strict_mypy_template, codefile, strict_mode_callback)

    output, error, status = run_module(codefile, typing_module)
    assert status == 0, (
        f"callback should pass strict type checking.\n"
        f"Status: {status}\nOutput: {output}\nError: {error}\n"
        f"Code: {code}\nModule: {typing_module}"
    )


@pytest.mark.parametrize("typing_module", typing_modules)
def test_typi_callback_preserves_signature(typing_module, tmp_path):
    """Test that callback preserves function signatures for type inference."""
    code = """
from dash import callback, Input, Output, html, Dash

app = Dash(__name__)
app.layout = html.Div([html.Div(id='in'), html.Div(id='out')])

@callback(Output('out', 'children'), Input('in', 'children'))
def my_func(value: str) -> int:
    return len(value)

# The decorated function should still have its original signature
result = my_func("test")  # Should return int
"""

    codefile = os.path.join(tmp_path, "code.py")
    with open(codefile, "w") as f:
        f.write(code)

    output, error, status = run_module(codefile, typing_module)

    assert status == 0, (
        f"callback should preserve function signature.\n"
        f"Status: {status}\nOutput: {output}\nError: {error}\n"
        f"Module: {typing_module}"
    )


@pytest.mark.parametrize("typing_module", typing_modules)
def test_typi_callback_with_none_values(typing_module, tmp_path):
    """Test callback with Optional types."""
    code = """
from dash import Dash, html, dcc, callback, Input, Output

app = Dash(__name__)
app.layout = html.Div([
    dcc.Input(id='input', value=''),
    html.Button('Click', id='btn'),
    html.Div(id='output'),
])

@callback(
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
        f"callback should handle Optional types.\n"
        f"Status: {status}\nOutput: {output}\nError: {error}\n"
        f"Module: {typing_module}"
    )
