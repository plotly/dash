from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly
import numpy as np

import utils
from components import element as el
from components import graph

app = Flask(__name__)
app.debug = True
app.config['key'] = 'secret'
socketio = SocketIO(app)


@app.route('/')
def index():
    utils.write_templates(
        'index.html',
        layout='two_column',
        blocks={
            'banner': [
                el('H1', {}, 'Hello World')
            ],

            'leftcolumn': [
                el('label', {}, 'Amplitude'),
                el('input', {
                    'type': 'range',
                    'class': 'u-full-width show-values',
                    'name': 'amplitude',
                    'value': 0,
                    'min': 0,
                    'max': 10,
                    'step': 0.1
                })
            ],

            'rightcolumn': [
                graph('sine-wave')
            ]
        }
    )
    return render_template('layouts/layout_twopane.html')


@socketio.on('replot')
def replot(app_state):
    amplitude = app_state['amplitude']
    x = np.linspace(0, 2 * 3.14, 500)
    y = amplitude * np.sin(x)
    messages = [
        {
            'id': 'sine-wave',
            'task': 'newPlot',
            'data': [{
                'x': x,
                'y': y,
            }],
        }
    ]
    emit('postMessage', json.dumps(messages, cls=plotly.utils.PlotlyJSONEncoder))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
