import time
from multiprocessing import Value

import pytest

import dash_html_components as html
import dash_core_components as dcc
import dash_table
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
        dcc.Input(id="a", value="x"),
        html.Div("b", id="b"),
        html.Div("c", id="c"),
        html.Div(id="out")
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


def test_cbmt003_chain_with_table(dash_duo):
    # see https://github.com/plotly/dash/issues/1071
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.Div(id="a1"),
        html.Div(id="a2"),
        html.Div(id="b1"),
        html.H1(id="b2"),
        html.Button("Update", id="button"),
        dash_table.DataTable(id="table"),
    ])

    @app.callback(
        # Changing the order of outputs here fixes the issue
        [Output("a2", "children"), Output("a1", "children")],
        [Input("button", "n_clicks")],
    )
    def a12(n):
        return "a2: {!s}".format(n), "a1: {!s}".format(n)

    @app.callback(Output("b1", "children"), [Input("a1", "children")])
    def b1(a1):
        return "b1: '{!s}'".format(a1)

    @app.callback(
        Output("b2", "children"),
        [Input("a2", "children"), Input("table", "selected_cells")],
    )
    def b2(a2, selected_cells):
        return "b2: '{!s}', {!s}".format(a2, selected_cells)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#a1", "a1: None")
    dash_duo.wait_for_text_to_equal("#a2", "a2: None")
    dash_duo.wait_for_text_to_equal("#b1", "b1: 'a1: None'")
    dash_duo.wait_for_text_to_equal("#b2", "b2: 'a2: None', None")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#a1", "a1: 1")
    dash_duo.wait_for_text_to_equal("#a2", "a2: 1")
    dash_duo.wait_for_text_to_equal("#b1", "b1: 'a1: 1'")
    dash_duo.wait_for_text_to_equal("#b2", "b2: 'a2: 1', None")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#a1", "a1: 2")
    dash_duo.wait_for_text_to_equal("#a2", "a2: 2")
    dash_duo.wait_for_text_to_equal("#b1", "b1: 'a1: 2'")
    dash_duo.wait_for_text_to_equal("#b2", "b2: 'a2: 2', None")


@pytest.mark.parametrize("MULTI", [False, True])
def test_cbmt004_chain_with_sliders(MULTI, dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.Button("Button", id="button"),
        html.Div([
            html.Label(id="label1"),
            dcc.Slider(id="slider1", min=0, max=10, value=0),

        ]),
        html.Div([
            html.Label(id="label2"),
            dcc.Slider(id="slider2", min=0, max=10, value=0),
        ])
    ])

    if MULTI:
        @app.callback(
            [Output("slider1", "value"), Output("slider2", "value")],
            [Input("button", "n_clicks")]
        )
        def update_slider_vals(n):
            if not n:
                raise PreventUpdate
            return n, n
    else:
        @app.callback(Output("slider1", "value"), [Input("button", "n_clicks")])
        def update_slider1_val(n):
            if not n:
                raise PreventUpdate
            return n

        @app.callback(Output("slider2", "value"), [Input("button", "n_clicks")])
        def update_slider2_val(n):
            if not n:
                raise PreventUpdate
            return n

    @app.callback(Output("label1", "children"), [Input("slider1", "value")])
    def update_slider1_label(val):
        return "Slider1 value {}".format(val)

    @app.callback(Output("label2", "children"), [Input("slider2", "value")])
    def update_slider2_label(val):
        return "Slider2 value {}".format(val)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#label1", "")
    dash_duo.wait_for_text_to_equal("#label2", "")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#label1", "Slider1 value 1")
    dash_duo.wait_for_text_to_equal("#label2", "Slider2 value 1")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal("#label1", "Slider1 value 2")
    dash_duo.wait_for_text_to_equal("#label2", "Slider2 value 2")
