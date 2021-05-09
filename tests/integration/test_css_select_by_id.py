from __future__ import unicode_literals
import pytest

import dash
import dash_html_components as html
from dash._utils import css_escape


TEST_STRING_IDS = [
    "standard-sane-id",
    "!sane~ID:at>all?" "-",
    "-1a",
    "0abc",
    "{'a': 1, 'b': 2, 'c': [3, 4, 5]}",
    '"string-in-string-with-escape-characters"',
    "\u001fabc\u007f",
]

TEST_DICT_IDS = [
    {"a": 1, "b": "some-string", "c": False},
    {"type": "some-type", "index": 42},
]


@pytest.mark.parametrize("id", TEST_STRING_IDS)
def test_css_escape(dash_duo, id):
    assert dash_duo.driver.execute_script(
        "return CSS.escape({!r})".format(id)
    ) == css_escape(id)


@pytest.mark.parametrize(
    "id", TEST_STRING_IDS + TEST_DICT_IDS,
)
def test_found_by_css_selector(dash_duo, id):
    # This test also indirectly checks that output from the JavaScript stringify_id
    # function equals output from the corresponding Python function.
    app = dash.Dash(__name__)

    app.layout = html.Div(id=id)

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element_by_id(dash.stringify_id(id, escape_css=True))
    assert dash_duo.wait_for_element("#" + dash.stringify_id(id, escape_css=True))
