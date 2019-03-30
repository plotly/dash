import dash
from dash.dependencies import Input, Output, State, ClientFunction
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json

import pandas as pd

app = dash.Dash(
    __name__,
    external_scripts=['https://cdnjs.cloudflare.com/ajax/libs/ramda/0.25.0/ramda.min.js']
)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True


app.layout = html.Div([
    html.Label('New Column'),
    dcc.Input(id='new-column-name', placeholder='name'),
    html.Button('Add Column', id='add-column', n_clicks=0),
    html.Button('Add Row', id='add-row', n_clicks=1),
    dash_table.DataTable(
        id='table',
        editable=True,
    ),

    html.Div(html.B('Clientside')),
    dcc.Graph(id='graph'),

    html.B('Server Side'),
    html.Pre(id='display')
])


app.callback(
    Output('table', 'columns'),
    [Input('add-column', 'n_clicks')],
    [State('new-column-name', 'value'),
     State('table', 'columns')],
    client_function=ClientFunction('clientside', 'tableColumns'))


app.callback(
    Output('table', 'data'),
    [Input('table', 'columns'),
     Input('add-row', 'n_clicks')],
    [State('table', 'data')],
    client_function=ClientFunction('clientside', 'tableData'))


app.callback(
    Output('graph', 'figure'),
    [Input('table', 'data')],
    client_function=ClientFunction('clientside', 'graphTable'))


@app.callback(Output('display', 'children'),
              [Input('table', 'columns'),
               Input('table', 'data')])
def display_data(columns, data):
    return html.Div([
        html.Div(html.B('Columns')),
        html.Pre(json.dumps(columns, indent=2)),
        html.Div(html.B('Data')),
        html.Pre(json.dumps(data, indent=2)),
    ])


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
