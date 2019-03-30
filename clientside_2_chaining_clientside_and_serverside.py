import dash
from dash.dependencies import Input, Output, State, ClientFunction
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = dash.Dash(
    __name__,
    external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/ramda/0.25.0/ramda.min.js']
)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True



app.layout = html.Div([

    html.Label('x'),
    dcc.Input(id='x', value=3),

    html.Label('y'),
    dcc.Input(id='y', value=6),

    # clientside
    html.Label('x + y (clientside)'),
    dcc.Input(id='x+y'),

    # server-side
    html.Label('x+y / 2 (serverside - takes 5 seconds)'),
    dcc.Input(id='x+y / 2'),

    # server-side
    html.Div([
        html.Label('Display x, y, x+y/2 (serverside) - takes 5 seconds'),
        html.Pre(id='display-all-of-the-values'),
    ]),

    # clientside
    html.Label('Mean(x, y, x+y, x+y/2) (clientside)'),
    html.Div(id='mean-of-all-values'),


])



app.callback(
    Output('x+y', 'value'),
    [Input('x', 'value'),
     Input('y', 'value')],
    client_function=ClientFunction('R', 'add'))


@app.callback(Output('x+y / 2', 'value'),
              [Input('x+y', 'value')])
def divide_by_two(value):
    import time; time.sleep(4)
    return float(value) / 2.0


@app.callback(Output('display-all-of-the-values', 'children'),
              [Input('x', 'value'),
               Input('y', 'value'),
               Input('x+y', 'value'),
               Input('x+y / 2', 'value')])
def display_all(*args):
    import time; time.sleep(4)
    return '\n'.join([str(a) for a in args])


app.callback(
    Output('mean-of-all-values', 'children'),
    [Input('x', 'value'), Input('y', 'value'),
     Input('x+y', 'value'), Input('x+y / 2', 'value')],
    client_function=ClientFunction('clientside', 'mean'))


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
