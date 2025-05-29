import pytest

from dash import Output
from dash.html import Div
from dash.exceptions import InvalidCallbackReturnValue, DuplicateCallback
from dash._validate import fail_callback_output, validate_duplicate_output


@pytest.mark.parametrize(
    "val",
    [
        {0},
        [{1}, 1],
        [1, {2}],
        Div({3}),
        Div([{4}]),
        Div(style={5}),
        Div([1, {6}]),
        Div([1, Div({7})]),
        [Div({8}), 1],
        [1, Div({9})],
        [Div(Div({10}))],
        [Div(Div({11})), 1],
        [1, Div(Div({12}))],
        {"a": {13}},
        Div(style={"a": {14}}),
        Div(style=[{15}]),
        [1, Div(style=[{16}])],
    ],
)
def test_ddvl001_fail_handler_fails_correctly(val):
    if isinstance(val, list):
        outputs = [Output(f"id{i}", "children") for i in range(len(val))]
    else:
        outputs = Output("id", "children")

    with pytest.raises(InvalidCallbackReturnValue):
        fail_callback_output(val, outputs)


@pytest.mark.parametrize(
    "output, prevent_initial_call, config_prevent_initial_call, expect_error",
    [
        (Output("a", "a", allow_duplicate=True), True, False, False),
        (Output("a", "a", allow_duplicate=True), False, True, False),
        (Output("a", "a", allow_duplicate=True), True, True, False),
        (Output("a", "a", allow_duplicate=True), False, False, True),
        (Output("a", "a", allow_duplicate=True), "initial_duplicate", False, False),
        (Output("a", "a", allow_duplicate=True), False, "initial_duplicate", False),
        (Output("a", "a"), False, False, False),
    ],
)
def test_ddv002_allow_duplicate_validation(
    output, prevent_initial_call, config_prevent_initial_call, expect_error
):
    if expect_error:
        with pytest.raises(DuplicateCallback):
            validate_duplicate_output(
                output, prevent_initial_call, config_prevent_initial_call
            )
    else:
        validate_duplicate_output(
            output, prevent_initial_call, config_prevent_initial_call
        )
