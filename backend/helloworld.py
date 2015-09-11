import pandas.io.data as web

from react import Dash
from components import div, h2, PlotlyGraph, Dropdown, label

from datetime import datetime as dt
df = web.DataReader("aapl", 'yahoo', dt(2007, 10, 1), dt(2009, 4, 1))

dash = Dash(__name__)

dash.layout = div([
    h2('hello dash'),
    div(className='row', content=[
        div(className='two columns', content=[
            div([
                label('select x data'),
                Dropdown(id='xdata', options=[{'val': c, 'label': c}
                                              for c in df.columns])
            ]),
            div([
                label('select y data'),
                Dropdown(id='ydata', options=[{'val': c, 'label': c}
                                              for c in df.columns])
            ]),
        ]),
        div(className='ten columns', content=[
            PlotlyGraph(id='graph')
        ])
    ])
])
dash.layout['xdata'].selected = dash.layout['xdata'].options[0]['val']
dash.layout['ydata'].selected = dash.layout['ydata'].options[0]['val']
dash.layout['graph'].figure = {
    'data': [{
        'x': df[dash.layout['xdata'].selected],
        'y': df[dash.layout['ydata'].selected]
    }],
    'layout': {
        'xaxis': {'title': dash.layout['xdata'].selected},
        'yaxis': {'title': dash.layout['ydata'].selected},
        'margin': {'t': 0}
    }}


@dash.react('graph', ['xdata', 'ydata'])
def update_graph(xdata_dropdown, ydata_dropdown):
    return {
        'figure': {
            'data': [{
                'x': df[xdata_dropdown.selected],
                'y': df[ydata_dropdown.selected]
            }],
            'layout': {
                'xaxis': {'title': xdata_dropdown.selected},
                'yaxis': {'title': ydata_dropdown.selected}
            }
        }
    }
if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)
