from flask import Flask, request
import flask

from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)


app.debug = True


LAYOUT = {
    'firstDropdown': {
        'options': [
            {'val': 'seafood', 'label': 'Fish'},
            {'val': 'meat', 'label': 'Meats'},
            {'val': 'vegetables', 'label': 'Les Legumes'}
        ],
        'selected': 'seafood',
        'id': 'firstDropdown',
        'element': 'dropdown'
    },

    'secondDropdown': {
        'options': [
            {'val': 'iris', 'label': 'iriss'},
            {'val': 'cosmos', 'label': 'c0sMOs'},
            {'val': 'sunflr', 'label': 'sunflowerz'}
        ],
        'selected': 'cosmos',
        'id': 'secondDropdown',
        'element': 'dropdown'
    },

    'firstRadio': {
        'options': [
            {'val': 'seafood', 'label': 'Fish'},
            {'val': 'meat', 'label': 'Meats'},
            {'val': 'vegetables', 'label': 'Les Legumes'}
        ],
        'id': 'firstRadio',
        'name': 'foodGroup',
        'selected': 'seafood',
        'element': 'radio'
    },

    'secondRadio': {
        'options': [
            {'val': 'iris', 'label': 'iriss'},
            {'val': 'cosmos', 'label': 'c0sMOs'},
            {'val': 'sunflr', 'label': 'sunflowerz'}
        ],
        'id': 'secondRadio',
        'name': 'flowers',
        'selected': 'cosmos',
        'element': 'radio'
    },

    'firstCheckbox': {
        'options': [
            {'id': 'daisy', 'label': 'Dasiy', 'isChecked': True},
            {'id': 'dandalion', 'label': 'Dandalion', 'isChecked': False}
        ],
        'name': 'flowers-that-start-with-d',
        'element': 'checkbox'
    },

    'firstSlider': {
        'min': 5,
        'max': 50,
        'step': 0.25,
        'value': 40,
        'id': 'firstSlider',
        'element': 'slider'
    },

    'secondSlider': {
        'min': 5,
        'max': 50,
        'step': 0.25,
        'value': 40,
        'id': 'secondSlider',
        'element': 'slider'
    },

    'graph1': {
        'figure': {
            'data': [{
                'x': [1, 2, 3, 4],
                'y': [1, 4, 9, 16]
            }],
            'layout': {
                'title': 'test'
            }
        },
        'id': 'graph1',
        'element': 'PlotlyGraph'
    }
}


@app.route('/api', methods=['POST'])
def intercept():
    body = request.json

    # This is generic, so maybe move it out
    if body['appStore'] == {}:
        body['appStore'] = LAYOUT

    if 'targetId' in body:
        print body['appStore'][body['targetId']]

    if body.get('targetId', '') == 'firstDropdown':
        selected = body['appStore']['firstDropdown']['selected']
        secondDropdown = body['appStore']['secondDropdown']
        if selected == 'seafood':
            secondDropdown['options'] = [
                {'val': 'a', 'label': 'A'},
                {'val': 'b', 'label': 'B'},
            ]
            secondDropdown['selected'] = 'a'

        elif selected == 'meat':
            secondDropdown['options'] = [
                {'val': 'c', 'label': 'C'},
                {'val': 'd', 'label': 'D'},
            ]
            secondDropdown['selected'] = 'c'

        elif selected == 'vegetables':
            secondDropdown['options'] = [
                {'val': 'e', 'label': 'E'},
                {'val': 'f', 'label': 'F'},
            ]
            secondDropdown['selected'] = 'e'

    if (body.get('targetId', '') == 'firstSlider' or
            body.get('targetId', '') == 'secondSlider'):

        x = float(body['appStore']['firstSlider']['value'])
        y = float(body['appStore']['secondSlider']['value'])
        trace = body['appStore']['graph1']['figure']['data'][0]
        trace['x'] = trace['x'][1:]
        trace['x'].append(x)
        trace['y'] = trace['y'][1:]
        trace['y'].append(y)
        print trace

    return flask.jsonify(body)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
