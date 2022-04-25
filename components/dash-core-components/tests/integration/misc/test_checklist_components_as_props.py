from dash import Dash, dcc, html


def test_mccap001_checklist_components_labels(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div([
        dcc.Checklist(
            [
                {'label': html.H2('H2 label'), 'value': 'h2'},
                {'label': html.A('Link in checklist', href='#'), 'value': 'a'}
            ],
            id="checklist"
        ),
    ])

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal('#checklist h2', 'H2 label')
    dash_dcc.wait_for_text_to_equal('#checklist a', 'Link in checklist')
