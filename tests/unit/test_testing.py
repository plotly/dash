from dash.testing import ignore_register_page
from dash import register_page


def test_tst001_ignore_register_page():
    with ignore_register_page():
        register_page("/")
