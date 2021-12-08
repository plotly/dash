import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Use the following function when accessing the value of 'my-slider'
# in callbacks to transform the output value to logarithmic
def transform_value(value):
    return 10 ** value

app.layout = html.Div([
    dcc.Slider(
        id="none-step-slider",
        min=-5,
        max=20,
        marks={
            i: str(i) for i in range(1, 6)
        },
        step=1,
        value=2,
        vertical=True,
    ),
    dcc.RangeSlider(
        min=0,
        max=10,
        step=None,
        marks={
            0: '0°F',
            3: '3°F',
            5: '5°F',
            7.65: '7.65°F',
            10: '10°F'
        },
        value=[3, 7.65]
    ),
    html.Div(id='updatemode-output-container', style={'margin-top': 20})
])

@app.callback(Output('updatemode-output-container', 'children'),
              Input('none-step-slider', 'value'))
def display_value(value):
    return 'Linear Value: {} | \
            Log Value: {:0.2f}'.format(value, transform_value(value))

if __name__ == '__main__':
    app.run_server(debug=True)
