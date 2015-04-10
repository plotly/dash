from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly
import re

import DataBackend

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

graph = DataBackend.Graph()

nan_regex = re.compile(r'\bNaN\b')


def replace_nan(encoded):
    regex = re.compile(r'\bNaN\b')
    return regex.sub('null', encoded)


@app.route('/')
def index():
    graph.on_page_load()
    app.logger.info('index')
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    app.logger.info('on connect')
    emit('server response', {'data': 'Connected'})


@socketio.on('replot')
def replot(message):
    app.logger.info('replot: {}'.format(message))
    messages = graph.replot(message)
    jmessages = replace_nan(json.dumps(messages,
                                       cls=plotly.utils.PlotlyJSONEncoder))
    emit('postMessage', jmessages)


@socketio.on('pong')
def on_pong(message):
    app.logger.info('on_pong: {}'.format(message))
    messages = graph.on_pong(message)
    jmessages = replace_nan(json.dumps(messages,
                                       cls=plotly.utils.PlotlyJSONEncoder))
    emit('postMessage', jmessages)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9999)
    # socketio.run(app, port=9999)
