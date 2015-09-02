import json

import flask
from flask.ext.cors import CORS

app = flask.Flask(__name__)
CORS(app)

from components import div, label, h2, h4, Dropdown, PlotlyGraph

import pandas as pd
import pandas.io.data as web
from datetime import datetime
from plotly.utils import PlotlyJSONEncoder
from plotly.graph_objs import Figure, Data, Scatter

datasets = {
    'hans': pd.read_csv('http://www.stat.ubc.ca/~jenny/'
                        'notOcto/STAT545A/examples/gapminder/'
                        'data/gapminderDataFiveYear.txt', sep='\t'),
    'stock': web.DataReader("aapl", 'yahoo',
                            datetime(2007, 10, 1), datetime(2009, 4, 1))
}

LAYOUT = div({'className': 'row'}, [
    div({'className': 'four columns'}, [
        h2({}, 'hello dash'),
        h4({}, 'reactpy. reactly. plux..ly. fluxpy?'),

        label({}, 'Select dataset'),
        Dropdown({
            'id': 'dataset',
            'options': [
                {'label': 'Stocks', 'val': 'stock'},
                {'label': 'Country Indicators (Hans Rosling)', 'val': 'hans'}
            ],
            'selected': 'stock'
        }),
        label({}, 'Select variable'),
        Dropdown({
            'id': 'yaxis-dropdown',
            'options': [{'label': c, 'val': c} for c in datasets['stock'].columns],
            'dependencies': ['dataset']
        }),
    ]),
    div({'className': 'eight columns'}, [
        PlotlyGraph({
            'figure': Figure(data=Data([
                Scatter(
                    x=datasets['stock'].index,
                    y=datasets['stock'][datasets['stock'].columns[0]],
                    name=datasets['stock'].columns[0])
            ])),
            'id': 'graph',
            'dependencies': ['yaxis-dropdown', 'dataset']
        })
    ])
])


@app.route('/initialize')
def initialize():
    return flask.jsonify(json.loads(json.dumps(LAYOUT, cls=PlotlyJSONEncoder)))


@app.route('/interceptor', methods=['POST'])
def interceptor():
    body = json.loads(flask.request.get_data())
    print body
    target = body['target']

    if target['props']['id'] == 'yaxis-dropdown':
        selected_dataset = body['parents']['dataset']['props']['selected']
        target['props']['options'] = [{'label': c, 'val': c} for c in datasets[selected_dataset].columns]

    if target['props']['id'] == 'graph':
        dataset = datasets[body['parents']['dataset']['props']['selected']]
        yaxis_column = body['parents']['yaxis-dropdown']['props']['selected']
        if yaxis_column in dataset.columns:
            target['props']['figure']['data'][0] = {
                'x': dataset.index,
                'y': dataset[yaxis_column]
            }
        else:
            target['props']['figure']['data'][0] = {
                'x': dataset.index,
                'y': dataset[dataset.columns[0]]
            }

    response = {'response': target}

    return flask.jsonify(json.loads(json.dumps(response, cls=PlotlyJSONEncoder)))


if __name__ == '__main__':
    app.run(port=8080, debug=True)
