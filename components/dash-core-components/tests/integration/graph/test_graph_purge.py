import pytest
import time

from selenium.webdriver.common.keys import Keys

from dash import Dash, Input, Output, dcc, html


@pytest.mark.parametrize("is_eager", [True, False])
def test_grgp001_clean_purge(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

    app.layout = html.Div(
        [html.Button("toggle children", id="tog"), html.Div(id="out")]
    )

    @app.callback(Output("out", "children"), [Input("tog", "n_clicks")])
    def show_output(num):
        if (num or 0) % 2:
            return dcc.Graph(
                figure={
                    "data": [
                        {"type": "scatter3d", "x": [1, 2], "y": [3, 4], "z": [5, 6]}
                    ],
                    "layout": {"title": {"text": "A graph!"}},
                }
            )
        else:
            return "No graphs here!"

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#out", "No graphs here!")

    tog = dash_dcc.find_element("#tog")
    tog.click()
    dash_dcc.wait_for_text_to_equal("#out .gtitle", "A graph!")

    tog.click()
    dash_dcc.wait_for_text_to_equal("#out", "No graphs here!")

    dash_dcc.find_element("body").send_keys(Keys.CONTROL)

    # the error with CONTROL was happening in an animation frame loop
    # wait a little to ensure it has fired
    time.sleep(0.5)
    assert not dash_dcc.get_logs()

    tog.click()
    dash_dcc.wait_for_text_to_equal("#out .gtitle", "A graph!")

    assert dash_dcc.get_logs() == []
