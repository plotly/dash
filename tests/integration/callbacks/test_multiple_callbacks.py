import time
from multiprocessing import Value

import dash_html_components as html
import dash
from dash.dependencies import Input, Output


def test_cbmt001_called_multiple_times_and_out_of_order(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Button(id="input", n_clicks=0), html.Div(id="output")])

    call_count = Value("i", 0)

    @app.callback(Output("output", "children"), [Input("input", "n_clicks")])
    def update_output(n_clicks):
        call_count.value = call_count.value + 1
        if n_clicks == 1:
            time.sleep(1)
        return n_clicks

    dash_duo.start_server(app)
    dash_duo.multiple_click("#input", clicks=3)

    time.sleep(3)

    assert call_count.value == 4, "get called 4 times"
    assert dash_duo.find_element("#output").text == "3", "clicked button 3 times"

    rqs = dash_duo.redux_state_rqs
    assert len(rqs) == 1 and not rqs[0]["rejected"]

    dash_duo.percy_snapshot(
        name="test_callbacks_called_multiple_times_and_out_of_order"
    )
