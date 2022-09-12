import pytest

from dash.exceptions import LongCallbackError
from dash.dependencies import Input, Output
from dash._validate import validate_long_callbacks


def test_circular_long_callback_progress():
    callback_map = {
        "side": {
            "output": [Output("side-progress", "children")],
            "raw_inputs": [Input("progress", "children")],
        },
        "long": {
            "output": [Output("result", "children")],
            "raw_inputs": [
                Input("click", "n_clicks"),
                Input("side-progress", "children"),
            ],
            "long": {"progress": [Output("progress", "children")]},
        },
    }

    with pytest.raises(LongCallbackError):

        validate_long_callbacks(callback_map)
