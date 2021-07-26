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

    @app.callback(Output("content", "children"), [Input("url", "pathname")])
    def display_children(children):
        return children

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#link1").click()

    dash_dcc.wait_for_text_to_equal("#content", "/google.com")

    assert dash_dcc.get_logs() == []


@pytest.mark.DCC782
def test_lipa002_path(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link(
                children="Absolute Path",
                id="link1",
                href="https://google.com",
                refresh=True,
            ),
            dcc.Location(id="url", refresh=False),
        ]
    )
    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#link1").click()

    location = dash_dcc.driver.execute_script(
        """
        return window.location.href
        """
    )

    assert location == "https://www.google.com/"

    assert dash_dcc.get_logs() == []
