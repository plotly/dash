from flask import jsonify
import requests
import pytest

from dash import Dash, Input, Output, html, hooks, set_props


@pytest.fixture(scope="module", autouse=True)
def hook_cleanup():
    yield
    hooks._ns["layout"] = []
    hooks._ns["setup"] = []
    hooks._ns["route"] = []
    hooks._ns["error"] = []
    hooks._ns["callback"] = []


def test_hook001_layout(dash_duo):
    @hooks.layout
    def on_layout(layout):
        return [html.Div("Header", id="header")] + layout

    app = Dash()
    app.layout = [html.Div("Body", id="body")]

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#header", "Header")
    dash_duo.wait_for_text_to_equal("#body", "Body")


def test_hook002_setup():
    setup_title = None

    @hooks.setup
    def on_setup(app: Dash):
        nonlocal setup_title
        setup_title = app.title

    app = Dash(title="setup-test")
    app.layout = html.Div("setup")

    assert setup_title == "setup-test"


def test_hook003_route(dash_duo):
    @hooks.route(methods=("POST",))
    def hook_route():
        return jsonify({"success": True})

    app = Dash()
    app.layout = html.Div("hook route")

    dash_duo.start_server(app)
    response = requests.post(f"{dash_duo.server_url}/hook_route")
    data = response.json()
    assert data["success"]


def test_hook004_error(dash_duo):
    @hooks.error
    def on_error(error):
        set_props("error", {"children": str(error)})

    app = Dash()
    app.layout = [html.Button("start", id="start"), html.Div(id="error")]

    @app.callback(Input("start", "n_clicks"), prevent_initial_call=True)
    def on_click(_):
        raise Exception("hook error")

    dash_duo.start_server(app)
    dash_duo.wait_for_element("#start").click()
    dash_duo.wait_for_text_to_equal("#error", "hook error")


def test_hook005_callback(dash_duo):
    @hooks.callback(
        Output("output", "children"),
        Input("start", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_hook_cb(n_clicks):
        return f"clicked {n_clicks}"

    app = Dash()
    app.layout = [
        html.Button("start", id="start"),
        html.Div(id="output"),
    ]

    dash_duo.start_server(app)
    dash_duo.wait_for_element("#start").click()
    dash_duo.wait_for_text_to_equal("#output", "clicked 1")
