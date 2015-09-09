from react import Dash
from components import div, Dropdown
import copy
import json

dash = Dash(__name__)

food_groups = ['fruits', 'vegetables']
food_varities = {
    'fruits': {
        'options': [{'val': c, 'label': c} for c in ['apples', 'oranges']]
    },
    'vegetables': {
        'options': [{'val': c, 'label': c} for c in ['kale', 'radishes']]
    }
}
colors = {
    'apples': {
        'options': [{'val': c, 'label': c} for c in
                    ['apple green', 'apple red']]
    },
    'oranges': {
        'options': [{'val': c, 'label': c} for c in
                    ['orange ruby', 'orange pink']]
    },
    'kale': {
        'options': [{'val': c, 'label': c} for c in
                    ['kale green', 'kale evergreen']]
    },
    'radishes': {
        'options': [{'val': c, 'label': c} for c in
                    ['radish red', 'radish pink']]
    }
}

components = [Dropdown({
    'id': 'xdata',
    'options': [{'val': c, 'label': c} for c in food_groups],
    'selected': food_groups[0]
})]

components.append(Dropdown({
    'id': 'ydata',
    'options': food_varities[components[0]['props']['selected']]['options'],
    'selected': food_varities[components[0]['props']['selected']]['options'][0]['val']
}))

components.append(Dropdown({
    'id': 'zdata',
    'options': colors[components[1]['props']['selected']]['options'],
    'selected': colors[components[1]['props']['selected']]['options'][0]['val']
}))

dash.layout = div({}, components)


@dash.react('ydata', ['xdata'])
def update_ydata(xdata):
    print 'update_ydata\n-------------'
    selected = xdata['selected']
    d = {
        'id': 'ydata',
        'options': food_varities[selected]['options'],
        'selected': food_varities[selected]['options'][0]['val']
    }
    print d
    return d


@dash.react('zdata', ['xdata', 'ydata'])
def update_zdata(xdata, ydata):
    print 'update_zdata\n-------------'
    yselected = ydata['selected']
    d = {
        'id': 'zdata',
        'options': colors[yselected]['options'],
        'selected': colors[yselected]['options'][0]['val']
    }
    print d
    return d

if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)
