import pytest
import mock

import dash
from dash.exceptions import WildcardInLongCallback
from dash.dependencies import Input, Output, State, ALL, MATCH, ALLSMALLER


def test_wildcard_ids_no_allowed_in_long_callback():
    """
    @app.long_callback doesn't support wildcard dependencies yet. This test can
    be removed if wildcard support is added to @app.long_callback in the future.
    """
    app = dash.Dash(long_callback_manager=mock.Mock())

    # ALL
    with pytest.raises(WildcardInLongCallback):

        @app.long_callback(
            Output("output", "children"),
            Input({"type": "filter", "index": ALL}, "value"),
        )
        def callback(*args, **kwargs):
            pass

    # MATCH
    with pytest.raises(WildcardInLongCallback):

        @app.long_callback(
            Output({"type": "dynamic-output", "index": MATCH}, "children"),
            Input({"type": "dynamic-dropdown", "index": MATCH}, "value"),
            State({"type": "dynamic-dropdown", "index": MATCH}, "id"),
        )
        def callback(*args, **kwargs):
            pass

    # ALLSMALLER
    with pytest.raises(WildcardInLongCallback):

        @app.long_callback(
            Output({"type": "output-ex3", "index": MATCH}, "children"),
            Input({"type": "filter-dropdown-ex3", "index": MATCH}, "value"),
            Input({"type": "filter-dropdown-ex3", "index": ALLSMALLER}, "value"),
        )
        def callback(*args, **kwargs):
            pass
