from dash import Dash, Input, Output, html
from dash.exceptions import PreventUpdate


def test_rdif001_sandbox_allow_scripts(dash_duo):
    app = Dash(__name__)

    N_OUTPUTS = 50

    app.layout = html.Div(
        [html.Button("click me", id="btn")]
        + [html.Div(id="output-{}".format(i)) for i in range(N_OUTPUTS)]
    )

    @app.callback(
        [Output("output-{}".format(i), "children") for i in range(N_OUTPUTS)],
        [Input("btn", "n_clicks")],
    )
    def update_output(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return ["{}={}".format(i, i + n_clicks) for i in range(N_OUTPUTS)]

    @app.server.after_request
    def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
        return response

    dash_duo.start_server(app)

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_element("#output-0").text == "0=1"

    assert dash_duo.get_logs() == []

    iframe = """
        <!DOCTYPE html>
    <html>
    <iframe src="{0}" sandbox="allow-scripts">
    </iframe>
    </html>
    """

    html_content = iframe.format(dash_duo.server_url)

    dash_duo.driver.get("data:text/html;charset=utf-8," + html_content)

    dash_duo.driver.switch_to.frame(0)

    assert dash_duo.get_logs() == []

    dash_duo.find_element("#btn").click()
    dash_duo.wait_for_text_to_equal("#output-0", "0=1")

    assert dash_duo.get_logs() == []
