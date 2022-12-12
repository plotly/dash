from multiprocessing import Value

from dash import Dash, html, dcc, Input, Output


def test_rddp001_dependencies_on_components_that_dont_exist(dash_duo):
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [dcc.Input(id="input", value="initial value"), html.Div(id="output-1")]
    )

    output_1_call_count = Value("i", 0)

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        output_1_call_count.value += 1
        return value

    # callback for component that doesn't yet exist in the dom
    # in practice, it might get added by some other callback
    output_2_call_count = Value("i", 0)

    @app.callback(Output("output-2", "children"), [Input("input", "value")])
    def update_output_2(value):
        output_2_call_count.value += 1
        return value

    dash_duo.start_server(app)

    assert dash_duo.find_element("#output-1").text == "initial value"
    assert output_1_call_count.value == 1 and output_2_call_count.value == 0

    dash_duo.find_element("#input").send_keys("a")
    assert dash_duo.find_element("#output-1").text == "initial valuea"

    assert output_1_call_count.value == 2 and output_2_call_count.value == 0

    assert not dash_duo.redux_state_is_loading

    assert dash_duo.get_logs() == []
