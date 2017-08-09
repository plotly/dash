import dash_date_picker as dp
import dash_html_components as html
from dash.dependencies import *
import dash_core_components as dcc
import dash
import datetime as dt

app = dash.Dash('')

app.layout = html.Div([
     dp.DatePickerRange(id='hello', calendar_orientation='vertical', is_RTL=True),
     dp.DatePickerSingle(id='nah', calendar_orientation='horizontal',
                         day_size=50),
     dp.DatePickerSingle(id='blah', calendar_orientation='horizontal',
                         day_size=50),
     dcc.Graph(id='testing', figure=dict(data=[dict(type='scatter', y=[1, 2, 3, 4])])),
     dcc.Slider(min=0, max=100, step=1, id='slider', value=5),
     dcc.Input(
        id='startdate-input',
        type='Date',
        value=dt.date.today() - dt.timedelta(days=60)
    ),
    html.P(id='holder'),
    html.P(id='holder2'),
    html.P(id='holder3'),
    dcc.Dropdown(
        id='test me',
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        multi=True,
        value="MTL"
    ),
    # dp.DatePickerSingle(id='test',
    #                     initialVisibleMonth={'years': 2013, 'months': 10, 'day': 3},
    #                     clearable=True,
    #                     stayOpenOnSelect=True),
    # dp.DatePicker(startDatePlaceholderText="hello", endDatePlaceholderText="world"),
    # dp.DatePicker(disabled=True),
    # dp.DatePicker(clearable=True, startDate={'year': 2012, 'month': 5, 'day': 3}),
    # dp.DatePicker(stayOpenOnSelect=True),
     html.P(id='hi')
], style={'font-family': 'Sans Serif'})

app.scripts.config.serve_locally=True

@app.callback(Output('holder2', 'children'), [Input('hello', 'start_date')])
def trigger_callback(startDate):
    print startDate
    return 'You have selected {}'.format(startDate)

@app.callback(Output('holder3', 'children'), [Input('hello', 'end_date')])
def trigger_callback(startDate):
    print startDate
    return 'You have selected {}'.format(startDate)

@app.callback(Output('nah', 'date'), [Input('slider', 'value')])
def trigger_callback(value):
    print value
    return dt.datetime(2017, 11, value)

@app.callback(Output('hello', 'start_date'), [Input('slider', 'value')])
def trigger_callback(value):
    print value
    return dt.datetime(2017, 11, value)

@app.callback(Output('holder', 'children'), [Input('nah', 'date')])
def display_date(date):
    print(date)
    return 'You have selected {}'.format(date)


if __name__ == '__main__':
    app.run_server(debug=True)
