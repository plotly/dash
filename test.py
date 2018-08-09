import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

app = dash.Dash()
app.scripts.config.serve_locally = True

app.layout = html.Div([
    html.Button(id='click', children='click'),
    html.Div(id='output', children=''),
    dcc.RadioItems(
        id='radio',
        options=[{
            'label': 'good',
            'value': 'good'
            },
            {
            'label': 'bad',
            'value': 'bad'
            }],
        value='good')
])


class MyCustomException(Exception):
    pass


@app.callback(Output('output', 'children'),
              [Input('click', 'n_clicks'),
               Input('radio', 'value')])
def crash_it(clicks, radio):
    print(clicks, radio)
    if radio == 'bad':
        raise MyCustomException("Something bad happened in the back-end")
    return clicks


app.run_server(debug=True, port=8000)
