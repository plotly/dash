import dash
print(dash.__version__)

from dash.dependencies import Input, Output, State, ClientFunction
import dash_core_components as dcc
import dash_html_components as html



app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='input', value='hello world'),
    html.Div(id='output-clientside'),
    html.Div(id='output-serverside')
])


@app.callback(
    Output('output-serverside', 'children'),
    [Input('input', 'value')])
def update_output(value):
    return 'Server says "{}"'.format(value)


app.callback(
    Output('output-clientside', 'children'),
    [Input('input', 'value')],
    client_function=ClientFunction(
        namespace='clientside',
        function_name='display'
    )
)

if __name__ == '__main__':
    app.run_server(debug=True)
