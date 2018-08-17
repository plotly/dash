import dash
from dash.dependencies import Input, Output
import dash_table
import dash_html_components as html

app = dash.Dash()

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

dataframe = [
    {'ind': 0, 'temp': 80, 'climate': 'Tropical'},
    {'ind': 1, 'temp': 30, 'climate': 'Snowy'},
    {'ind': 2, 'temp': 20, 'climate': 'Rain Forests'},
]

dataframe2 = [
    {'ind': 0, 'temp': 80, 'climate': 'Tropical'},
    {'ind': 1, 'temp': 30, 'climate': 'Snowy'},
    {'ind': 2, 'temp': 20, 'climate': 'Rain Forests'},
    {'ind': 2, 'temp': 20, 'climate': 'Rain Forests'},
    {'ind': 2, 'temp': 20, 'climate': 'Rain Forests'},
    {'ind': 2, 'temp': 20, 'climate': 'Rain Forests'},
]

app.layout = html.Div([
    dash_table.Table(
        id='table',
        dataframe=dataframe,
        virtualization='be',
        virtualization_settings={
            'displayed_pages': 1,
            'current_page': 0,
            'page_size': 100
        },
        navigation='page',
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
    Output('table', 'dataframe'),
    [Input('table', 'virtualization')]
)
def updateDataframe():
    return dataframe2


@app.callback(
    Output('container', 'children'),
    [
        Input('table', 'virtual_dataframe'),
        Input('table', 'virtual_dataframe_indices')
    ]
)
def updateContainer():
    return html.Pre('<div>Hello</div>')


if __name__ == '__main__':
    app.run_server(debug=True)
