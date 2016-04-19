# This code generated this page.

import os

from react import Dash
from components import (Dropdown, RadioButton, TextInput, Slider, PlotlyGraph,
                        CheckList, div, pre, hr, h4)

dash = Dash(__name__)


option_list = [('apples', 'Apples'), ('oranges', 'Oranges')]

component_list = [
    Dropdown(id='dropdown',
             options=[{'val': v, 'label': l} for (v, l) in option_list]),
    RadioButton(
        id='radio',
        name='fruit',
        options=[{'val': v, 'label': l} for (v, l) in option_list]),

    TextInput(
        id='textinput',
        label='Name',
        placeholder='James Murphy'
    ),

    Slider(id='slider', min=-5, max=5, value=3, step=0.2, label='time'),

    CheckList(id='checklist', options=[{'id': id, 'label': l,
                                        'checked': False}
                                       for (id, l) in option_list]),

    PlotlyGraph(
        id='graph',
        figure={
            'data': [{'x': [1, 2, 3], 'y': [3, 1, 5]}],
            'layout': {'title': 'PlotlyGraph'}
        }
    )
]

container_style = {'width': '90%', 'marginLeft': 'auto', 'marginRight': 'auto'}
column_style = {'overflowX': 'scroll'}

dash.layout = div(style=container_style, content=[
    div(className="row", content=[
        div(className="six columns", style=column_style, content=[
            h4('Dash Components'),
            hr(),
            # display all of the components with a <pre> container
            div([
                div(className="row", content=[
                    component,
                    pre(id=component.id + '-repr'),
                    hr()
                ]) for component in component_list]),

        ]),
        # Display this app code on the right column
        div(className="six columns",
            style=dict(borderLeft='1px solid #E1E1E1', paddingLeft='4%',
                       **column_style),
            content=[
                h4('App Code'),
                hr(),
                pre(open(os.path.basename(__file__)).read())
            ])
    ])
])


def display_component_repr(component):
    return {
        'content': str(component)
    }

for component in component_list:
    # Update each component's "pre" with its representation when it changes
    # Normally a decorator like @dash.react('graph-repr', ['graph'])
    dash.react(component.id + '-repr', [component.id])(display_component_repr)


if __name__ == '__main__':
    dash.server.run(port=8080, debug=True)
