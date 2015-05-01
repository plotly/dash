from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly

import utils
from components import element as el
from components import graph

app = Flask(__name__)
app.debug = True
socketio = SocketIO(app)


@app.route('/')
def index():
    utils.write_templates(
        'index.html',
        layout='two_column',
        blocks={
            'banner': [
                el('H1', {}, 'Simple example')
            ],
            'leftcolumn': [
                el('H4', {}, 'Simple Dash Example')
            ],
            'rightcolumn': [
                graph('time-series')
            ]
        }
    )
    return render_template('layouts/layout_twopane.html')


@socketio.on('replot')
def replot(app_state):
    messages = []
    emit('postMessage', json.dumps(messages, cls=plotly.utils.PlotlyJSONEncoder))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
