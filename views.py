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
        'name': 'flowers-that-start-with-d'
    },

    'firstSlider': {
        'min': 5,
        'max': 50,
        'step': 0.25,
        'value': 40,
        'id': 'firstSlider'
    },

    'dateSlider': {
        'min': '2015-01-01 00:00:00',
        'max': '2015-05-03 00:00:00',
        'step': 1000 * 60 * 60 * 3,  # 3 hours
        'value': '2015-04-01T08:00:00Z',
        'id': 'dateSlider'
    }
}


@app.route('/api', methods=['POST'])
def intercept():
    body = request.json

    # This is generic, so maybe move it out
    if body['appStore'] == {}:
        body['appStore'] = LAYOUT

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

    return flask.jsonify(body)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
