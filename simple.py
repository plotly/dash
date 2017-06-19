from dash import Dash
import dash
import dash_html_components as html
import dash_core_components as dcc

app = Dash(__name__)
app.scripts.config.serve_locally=True
app.layout = html.Div([
    dcc.Input(id='my-input', value='initial-input'),
    html.Div(id='my-output')
])


@app.callback(
    dash.dependencies.Output('my-output', 'children'),
    [dash.dependencies.Input('my-input', 'value')]
)
def update(value):
    return 'Output: {}'.format(value)


if __name__ == '__main__':
    app.run_server(debug=True)
