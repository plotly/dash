import json

from dash import Dash, html, dcc, Output, Input
from dash.exceptions import PreventUpdate


sample_dropdown_options = [
    {"label": "New York City", "value": "NYC"},
    {"label": "Montreal", "value": "MTL"},
    {"label": "San Francisco", "value": "SF"},
]


def test_ddro001_remove_option_single(dash_dcc):
    dropdown_options = sample_dropdown_options

    app = Dash(__name__)
    value = "SF"

    app.layout = html.Div(
        [
            dcc.Dropdown(
                options=dropdown_options,
                value=value,
                searchable=False,
                id="dropdown",
            ),
            html.Button("Remove option", id="remove"),
            html.Div(id="value-output"),
        ]
    )

    @app.callback(Output("dropdown", "options"), [Input("remove", "n_clicks")])
    def on_click(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return sample_dropdown_options[:-1]

    @app.callback(Output("value-output", "children"), [Input("dropdown", "value")])
    def on_change(val):
        if not val:
            raise PreventUpdate
        return val or "None"

    dash_dcc.start_server(app)
    btn = dash_dcc.wait_for_element("#remove")
    btn.click()

    dash_dcc.wait_for_text_to_equal("#value-output", "None")


def test_ddro002_remove_option_multi(dash_dcc):
    dropdown_options = sample_dropdown_options

    app = Dash(__name__)
    value = ["MTL", "SF"]

    app.layout = html.Div(
        [
            dcc.Dropdown(
                options=dropdown_options,
                value=value,
                multi=True,
                id="dropdown",
                searchable=False,
            ),
            html.Button("Remove option", id="remove"),
            html.Div(id="value-output"),
        ]
    )

    @app.callback(Output("dropdown", "options"), [Input("remove", "n_clicks")])
    def on_click(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        return sample_dropdown_options[:-1]

    @app.callback(Output("value-output", "children"), [Input("dropdown", "value")])
    def on_change(val):
        return json.dumps(val)

    dash_dcc.start_server(app)
    btn = dash_dcc.wait_for_element("#remove")
    btn.click()

    dash_dcc.wait_for_text_to_equal("#value-output", '["MTL"]')
