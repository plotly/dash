import dash
from dash.dependencies import Input, Output, State, ClientFunction
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

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

    html.Div(style={'padding': 50}, children=[
        dcc.Dropdown(
            id='country-search',
            options=[{'label': i, 'value': i} for i in df['country'].unique()],
            value=df['country'].unique(),
            multi=True
        ),

        dcc.Slider(
            id='year',
            min=df['year'].min(),
            max=df['year'].max(),
            value=df['year'].min(),
            marks={str(year): str(year) for year in df['year'].unique()},
            updatemode='drag',
            step=5
        ),
    ]),

    dcc.Graph(id='my-fig'),
])


app.callback(
    Output('my-fig', 'figure'),
    [Input('country-search', 'value'),
     Input('year', 'value')],
    [State('df', 'data')],
    client_function=ClientFunction('clientside', 'animateFig'))


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
