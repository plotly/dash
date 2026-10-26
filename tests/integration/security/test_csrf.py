import flask

from dash import Dash, Input, Output, html


def test_csrf001_token_cookie_sent_as_header(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([html.Button("go", id="go"), html.Div(id="out")])

    @app.server.after_request
    def set_token(response):
        response.set_cookie("_csrf_token", "tok123")
        return response

    @app.callback(Output("out", "children"), Input("go", "n_clicks"))
    def echo(_):
        return flask.request.headers.get("X-CSRFToken", "missing")

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "tok123")
    assert dash_duo.get_logs() == []
