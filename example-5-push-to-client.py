from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly
from threading import Thread

import dash.utils as utils
from dash.components import element as el
from dash.components import graph

name = __name__
app = Flask(name)
app.debug = True
app.config['key'] = 'secret'
socketio = SocketIO(app)

# Write the HTML "includes" blocks to /templates/runtime/dash-5-push-to-client
# Alternatively, include the HTML yourself in that folder
utils.write_templates(
    {
        'content': [
            el('h1', {}, 'Refresh the data behind the graph'),
            graph('graph')
        ]
    }, name
)


@app.route('/')
def index():
    return render_template('layouts/layout_full_screen.html',
                           app_name=name)


@socketio.on('replot')
def replot(app_state):
    """ Callback for state changes in the front-end
    """
    pass


def refresh_data_in_background():
    """ This function is executed as a background thread when the
    app starts and can be used to push updates the graph in the client.
    Note that all of the viewers of the graph will see the same
    updates at the same time.
    This is useful for periodically updating charts with new data.
    """
    import time
    from collections import deque
    x = deque([], 10)
    y = deque([], 10)
    i = 0
    while True:
        i += 1
        time.sleep(1)
        print('refresh')
        x.append(i)
        y.append(i)
        messages = [
            {
                'id': 'graph',
                'task': 'newPlot',
                'data': [{
                    'x': list(x),
                    'y': list(y),
                }]
            }
        ]
        socketio.emit('postMessage',
                      json.dumps(messages,
                                 cls=plotly.utils.PlotlyJSONEncoder))


if __name__ == '__main__':
    t = Thread(target=refresh_data_in_background)
    t.daemon = True
    t.start()
    socketio.run(app, host='0.0.0.0', port=9991)
