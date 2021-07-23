import pytest
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


@pytest.mark.DCC776
def test_lich001_default(dash_dcc):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link(id="link1", href="/page-1"),
            dcc.Location(id="url", refresh=False),
            html.Div(id="content"),
        ]
    )
    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#link1", "/page-1")

    assert dash_dcc.get_logs() == []


@pytest.mark.DCC776
def test_lich002_children(dash_dcc):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Link(children="test children", id="link1", href="/page-1"),
            dcc.Location(id="url", refresh=False),
            html.Div(id="content"),
        ]
    )

    @app.callback(Output("content", "children"), [Input("link1", "children")])
    def display_children(children):
        return children

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#content", "test children")

    assert dash_dcc.get_logs() == []
