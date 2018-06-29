import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_html_components as html
import json

app = dash.Dash()

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

app.layout = html.Div([
    dash_table.Table(
        id='table',
        dataframe=[
            {'ind': 0, 'temp': 80, 'climate': 'Tropical'},
            {'ind': 1, 'temp': 30, 'climate': 'Snowy'},
            {'ind': 2, 'temp': 20, 'climate': 'Rain Forests'},
        ],
        columns=[
            {
                'id': 'ind',
                'name': ''
            },
            {
                'id': 'temp',
                'name': 'Temperature'
            },
            {
                'id': 'climate',
                'name': 'Climate'
            },
        ],
        editable=True
    ),
    html.Div(id='container')
])


@app.callback(
    Output('container', 'children'),
    [Input('table', 'dataframe_timestamp')],
    [State('table', 'dataframe'),
     State('table', 'dataframe_previous')])
def display_data(timestamp, dataframe, dataframe_previous):
    changes = []
    for (i, row) in enumerate(dataframe):
        row_prev = dataframe_previous[i]
        for col in row:
            if row[col] != row_prev[col]:
                changes.append(u'rows[{}][{}] = {} ➡ {}'.format(
                    i, col, row_prev[col], row[col]
                ))

    return html.Pre('\n'.join(changes), style={'fontSize': 20})


if __name__ == '__main__':
    app.run_server(debug=True)
