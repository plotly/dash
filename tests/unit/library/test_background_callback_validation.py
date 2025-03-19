import pytest

from dash.exceptions import BackgroundCallbackError
from dash.dependencies import Input, Output
from dash._validate import validate_background_callbacks


def test_circular_background_callback_progress():
    callback_map = {
        "side": {
            "output": [Output("side-progress", "children")],
            "raw_inputs": [Input("progress", "children")],
        },
        "background": {
            "output": [Output("result", "children")],
            "raw_inputs": [
                Input("click", "n_clicks"),
                Input("side-progress", "children"),
            ],
            "background": {"progress": [Output("progress", "children")]},
        },
    }

    with pytest.raises(BackgroundCallbackError):

        validate_background_callbacks(callback_map)
