import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

app.scripts.config.serve_locally=True

app.layout = html.Div([
    dcc.Graph(id='my-graph', figure={'data': [{'x': [1, 2, 3]}]}, config={'editable': True, 'modeBarButtonsToRemove': ['pan2d', 'lasso2d']})
])

if __name__ == '__main__':
    app.run_server(debug=True)
