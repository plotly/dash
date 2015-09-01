from flask import Flask, request
import flask

from flask.ext.cors import CORS

import pandas as pd
import json

from plotly.utils import PlotlyJSONEncoder
import plotly.tools as tls
import copy


app = Flask(__name__)
CORS(app)


app.debug = True


def generic_dropdown(id, dependson):
    return {
        'id': id,
        'component': 'dropdown',
        'options': [
            {'label': 'selection 1', 'value': 'sel1'},
            {'label': 'selection 2', 'value': 'sel2'},
        ],
        'selected': 'selection 1',
        'dependson': dependson
    }


def generic_slider(id, dependson):
    return {
        'id': id,
        'component': 'slider',
        'dependson': dependson,
        'min': 0,
        'max': 10,
        'value': 2,
        'label': True
    }


def generic_graph(id, dependson):
    return {
        'id': id,
        'component': 'graph',
        'dependson': dependson,
        'figure': {
            'data': [{
                'x': [1, 2, 3],
                'y': [3, 1, 5]
            }],
            'layout': {
                'title': 'initial state'
            }
        },
        'height': '400px'
    }

supported_html_elements = ['a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 'big', 'blockquote', 'body', 'br','button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd', 'del', 'details', 'dfn','dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5','h6', 'head', 'header', 'hr', 'html', 'i', 'iframe', 'img', 'input', 'ins', 'kbd', 'keygen', 'label', 'legend', 'li', 'link','main', 'map', 'mark', 'menu', 'menuitem', 'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup', 'option','output', 'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 'script', 'section', 'select','small', 'source', 'span', 'strong', 'style', 'sub', 'summary', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th','thead', 'time', 'title', 'tr', 'track', 'u', 'ul', 'var', 'video', 'wbr']

LAYOUT = {
    'w1': generic_dropdown('w1', []),
    'x1': generic_dropdown('x1', []),
    'y1': generic_dropdown('y1', []),
    'z1': generic_dropdown('z1', []),

    'w2': generic_dropdown('w2', ['w1', 'x1']),
    'x2': generic_dropdown('x2', ['x1', 'y1']),
    'y2': generic_dropdown('y2', ['z1']),

    'w3': generic_dropdown('w3', ['w2']),

    's1': generic_slider('s1', []),

    'g1': generic_graph('g1', ['w1', 'w3', 's1']),

    'br1': {'component': 'br'}
}
LAYOUT['t1'] = {
    'id': 't1',
    'codeblock': {'test': 'this'},
    'dependson': [k for k in LAYOUT.keys() if LAYOUT[k].get('component', '') not in supported_html_elements]
}

for _, v in LAYOUT.iteritems():
    if v.get('component', '') not in supported_html_elements:
        v['children'] = []

for k, v in LAYOUT.iteritems():
    for parent in v.get('dependson', []):
        LAYOUT[parent]['children'].append(k)


@app.route('/initialize')
def initialize():
    return flask.jsonify(LAYOUT)


@app.route('/interceptor', methods=['POST'])
def interceptor():
    body = json.loads(request.get_data())
    print body
    target = body['id']
    print 'target: ' + target
    state = body['parents']
    response = []

    layout = copy.deepcopy(LAYOUT)

    for componentid, component in layout.iteritems():

        if componentid == target:
            if componentid == 'g1':
                component['figure']['layout']['title'] = 'f(' + ', '.join(c + '=' + str(state[c].get('selected', state[c].get('value', '?'))) for c in component['dependson']) + ')'
                response.append(component)
            elif componentid in ['w1', 'x1', 'y1', 'z1', 'w2', 'x2', 'y2', 'w3']:
                for option in component['options']:
                    option['label'] = 'f(' + ', '.join(c + '=' + str(state[c].get('selected', state[c].get('value', '?')))  for c in component['dependson']) + ')'
                response.append(component)
            elif componentid == 't1':
                codeblock = {}
                for k, v in state.iteritems():
                    codeblock[k] = {}
                    for key in ['value', 'selected', 'options']:
                        if key in v:
                            if key == 'options':
                                st = json.dumps(v[key])
                            else:
                                st = v[key]
                            codeblock[k][key] = st
                component['codeblock'] = json.dumps(codeblock, indent=4, sort_keys=True)
                response.append(component)

    response = {'response': response[0]}

    return flask.jsonify(response)


def run():
    app.run(port=8080, debug=True)

if __name__ == '__main__':
    run()




