import pytest
from multiprocessing import Lock, Value

from dash.g import app as gapp
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html


def test_dash_g_001(dash_duo):
    @gapp.callback(Output('div-1', 'children'), Input('input', 'value'))
    def update_1(value):
        return f'Input 1 - {value}'

    @gapp.callback(Output('div-2', 'children'), Input('input', 'value'))
    def update_2(value):
        return f'Input 2 - {value}'

    app = dash.Dash(__name__)

    @app.callback(Output('div-3', 'children'), Input('input', 'value'))
    def update_3(value):
        return f'Input 3 - {value}'

    app.layout = html.Div([
        dcc.Input(id='input'),

        html.Div(id='div-1'),
        html.Div(id='div-2'),
        html.Div(id='div-3'),
    ])

    dash_duo.start_server(app)
    input = dash_duo.find_element("#input")
    input.send_keys('dash-g')
    dash_duo.wait_for_text_to_equal("#div-1", "Input 1 - dash-g")
    dash_duo.wait_for_text_to_equal("#div-2", "Input 2 - dash-g")
    dash_duo.wait_for_text_to_equal("#div-3", "Input 3 - dash-g")
