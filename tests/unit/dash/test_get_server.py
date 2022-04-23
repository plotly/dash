from dash import Dash, get_server, register_page

import flask


def test_get_server():
    app = Dash()
    server = get_server()
    assert app.server == server


def test_get_server_deferred():
    app = Dash(server=False)
    server = get_server()
    app.init_app(server)
    assert app.server == server


def test_flask_get_server():
    server = flask.Flask("flask_server")
    app = Dash(server=server)
    dash_server = get_server()
    assert app.server == dash_server == server


def test_get_server_pages():
    server = flask.Flask("flask_server")
    app = Dash(__name__, pages_folder="", server=False)
    app.init_app(server)
    dash_server = get_server()
    register_page("app1", path="/")
    register_page("app2")
    assert app.server == dash_server == server
