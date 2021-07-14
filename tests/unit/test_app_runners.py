import os
import sys
import requests
import pytest

import dash
from dash import html


def test_threaded_server_smoke(dash_thread_server):
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("click me", id="clicker"),
            html.Div(id="output", children="hello thread"),
        ]
    )
    dash_thread_server(app, debug=True, use_reloader=False, use_debugger=True)
    r = requests.get(dash_thread_server.url)
    assert r.status_code == 200, "the threaded server is reachable"
    assert 'id="react-entry-point"' in r.text, "the entrypoint is present"


@pytest.mark.skipif(
    sys.version_info < (3,), reason="requires python3 for process testing"
)
def test_process_server_smoke(dash_process_server):
    cwd = os.getcwd()
    this_dir = os.path.dirname(__file__)
    assets_dir = os.path.abspath(os.path.join(this_dir, "..", "assets"))
    try:
        os.chdir(assets_dir)
        dash_process_server("simple_app")
        r = requests.get(dash_process_server.url)
        assert r.status_code == 200, "the server is reachable"
        assert 'id="react-entry-point"' in r.text, "the entrypoint is present"
    finally:
        os.chdir(cwd)
