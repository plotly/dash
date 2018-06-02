import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
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
    [Input('table', 'dataframe_timestamp'),
     Input('table', 'selected_cell')],
    [State('table', 'dataframe')])
def display_data(*args):
    return html.Pre(json.dumps(args, indent=2))


if __name__ == '__main__':
    app.run_server(debug=True)
