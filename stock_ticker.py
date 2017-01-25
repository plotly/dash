from pandas_datareader import data as web
from datetime import datetime as dt

from dash.react import Dash
from dash_html_components import Div, H2, P, Span, Strong
from dash_core_components import Dropdown, PlotlyGraph, Label

# Create a AAPL stock data reader
df = web.DataReader(
    'aapl', 'yahoo',
    dt(2007, 10, 1), dt(2009, 4, 1))

dash = Dash(__name__)

dash.layout = Div(id='wrapper', content=[
    H2('Apple historical stock value'),

    P(
        Strong('Select Y data:')
    ),

    Dropdown(
        id='ydata',
        options=[
            {'value': c, 'label': c}
            for c in df.columns
        ]
    ),

    PlotlyGraph(id='graph')
])


def update_graph(ydata_dropdown):

    selected = ydata_dropdown['props']['value']

    return {
        'data': [{
            'x': df.index,
            'y': df[selected],
            'mode': 'markers'
        }],
        'layout': {
            'yaxis': {'title': selected},
            'margin': {'t': 0}
        }
    }

dash.react('graph', ['ydata'])(update_graph)

if __name__ == "__main__":
    dash.run_server(
        port=8050,
        debug=True,
        component_suites=[
            'dash_core_components',
            'dash_html_components'
        ]
    )
