import pandas.io.data as web

from react import Dash
from components import div, h2, PlotlyGraph, Dropdown

from datetime import datetime
df = web.DataReader("aapl", 'yahoo', datetime(2007, 10, 1), datetime(2009, 4, 1))

dash = Dash(__name__)

dash.layout = div({}, [
    h2({}, 'hello dash'),
    Dropdown({
        'id': 'xdata',
        'options': [{'val': c, 'label': c} for c in df.columns],
        'selected': df.columns[0]
    }),
    Dropdown({
        'id': 'ydata',
        'options': [{'val': c, 'label': c} for c in df.columns],
        'selected': df.columns[0]
    }),
    PlotlyGraph({
        'id': 'figure',
        'figure': {
            'data': [], 'layout': {}
        }
    })
])


@dash.react('figure', ['xdata', 'ydata'])
def update_graph(xdata_dropdown, ydata_dropdown):
    return {'figure': {
        'data': [{
            'x': df[xdata_dropdown['selected']],
            'y': df[ydata_dropdown['selected']],
            'mode': 'markers'
        }],
        'layout': {
            'xaxis': {'title': xdata_dropdown['selected']},
            'yaxis': {'title': ydata_dropdown['selected']}
        }
    }}

if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)

