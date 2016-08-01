import datetime
import time
import random

from dash.react import Dash
from dash_html_components import Div
from dash_core_components import Dropdown, Label

dash = Dash(__name__)

dash.layout = Div(id='wrapper', content=[
    Dropdown(id='source', options=[
        { 'value': 'a', 'label': 'Option a' },
        { 'value': 'b', 'label': 'Option b' }
    ]),
    Label(id='target', value='will update')
])


def update_target(dropdown_data):
    return {
        'value': dropdown_data['props']['value']
    }


dash.react('target', ['source'])(update_target)

if __name__ == "__main__":
    dash.run_server(
        port=8050,
        debug=True,
        component_suites=[
            'dash_core_components',
            'dash_html_components'
        ]
    )