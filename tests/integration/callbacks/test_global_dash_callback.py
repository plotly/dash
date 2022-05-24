import pytest

import dash
from dash import Input, Output, dcc, html


@pytest.mark.parametrize('rep', [1, 2])
def test_dash_callback_001(dash_duo, rep):
    # run this test twice to ensure global state is properly reset between runs
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="input"),
            html.Div(id="div-1"),
            html.Div(id="div-2"),
            html.Div(id="div-3"),
            html.Div(id="div-4"),
            html.Div(id="div-5"),
        ]
    )

    @dash.callback(Output("div-1", "children"), Input("input", "value"))
    def update_1(value):  # pylint: disable=unused-variable
        return f"Input 1 - rep {rep} - {value}"

    @dash.callback(Output("div-2", "children"), Input("input", "value"))
    def update_2(value):  # pylint: disable=unused-variable
        return f"Input 2 - rep {rep} - {value}"

    @app.callback(Output("div-3", "children"), Input("input", "value"))
    def update_3(value):  # pylint: disable=unused-variable
        return f"Input 3 - rep {rep} - {value}"

    app.clientside_callback(
        f"""
        function (args) {{return ('Input 4 - rep {rep} - ' + args);}}
        """,
        Output("div-4", "children"),
        Input("input", "value"),
    )

    dash.clientside_callback(
        f"""
        function (args) {{return ('Input 5 - rep {rep} - ' + args);}}
        """,
        Output("div-5", "children"),
        Input("input", "value"),
    )

    dash_duo.start_server(app)
    input_element = dash_duo.find_element("#input")
    input_element.send_keys("dash.callback")
    dash_duo.wait_for_text_to_equal("#div-1", f"Input 1 - rep {rep} - dash.callback")
    dash_duo.wait_for_text_to_equal("#div-2", f"Input 2 - rep {rep} - dash.callback")
    dash_duo.wait_for_text_to_equal("#div-3", f"Input 3 - rep {rep} - dash.callback")
    dash_duo.wait_for_text_to_equal("#div-4", f"Input 4 - rep {rep} - dash.callback")
    dash_duo.wait_for_text_to_equal("#div-5", f"Input 5 - rep {rep} - dash.callback")
