import time

from selenium.webdriver.common.keys import Keys

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


def test_grgp001_clean_purge(dash_duo):
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.Button("toggle children", id="tog"),
        html.Div(id="out")
    ])

    @app.callback(
        Output("out", "children"),
        [Input("tog", "n_clicks")]
    )
    def show_output(num):
        if (num or 0) % 2:
            return dcc.Graph(figure={
                "data": [{
                    "type": "scatter3d", "x": [1, 2], "y": [3, 4], "z": [5, 6]
                }],
                "layout": {"title": {"text": "A graph!"}}
            })
        else:
            return "No graphs here!"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "No graphs here!")

    tog = dash_duo.find_element("#tog")
    tog.click()
    dash_duo.wait_for_text_to_equal("#out .gtitle", "A graph!")

    tog.click()
    dash_duo.wait_for_text_to_equal("#out", "No graphs here!")

    dash_duo.find_element('body').send_keys(Keys.CONTROL)

    # the error with CONTROL was happening in an animation frame loop
    # wait a little to ensure it has fired
    time.sleep(0.5)
    assert not dash_duo.get_logs()

    tog.click()
    dash_duo.wait_for_text_to_equal("#out .gtitle", "A graph!")
