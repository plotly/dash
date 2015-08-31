from flask import Flask, request
import flask

from flask.ext.cors import CORS

import pandas as pd
import json

from plotly.utils import PlotlyJSONEncoder
import plotly.tools as tls
import copy


app = Flask(__name__)
CORS(app)


app.debug = True


def generic_dropdown(id, children, dependson):
    return {
        'id': id,
        'component': 'dropdown',
        'options': [
            {'label': 'selection 1', 'value': 'sel1'},
            {'label': 'selection 2', 'value': 'sel2'},
        ],
        'selected': 'selection 1',
        'children': children,
        'dependson': dependson

    }

def generic_slider(id, children, dependson):
    return {
        'id': id,
        'children': children,
        'dependson': dependson,
        'min': 0,
        'max': 10,
        'value': 2,
        'label': True
    }

def generic_graph(id, children, dependson):
    pass


LAYOUT = {
    'w1': generic_dropdown('w1', ['w2'], []),
    'x1': generic_dropdown('x1', ['w2', 'x2'], []),
    'y1': generic_dropdown('y1', ['x2'], []),
    'z1': generic_dropdown('z1', ['y2'], []),

    'w2': generic_dropdown('w2', ['w3'], ['w1', 'x1']),
    'x2': generic_dropdown('x2', [], ['x1', 'y1']),
    'y2': generic_dropdown('y2', [], ['z1']),

    'w3': generic_dropdown('w3', [], ['w2']),

    's1': generic_slider('s1', [], [])
}


@app.route('/initialize')
def initialize():
    return flask.jsonify(LAYOUT)


@app.route('/interceptor', methods=['POST'])
def interceptor():
    body = json.loads(request.get_data())
    print body
    target = body['id']
    state = body['parents']
    response = []

    layout = copy.deepcopy(LAYOUT)

    for componentid, component in layout.iteritems():
        print componentid
        print target
        if componentid == target:
            for option in component['options']:
                option['label'] = 'f(' + ', '.join(c + '=' + state[c]['selected'] for c in component['dependson']) + ')'
            response.append(component)

    response = {'response': response[0]}

    return flask.jsonify(response)

if __name__ == '__main__':
    app.run(port=8080, debug=True)




