import datetime
import time
import random

from dash.react import Dash
from dash_html_components import Div, Label
from dash_core_components import Dropdown

dash = Dash(__name__)

dash.layout = Div(id='wrapper', content=[
    Dropdown(id='source', options=[
        {'value': 'a', 'label': 'Option a'},
        {'value': 'b', 'label': 'Option b'}
    ], value='a'),
    Label(id='target')
])


def update_target(dropdown_data):
    return {
        'content': dropdown_data['value']
    }


dash.react('target', ['source'])(update_target)

dash.css.append_css({
    'external_url': (
        'https://rawgit.com/chriddyp/0247653a7c52feb4c48437e1c1837f75'
        '/raw/d4f178bc09f253251135aeb2141aa077300d1b3f/dash.css'
    )
})

# dash.scripts.config.serve_locally = True
# dash.css.config.serve_locally = True

if __name__ == "__main__":
    dash.run_server(
        port=8050,
        debug=True
    )
