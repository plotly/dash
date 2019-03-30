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
    dcc.Store(
        id='df',
        data=df.to_dict('records')
    ),

    dcc.Input(
        id='country-search',
        value='Canada'
    ),

    dcc.Dropdown(
        id='year',
        options=[
            {'value': i, 'label': i}
            for i in df.year.unique()
        ],
        multi=True,
        value=df.year.unique()
    ),

    dcc.RadioItems(
        id='mode',
        options=[
            {'label': 'Lines', 'value': 'lines'},
            {'label': 'Markers', 'value': 'markers'},
        ],
        value='lines'
    ),

    dcc.Graph(id='my-fig'),

])


app.callback(
    Output('my-fig', 'figure'),
    [Input('country-search', 'value'),
     Input('year', 'value'),
     Input('mode', 'value')],
    [State('df', 'data')],
    client_function=ClientFunction('clientside', 'updateFig'))


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
