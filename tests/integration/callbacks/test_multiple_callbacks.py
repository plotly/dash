import time
from multiprocessing import Value

import dash_html_components as html
import dash_core_components as dcc
import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


def test_cbmt001_called_multiple_times_and_out_of_order(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="input", n_clicks=0), html.Div(id="output")]
    )

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
    assert (
        dash_duo.find_element("#output").text == "3"
    ), "clicked button 3 times"

    assert dash_duo.redux_state_rqs == []

    dash_duo.percy_snapshot(
        name="test_callbacks_called_multiple_times_and_out_of_order"
    )


def test_cbmt002_canceled_intermediate_callback(dash_duo):
    # see https://github.com/plotly/dash/issues/1053
    app = dash.Dash(__name__)
    app.layout = html.Div([
        dcc.Input(id='a', value="x"),
        html.Div('b', id='b'),
        html.Div('c', id='c'),
        html.Div(id='out')
    ])

    @app.callback(
        Output("out", "children"),
        [Input("a", "value"), Input("b", "children"), Input("c", "children")]
    )
    def set_out(a, b, c):
        return "{}/{}/{}".format(a, b, c)

    @app.callback(Output("b", "children"), [Input("a", "value")])
    def set_b(a):
        raise PreventUpdate

    @app.callback(Output("c", "children"), [Input("a", "value")])
    def set_c(a):
        return a

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out", "x/b/x")
    chars = "x"
    for i in list(range(10)) * 2:
        dash_duo.find_element("#a").send_keys(str(i))
        chars += str(i)
        dash_duo.wait_for_text_to_equal("#out", "{0}/b/{0}".format(chars))
