import os
import copy
import time

import dash
from dash import Dash, dcc, html, Input, Output, callback, get_server

import numpy as np
import pandas as pd
from flask_caching import Cache

dash.register_page(__name__)


CACHE_CONFIG = {
    # try 'FileSystemCache' if you don't want to setup redis
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
}
cache = Cache()
cache.init_app(get_server(), config=CACHE_CONFIG)

N = 100

df = pd.DataFrame({
    'category': (
        (['apples'] * 5 * N) +
        (['oranges'] * 10 * N) +
        (['figs'] * 20 * N) +
        (['pineapples'] * 15 * N)
    )
})
df['x'] = np.random.randn(len(df['category']))
df['y'] = np.random.randn(len(df['category']))

layout = html.Div([
    dcc.Dropdown(df['category'].unique(), 'apples', id='dropdown'),
    html.Div([
        html.Div(dcc.Graph(id='graph-1'), className="six columns"),
        html.Div(dcc.Graph(id='graph-2'), className="six columns"),
    ], className="row"),
    html.Div([
        html.Div(dcc.Graph(id='graph-3'), className="six columns"),
        html.Div(dcc.Graph(id='graph-4'), className="six columns"),
    ], className="row"),

    # signal value to trigger callbacks
    dcc.Store(id='signal')
])


# perform expensive computations in this "global store"
# these computations are cached in a globally available
# redis memory store which is available across processes
# and for all time.
@cache.memoize()
def global_store(value):
    # simulate expensive query
    print(f'Computing value with {value}')
    time.sleep(3)
    return df[df['category'] == value]


def generate_figure(value, figure):
    fig = copy.deepcopy(figure)
    filtered_dataframe = global_store(value)
    fig['data'][0]['x'] = filtered_dataframe['x']
    fig['data'][0]['y'] = filtered_dataframe['y']
    fig['layout'] = {'margin': {'l': 20, 'r': 10, 'b': 20, 't': 10} }
    return fig


@callback(Output('signal', 'data'), Input('dropdown', 'value'))
def compute_value(value):
    # compute value and send a signal when done
    global_store(value)
    return value


@callback(Output('graph-1', 'figure'), Input('signal', 'data'))
def update_graph_1(value):
    # generate_figure gets data from `global_store`.
    # the data in `global_store` has already been computed
    # by the `compute_value` callback and the result is stored
    # in the global redis cached
    return generate_figure(value, {
        'data': [{
            'type': 'scatter',
            'mode': 'markers',
            'marker': {
                'opacity': 0.5,
                'size': 14,
                'line': {'border': 'thin darkgrey solid'}
            }
        }]
    })


@callback(Output('graph-2', 'figure'), Input('signal', 'data'))
def update_graph_2(value):
    return generate_figure(value, {
        'data': [{
            'type': 'scatter',
            'mode': 'lines',
            'line': {'shape': 'spline', 'width': 0.5},
        }]
    })


@callback(Output('graph-3', 'figure'), Input('signal', 'data'))
def update_graph_3(value):
    return generate_figure(value, {
        'data': [{
            'type': 'histogram2d',
        }]
    })


@callback(Output('graph-4', 'figure'), Input('signal', 'data'))
def update_graph_4(value):
    return generate_figure(value, {
        'data': [{
            'type': 'histogram2dcontour',
        }]
    })

