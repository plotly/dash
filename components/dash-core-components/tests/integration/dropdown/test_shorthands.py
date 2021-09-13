from dash import Dash, dcc
from dash.dcc import Dropdown
from dash.html import Div

def test_ddsh001_dropdown_shorthand_properties(dash_dcc):
    app = Dash(__name__)
    app.layout = Div(
        [
            dcc.Dropdown(['a', 'b', 'c']),
            dcc.Dropdown(['a', 'b', 'c'], 'b'),
            dcc.Dropdown(['a', 3, 'c']),
            dcc.Dropdown(['a', 3, 'c'], 3),
            dcc.Dropdown(['a', 3, 'c', True, False]),
            dcc.Dropdown(['a', 3, 'c', True, False], False),
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element(".dash-dropdown")

    dash_dcc.percy_snapshot("ddsh001 - test_ddsh001_dropdown_shorthand_properties")
