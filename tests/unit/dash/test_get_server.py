from dash import Dash, get_server


def test_get_server():
    app = Dash()
    server = get_server()
    assert app.server == server


def test_get_server_deferred():
    app = Dash(server=False)
    server = get_server()
    app.init_app(server)
    assert app.server == server
