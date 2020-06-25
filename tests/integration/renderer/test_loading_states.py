from multiprocessing import Lock

import dash
from dash.dependencies import Input, Output

import dash_core_components as dcc
import dash_html_components as html


def test_rdls001_multi_loading_components(dash_duo):
    lock = Lock()

    app = dash.Dash(__name__)

    app.layout = html.Div(
        children=[
            html.H3("Edit text input to see loading state"),
            dcc.Input(id="input-3", value='Input triggers the loading states'),
            dcc.Loading(className="loading-1", children=[
                html.Div(id="loading-output-1")
            ], type="default"),
            html.Div(
                [
                    dcc.Loading(
                        className="loading-2",
                        children=[html.Div([html.Div(id="loading-output-2")])],
                        type="circle",
                    ),
                    dcc.Loading(
                        className="loading-3",
                        children=dcc.Graph(id='graph'),
                        type="cube",
                    )
                ]
            ),
        ],
    )

    @app.callback(
        [
            Output("graph", "figure"),
            Output("loading-output-1", "children"),
            Output("loading-output-2", "children"),
        ],
        [Input("input-3", "value")])
    def input_triggers_nested(value):
        with lock:
            return dict(data=[dict(y=[1, 4, 2, 3])]), value, value

    def wait_for_all_spinners():
        dash_duo.find_element('.loading-1 .dash-spinner.dash-default-spinner')
        dash_duo.find_element('.loading-2 .dash-spinner.dash-sk-circle')
        dash_duo.find_element('.loading-3 .dash-spinner.dash-cube-container')

    def wait_for_no_spinners():
        dash_duo.wait_for_no_elements('.dash-spinner')

    with lock:
        dash_duo.start_server(app)
        wait_for_all_spinners()

    wait_for_no_spinners()

    with lock:
        dash_duo.find_element('#input-3').send_keys('X')
        wait_for_all_spinners()

    wait_for_no_spinners()
