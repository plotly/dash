from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly

import dash.utils as utils
from dash.components import graph

name = 'dash-3-click-events'
app = Flask(name)
app.debug = True
app.config['key'] = 'secret'
socketio = SocketIO(app)

from example_3_click_events_state import Dash
dash = Dash()


@app.route('/')
def index():
    utils.write_templates(
        {
            # 'controls.html' is already written as a raw html file in
            # templates/runtime/dash-3-click-events
            'leftgraph': [graph('bubbles')],
            'rightgraph': [graph('line-chart')]
        }, name
    )
    return render_template('layouts/layout_two_column_and_controls.html',
                           app_name=name)


@socketio.on('pong')
def onpong(app_state):
    messages = dash.on_pong(app_state)
    emit('postMessage', json.dumps(messages,
                                   cls=plotly.utils.PlotlyJSONEncoder))


@socketio.on('replot')
def replot(app_state):
    print app_state
    messages = dash.replot(app_state)
    emit('postMessage', json.dumps(messages,
                                   cls=plotly.utils.PlotlyJSONEncoder))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9999)
