import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import json
import datetime as dt

app = dash.Dash(__name__)

app.scripts.config.serve_locally = True

styles = {
    'column': {
        'display': 'inline-block',
        'width': '25%',
        'padding': 10,
        'boxSizing': 'border-box',
        'minHeight': '200px'
    },
    'pre': {'border': 'thin lightgrey solid'}
}

app.layout = html.Div([
    dcc.Textarea(id='my-area', value='''
	Hello!

	Let's run some sql.

	SELECT YOLO FROM ****

    '''),

    dcc.DatePickerSingle(
        id='date-picker-single',
        initial_visible_month=dt.datetime(1997, 5, 5),
        min_date_range=dt.datetime(1997, 4, 29),
        max_date_range=dt.datetime(1997, 6, 3),
        show_outside_days=True,
        with_portal=True,
        number_of_months_shown=1,
        placeholder='Try it out!'
    ),

    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=dt.datetime(1997, 5, 10),
        end_date_placeholder_text="Clear the date!",
        initial_visible_month=dt.datetime(1997, 5, 10),
        min_date_range=dt.datetime(1997, 4, 29),
        max_date_range=dt.datetime(1997, 6, 3),
        show_outside_days=True,
        with_portal=True,
        number_of_months_shown=2,
        clearable=True,
        stay_open_on_select=True,
        open_calendar_on_clear=True,
        month_format='MM YY',
        display_format='MMMM D, Y'
    ),

    html.Div(id='output-textarea'),
    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': [1, 2, 3, 4],
                    'y': [4, 1, 3, 5],
                    'text': ['a', 'b', 'c', 'd'],
                    'customdata': ['c.a', 'c.b', 'c.c', 'c.d'],
                    'name': 'Trace 1',
                    'mode': 'markers',
                    'marker': {'size': 12}
                },
                {
                    'x': [1, 2, 3, 4],
                    'y': [9, 4, 1, 4],
                    'text': ['w', 'x', 'y', 'z'],
                    'customdata': ['c.w', 'c.x', 'c.y', 'c.z'],
                    'name': 'Trace 2',
                    'mode': 'markers',
                    'marker': {'size': 12}
                }
            ]
        }
    ),

    html.Div([
        dcc.Markdown("""
            **Hover Data**

            Mouse over values in the graph.
        """.replace('   ', '')),
        html.Pre(id='hover-data', style=styles['pre'])
    ], style=styles['column']),

    html.Div([
        dcc.Markdown("""
            **Click Data**

            Click on points in the graph.
        """.replace('    ', '')),
        html.Pre(id='click-data', style=styles['pre']),
    ], style=styles['column']),

    html.Div([
        dcc.Markdown("""
            **Selection Data**

            Choose the lasso or rectangle tool in the graph's menu
            bar and then select points in the graph.
        """.replace('    ', '')),
        html.Pre(id='selected-data', style=styles['pre']),
    ], style=styles['column']),

    html.Div([
        dcc.Markdown("""
            **Zoom Data**

            Zoom to set the "`relayoutData`" property.
        """.replace('    ', '')),
        html.Pre(id='relayout-data', style=styles['pre']),
    ], style=styles['column'])
])


@app.callback(
    Output('hover-data', 'children'),
    [Input('basic-interactions', 'hoverData')])
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    [Input('basic-interactions', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('selected-data', 'children'),
    [Input('basic-interactions', 'selectedData')])
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


@app.callback(
    Output('relayout-data', 'children'),
    [Input('basic-interactions', 'relayoutData')])
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)


@app.callback(
	Output('output-textarea', 'children'),
 	[Input('my-area', 'value')])
def lah(value):
    return value


if __name__ == '__main__':
    app.run_server(debug=True)
