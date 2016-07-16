import datetime
import time
import random

from dash.react import Dash
from dash_html_components import Div
from dash_core_components import Dropdown, PlotlyGraph

dash = Dash(__name__)

graph_json = {
    'figure': {
        'layout': {
            'barmode': 'stack'
        }
    }
}

graph_data = [
    [{
        'x': [
            20,
            14,
            23
        ],
        'y': [
            'giraffes',
            'orangutans',
            'monkeys'
        ],
        'marker': {
            'color': 'rgba(55, 128, 191, 0.6)',
            'line': {
                'color': 'rgba(55, 128, 191, 1.0)',
                'width': 1
            }
        },
        'name': 'SF Zoo',
        'orientation': 'h',
        'type': 'bar'
    }],
    [{
        'x': [
            12,
            18,
            29
        ],
        'y': [
            'giraffes',
            'orangutans',
            'monkeys'
        ],
        'marker': {
            'color': 'rgba(255, 153, 51, 0.6)',
            'line': {
                'color': 'rgba(255, 153, 51, 1.0)',
                'width': 1
            }
        },
        'name': 'LA Zoo',
        'orientation': 'h',
        'type': 'bar'
    }]
]

dash.layout = Div(id='wrapper', content=[
    Dropdown(id='data_source', options=[
        {'value': '0', 'label': 'Data set 0'},
        {'value': '1', 'label': 'Data set 1'}
    ]),
    PlotlyGraph(id='graph', figure=graph_json)
])


def update_graph(dropdown):
    dropdown_value = int(dropdown['props']['value'])
    selected_data = graph_data[dropdown_value]
    return {
        'figure': {
            'data': selected_data
        }
    }


dash.react('graph', ['data_source'])(update_graph)

if __name__ == '__main__':
    dash.server.run(port=8050, debug=True)
