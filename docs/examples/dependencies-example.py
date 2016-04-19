from react import Dash
from components import div, Dropdown

dash = Dash(__name__)

food_groups = ['fruits', 'vegetables']
food_varities = {
    'fruits': [{'val': c, 'label': c} for c in ['apples', 'oranges']],
    'vegetables': [{'val': c, 'label': c} for c in ['kale', 'radishes']]
}
colors = {
    'apples': [{'val': c, 'label': c} for c in
               ['apple green', 'apple red']],
    'oranges': [{'val': c, 'label': c} for c in
                ['orange ruby', 'orange pink']],
    'kale': [{'val': c, 'label': c} for c in
             ['kale green', 'kale evergreen']],
    'radishes': [{'val': c, 'label': c} for c in
                 ['radish red', 'radish pink']]
}

dash.layout = div([
    Dropdown(id='xdata', options=[{'val': c, 'label': c} for c in food_groups])
])
dash.layout['xdata'].selected = dash.layout['xdata'].options[0]['val']
dash.layout.append(
    Dropdown(id='ydata', options=food_varities[dash.layout['xdata'].selected])
)
dash.layout['ydata'].selected = dash.layout['ydata'].options[0]['val']

dash.layout.append(
    Dropdown(id='zdata', options=colors[dash.layout['ydata'].selected])
)
dash.layout['zdata'].selected = dash.layout['zdata'].options[0]['val']


@dash.react('ydata', ['xdata'])
def update_ydata(xdata):
    new_dropdown = {
        'options': food_varities[xdata.selected]
    }
    new_dropdown['selected'] = new_dropdown['options'][0]['val']
    return new_dropdown


@dash.react('zdata', ['ydata'])
def update_zdata(ydata):
    new_dropdown = {
        'options': colors[ydata.selected]
    }
    new_dropdown['selected'] = new_dropdown['options'][0]['val']
    return new_dropdown

if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)
