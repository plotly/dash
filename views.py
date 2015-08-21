from flask import Flask
import flask

from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api')
def hello_world():
    second_dropdown = {
        'seafood': [
            {'val': 'smoked-salmon', 'name': 'Fresh Smoked Salmon'},
            {'val': 'smoked-trout', 'name': 'Wild Alaska Trout'},
            {'val': 'flying-fish', 'name': 'A Barbados Special'}
        ],
        'meat': [
            {'val': 'hamburger', 'name': 'Palace Burger'},
            {'val': 'sausage', 'name': 'Chez Vito Turkey Sausage'}
        ],
        'vegetables': [
            {'val': 'rutabegga', 'name': 'Rudabagga'},
            {'val': 'carrots', 'name': 'Rainbow Carrots'},
            {'val': 'fennel', 'name': 'Sliced Fennal'}
        ]
    }

    return flask.jsonify(**second_dropdown)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
