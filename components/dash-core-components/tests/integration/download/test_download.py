import os
from dash import Dash, Input, Output, dcc, html

from dash.testing.wait import until


def test_dltx001_download_text(dash_dcc):
    text = "Hello, world!"
    filename = "hello.txt"
    # Create app.
    app = Dash(__name__, prevent_initial_callbacks=True)
    app.layout = html.Div([html.Button("Click", id="btn"), dcc.Download(id="download")])

    @app.callback(Output("download", "data"), Input("btn", "n_clicks"))
    def download(_):
        return dcc.send_string(text, filename)

    dash_dcc.start_server(app)

    # Check that there is nothing before clicking
    fp = os.path.join(dash_dcc.download_path, filename)
    assert not os.path.isfile(fp)

    dash_dcc.find_element("#btn").click()

    # Check that a file has been download, and that it's content matches the original text.
    until(lambda: os.path.exists(fp), 10)
    with open(fp, "r") as f:
        content = f.read()
    assert content == text

    assert dash_dcc.get_logs() == []
