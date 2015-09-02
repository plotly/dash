import json

import flask
from flask.ext.cors import CORS

app = flask.Flask(__name__)
CORS(app)

from components import div, h1, h4, Dropdown, PlotlyGraph, Slider

LAYOUT = div({'className': 'row'}, [
    div({'className': 'four columns'}, [
        h1({}, 'this is my bass line'),
        h4({}, 'my waist line'),
        Dropdown({
            'id': 'droppy',
            'options': [
                {'label': 'label 1', 'val': 'val 1'},
                {'label': 'label 2', 'val': 'val 2'}
            ]
        })
    ]),
    div({'className': 'four columns'}, [
        div({}, 'the silence is deafening'),
        PlotlyGraph({
            'figure': {
                'data': [{
                    'x': [1, 2, 3], 'y': [3, 1, 2]
                }],
                'layout': {'title': 'see the light'}
            }, 'id': 'g1', 'height': 300,
            'dependencies': ['droppy', 'slidy']
        }),
        PlotlyGraph({
            'figure': {
                'data': [{
                    'x': [1, 2, 3], 'y': [3, 5, 2]
                }],
                'layout': {'title': 'its that time of the night'}
            }, 'id': 'g2', 'height': 300
        })
    ]),
    div({'className': 'four columns'}, [
        h1({}, 'the west side'),
        h4({}, 'the best side'),
        Slider({'id': 'slidy', 'min': 0, 'max': 5, 'step': 2, 'value': 1})
    ])
])


@app.route('/initialize')
def initialize():
    return flask.jsonify(LAYOUT)


@app.route('/interceptor', methods=['POST'])
def interceptor():
    body = json.loads(flask.request.get_data())
    print body
    target = body['target']
    if target['props']['id'] == 'g1':
        target['props']['figure']['layout']['title'] = body['parents']['droppy']['props']['selected']

    response = {'response': target}

    return flask.jsonify(response)


if __name__ == '__main__':
    app.run(port=8080, debug=True)
