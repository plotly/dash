from flask import Flask, request
import flask

from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)


app.debug = True


@app.route('/api', methods=['POST'])
def hello_world():
    body = request.json

    if body['targetId'] == 'firstDropdown':
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
