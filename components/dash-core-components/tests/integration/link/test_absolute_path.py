import pytest
from dash import Dash, Input, Output, dcc, html


@pytest.mark.DCC782
def test_lipa001_path(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link("Relative Path", id="link1", href="google.com"),
            dcc.Location(id="url", refresh=False),
            html.Div(id="content"),
        ]
    )

    @app.callback(Output("content", "children"), Input("url", "pathname"))
    def display_children(children):
        return children

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#link1").click()

    dash_dcc.wait_for_text_to_equal("#content", "/google.com")

    assert dash_dcc.get_logs() == []


@pytest.mark.DCC782
def test_lipa002_path(dash_dcc):
    app = Dash(__name__)

    def extras(t):
        return f"""<!DOCTYPE html>
        <html><body>
        {t[::-1]}
        </body></html>
        """

    app.server.add_url_rule(
        "/extra/<string:t>",
        view_func=extras,
        endpoint="/extra/<string:t>",
        methods=["GET"],
    )

    app.layout = html.Div(
        [
            dcc.Link(
                children="Absolute Path",
                id="link1",
                href="/extra/eseehc",
                refresh=True,
            ),
            dcc.Location(id="url", refresh=False),
        ]
    )
    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#link1").click()

    location, text = dash_dcc.driver.execute_script(
        """
        return [window.location.href, document.body.textContent.trim()]
        """
    )

    assert location == dash_dcc.server.url + "/extra/eseehc"
    assert text == "cheese"

    assert dash_dcc.get_logs() == []
