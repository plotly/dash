from dash import Dash, dcc, html


def test_mdcap001_dcc_components_as_props(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Checklist(
                [
                    {"label": html.H2("H2 label"), "value": "h2"},
                    {"label": html.A("Link in checklist", href="#"), "value": "a"},
                ],
                id="checklist",
            ),
            dcc.RadioItems(
                [
                    {"label": html.H3("on"), "value": "on"},
                    {"label": html.P("off"), "value": "off"},
                ],
                id="radio-items",
            ),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#checklist h2", "H2 label")
    dash_dcc.wait_for_text_to_equal("#checklist a", "Link in checklist")

    dash_dcc.wait_for_text_to_equal("#radio-items h3", "on")
    dash_dcc.wait_for_text_to_equal("#radio-items p", "off")
