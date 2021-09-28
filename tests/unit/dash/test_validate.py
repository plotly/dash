import pytest

from dash import Output
from dash.html import Div
from dash.exceptions import InvalidCallbackReturnValue
from dash._validate import fail_callback_output


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
