import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

app = dash.Dash()
app.scripts.config.serve_locally = True

app.layout = html.Div([
    html.Button(id='click', children='click'),
    dcc.Tabs(id='output2', children=[dcc.Tab(), dcc.Tab()]),
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
        value='good'),
    html.Div(id='output1', children=''),
])


class MyCustomException(Exception):
    pass


@app.callback(Output('output1', 'children'),
              [Input('radio', 'value')])
def crash_it(radio):
    if radio == 'bad':
        raise MyCustomException("Something bad happened in the back-end")
    return 'hello'


@app.callback(Output('output2', 'children'),
              [Input('click', 'n_clicks')])
def crash_it2(click):
    if click:
        return None
    return [dcc.Tab('hello'), dcc.Tab('there')]


app.run_server(debug=True, port=8000)
