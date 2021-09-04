import contextlib

import pytest
import flask_talisman
from selenium.common.exceptions import NoSuchElementException

from dash import Dash, Input, Output, dcc, html


@contextlib.contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "add_hashes, hash_algorithm, expectation",
    [
        (False, None, pytest.raises(NoSuchElementException)),
        (True, "sha256", does_not_raise()),
        (True, "sha384", does_not_raise()),
        (True, "sha512", does_not_raise()),
        (True, "sha999", pytest.raises(ValueError)),
    ],
)
def test_incs001_csp_hashes_inline_scripts(
    dash_duo, add_hashes, hash_algorithm, expectation
):
    app = Dash(__name__)

    app.layout = html.Div(
        [dcc.Input(id="input_element", type="text"), html.Div(id="output_element")]
    )

    app.clientside_callback(
        """
        function(input) {
            return input;
        }
        """,
        Output("output_element", "children"),
        [Input("input_element", "value")],
    )

    with expectation:
        csp = {
            "default-src": "'self'",
            "script-src": ["'self'"]
            + (app.csp_hashes(hash_algorithm) if add_hashes else []),
        }

        flask_talisman.Talisman(
            app.server, content_security_policy=csp, force_https=False
        )

        dash_duo.start_server(app)

        dash_duo.find_element("#input_element").send_keys("xyz")
        assert dash_duo.wait_for_element("#output_element").text == "xyz"
