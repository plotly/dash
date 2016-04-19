from react import Dash
from components import div, Dropdown, label

dash = Dash(__name__)


def gen_dropdown(id):
    return Dropdown(
        id=id,
        options=[{'val': c, 'label': c} for c in ['a', 'b', 'c']],
        selected='a'
    )

components = []
for id in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'O']:
    components.append(label(id))
    components.append(gen_dropdown(id))

dash.layout = div(components)

import time


@dash.react('O', ['C', 'B', 'D', 'E'])
def update_odata(c, b, d, e):
    print 'O'
    time.sleep(10)
    return {'selected': 'b'}


@dash.react('A', ['C'])
def update_adata(c):
    print 'A'
    time.sleep(10)
    return {'selected': 'b'}


@dash.react('D', ['C'])
def update_ddata(c):
    print 'D'
    time.sleep(10)
    return {'selected': 'b'}


@dash.react('E', ['C'])
def update_edata(c):
    print 'E'
    time.sleep(10)
    return {'selected': 'b'}


@dash.react('G', ['C'])
def update_gdata(c):
    print 'G'
    time.sleep(10)
    return {'selected': 'b'}


@dash.react('B', ['A', 'D'])
def update_bdata(a, d):
    print 'B'
    time.sleep(10)
    return {'selected': 'b'}


@dash.react('F', ['E'])
def update_fdata(e):
    print 'F'
    time.sleep(10)
    return {'selected': 'b'}


if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)
