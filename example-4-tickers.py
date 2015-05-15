from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit

import json
import plotly
import pandas_datareader.data as web
import datetime as dt
import traceback
import pandas as pd

import dash.utils as utils
from dash.components import element as el
from dash.components import graph

name = 'dash-4-tickers'
app = Flask(name)
app.debug = True
app.config['key'] = 'secret'
socketio = SocketIO(app)

df_companies = pd.read_csv('companylist.csv')
tickers = list(df_companies['Symbol'])


@app.route('/')
def index():
    utils.write_templates(
        {
            'header': [
                el('H1', {}, 'Yahoo Finance Explorer'),
            ],
            'controls': [
                el('label', {'for': 'ticker'}, 'Ticker'),
                el('input', {
                    'name': 'ticker',
                    'type': 'text',
                    'value': 'GOOG',
                    'class': 'u-full-width'
                }, '')
            ],
            'main_pane': [graph('line-chart')]
        }, name
    )
    return render_template('layouts/layout_single_column_and_controls.html',
                           app_name=name)


@socketio.on('pong')
def pong(app_state):
    update_graph(app_state)


@socketio.on('replot')
def replot(app_state):
    update_graph(app_state)


def update_graph(app_state):
    print app_state

    ticker = app_state['ticker']
    if ticker not in tickers:
        print ticker, 'not in tickers'
        return
    else:
        try:
            df = web.DataReader(ticker, 'yahoo', dt.datetime(2014, 1, 1),
                                dt.datetime(2015, 4, 15))
        except:
            print traceback.format_exc()
            return

        messages = [
            {
                'id': 'line-chart',
                'task': 'newPlot',
                'data': [{
                    'x': df.index,
                    'y': df['Close']
                }]
            }
        ]

        emit('postMessage', json.dumps(messages,
                                       cls=plotly.utils.PlotlyJSONEncoder))


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9992)
