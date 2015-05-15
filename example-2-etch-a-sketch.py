from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly

import dash.utils as utils
from dash.components import element as el
from dash.components import graph

from collections import deque

name = 'dash-2-etch-a-sketch'
app = Flask(name)
app.debug = True
app.config['key'] = 'secret'
socketio = SocketIO(app)


graph_id = 'main-graph'
slider_x_id = 'X'
slider_y_id = 'Y'
title_input_id = 'title'

last_x = deque([], 100)
last_y = deque([], 100)


@app.route('/')
def index():
    utils.write_templates(
        {
            'header': [
                el('H1', {}, 'Etch-a-sketch')
            ],

            'controls': [
                el('label', {}, 'X Position'),
                el('input', {
                    'type': 'range',
                    'class': 'u-full-width show-values',
                    'name': slider_x_id,
                    'value': 0,
                    'min': 10,
                    'max': 2000,
                    'step': 10
                }),

                el('label', {}, 'Y Position'),
                el('input', {
                    'type': 'range',
                    'class': 'u-full-width show-values',
                    'name': slider_y_id,
                    'value': 0,
                    'min': 10,
                    'max': 2000,
                    'step': 10
                }),

                el('label', {}, 'Title'),
                el('input', {
                    'class': 'u-full-width',
                    'type': 'text',
                    'placeholder': 'Type away',
                    'name': title_input_id})
            ],

            'main_pane': [
                graph(graph_id)
            ]
        }, name
    )

    return render_template('layouts/layout_single_column_and_controls.html',
                           app_name=name)


@socketio.on('replot')
def replot(app_state):
    print(app_state)
    last_x.append(app_state[slider_x_id])
    last_y.append(app_state[slider_y_id])
    messages = [
        {
            'id': graph_id,
            'task': 'newPlot',
            'layout': {
                'title': app_state[title_input_id]
            },
            'data': [{
                'x': list(last_x),
                'y': list(last_y)
            }]
        }
    ]

    emit('postMessage', json.dumps(messages,
                                   cls=plotly.utils.PlotlyJSONEncoder))


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9991)
