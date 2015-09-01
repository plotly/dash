from flask import Flask, request
import flask

from flask.ext.cors import CORS

import pandas as pd
import json

from plotly.utils import PlotlyJSONEncoder
import plotly.tools as tls

app = Flask(__name__)
CORS(app)


app.debug = True

df = pd.read_csv('http://www.stat.ubc.ca/~jenny/'
                 'notOcto/STAT545A/examples/gapminder/'
                 'data/gapminderDataFiveYear.txt', sep='\t')


def dropdown(id):
    return {
        'options': [{'val': '', 'label': ''}] + [{'val': c, 'label': c} for c in df.columns],
        'id': id,
        'selected': '',
        'element': 'dropdown'
    }



def numericdropdown(id):
    return {
        'options': [{'val': '', 'label': ''}] + [{'val': c, 'label': c} for c in df.columns if df[c].dtype in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']],
        'id': id,
        'selected': '',
        'element': 'dropdown'
    }

LAYOUT = {
    'x': dropdown('x'),
    'y': dropdown('y'),
    'rows': dropdown('rows'),
    'cols': dropdown('cols'),

    'type': {
        'options': [
            {'val': c, 'label': c} for c in ['scatter', 'line', 'bar', '2dhistogram']
        ],
        'id': 'type',
        'selected': 'scatter',
        'element': 'radio'
    },

    'color': dropdown('color'),
    'size': numericdropdown('size'),

    'slide': dropdown('slide'),

    'slider': {
        'min': 5,
        'max': 50,
        'step': 0.25,
        'value': 40,
        'id': 'slider',
        'element': 'slider'
    },

    'graph': {
        'figure': {
            'data': [],
            'layout': {}
        },
        'id': 'graph',
        'element': 'PlotlyGraph'
    }
}


@app.route('/api', methods=['POST'])
def intercept():
    body = json.loads(request.get_data())

    # This is generic, so maybe move it out
    if body['appStore'] == {}:
        body['appStore'] = LAYOUT
    else:
        x = body['appStore']['x']['selected']
        y = body['appStore']['y']['selected']
        rows = body['appStore']['rows']['selected']
        cols = body['appStore']['cols']['selected']
        color = body['appStore']['color']['selected']
        size = body['appStore']['size']['selected']
        graphtype = body['appStore']['type']['selected']
        slider = body['appStore']['slider']

        def create_trace(x_col, y_col, size_col, graphtype, dff):
            trace = {}
            if x_col != '':
                trace['x'] = dff[x_col]

            if y_col != '':
                trace['y'] = dff[y_col]
            elif x_col != '':
                trace['y'] = ['-'] * len(trace['x'])

            if graphtype == '':
                trace['type'] = 'scatter'
                trace['mode'] = 'markers'
            else:
                trace['type'] = 'scatter' if graphtype in ['scatter', 'line'] else trace['type']
                trace['mode'] = 'markers' if graphtype == 'scatter' else 'lines'

            if size_col != '' and graphtype == 'scatter':
                trace['marker'] = {}
                trace['marker']['sizemin'] = 4
                trace['marker']['sizeref'] = max(df[size_col]) / 3600.
                trace['marker']['size'] = dff[size_col]
                trace['marker']['sizemode'] = 'area'

            return trace

        def create_traces(color, size, dff):
            if color != '':
                if dff[color].dtype == 'object':
                    trace_names = dff[color].unique()
                    traces = []
                    for trace_name in trace_names:
                        idx = dff[color] == trace_name
                        traces.append(create_trace(x, y, size, graphtype, dff[idx]))
                        traces[-1]['name'] = trace_name
                else:
                    dff.sort(color, ascending=True, inplace=True)
                    trace = create_trace(x, y, size, graphtype, dff)
                    if 'marker' in trace:
                        trace['marker']['color'] = dff[color]
                    else:
                        trace['marker'] = dict(color=dff[color])
                    traces = [trace]
            else:
                traces = [create_trace(x, y, size, graphtype, dff)]
            return traces

        if slide != '':
            idx = df[slide] == slider.value

        if rows != '':
            if df[rows].dtype == 'object':
                row_names = df[rows].unique()
                fig = tls.make_subplots(rows=len(row_names), cols=1, shared_xaxes=True, subplot_titles=row_names)

                for i, row_name in enumerate(row_names):
                    idx = df[rows] == row_name
                    traces = create_traces(color, size, df[idx])
                    for trace in traces:
                        fig.append_trace(trace, i + 1, 1)
                fig['layout']['height'] = 300 * len(row_names)
                fig['layout']['showlegend'] = False

        else:
            fig = {}
            fig['data'] = create_traces(color, size, df)
            fig['layout'] = {}
            fig['layout']['xaxis'] = {'title': x}
            fig['layout']['yaxis'] = {'title': y}
            fig['layout']['height'] = 600

        fig['layout']['hovermode'] = 'closest'

        body['appStore']['graph']['figure'] = json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))

    return flask.jsonify(body)

if __name__ == '__main__':
    app.run(port=8080, debug=True)
