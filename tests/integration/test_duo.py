import pytest
from selenium.common.exceptions import TimeoutException

from dash import Dash, html


def test_duo001_wait_for_text_error(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([html.Div("Content", id="content")])
    dash_duo.start_server(app)

    with pytest.raises(TimeoutException) as err:
        dash_duo.wait_for_text_to_equal("#content", "Invalid", timeout=1.0)

    assert err.value.args[0] == "text -> Invalid not found within 1.0s, found: Content"

    with pytest.raises(TimeoutException) as err:
        dash_duo.wait_for_text_to_equal("#none", "None", timeout=1.0)

    assert err.value.args[0] == "text -> None not found within 1.0s, #none not found"

    with pytest.raises(TimeoutException) as err:
        dash_duo.wait_for_contains_text("#content", "invalid", timeout=1.0)

    assert (
        err.value.args[0]
        == "text -> invalid not found inside element within 1.0s, found: Content"
    )

    with pytest.raises(TimeoutException) as err:
        dash_duo.wait_for_contains_text("#none", "none", timeout=1.0)

    assert (
        err.value.args[0]
        == "text -> none not found inside element within 1.0s, #none not found"
    )
