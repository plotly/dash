import pytest
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


@pytest.mark.DCC774
def test_loca001_callbacks(dash_dcc):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Location(id="location", refresh=False),
            html.A("Anchor Link 1", href="#div"),
            html.Div(id="div"),
        ]
    )

    @app.callback(Output("div", "children"), [Input("location", "pathname")])
    def update_path(path):
        return path

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#div", "/")
