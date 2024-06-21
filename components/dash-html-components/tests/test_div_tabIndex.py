from dash import Dash, Input, Output, State, html


def test_dt001_div_tabindex_accept_string_and_number_type(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="string-div", tabIndex="1"),
            html.Div(id="number-div", tabIndex=1),
            html.Button("string", id="trigger-string"),
            html.Button("number", id="trigger-number"),
            html.Pre(id="output-string-result"),
            html.Pre(id="output-number-result"),
        ],
        style={"padding": 50},
    )

    @app.callback(
        Output("output-string-result", "children"),
        Input("trigger-string", "n_clicks"),
        State("string-div", "tabIndex"),
        prevent_initial_call=True,
    )
    def show_div_tabindex_string_type(n_clicks, tabindex):
        if n_clicks:
            if isinstance(tabindex, str):
                return "success"
        return "fail"

    @app.callback(
        Output("output-number-result", "children"),
        Input("trigger-number", "n_clicks"),
        State("number-div", "tabIndex"),
        prevent_initial_call=True,
    )
    def show_div_tabindex_number_type(n_clicks, tabindex):
        if n_clicks:
            if isinstance(tabindex, int):
                return "success"
        return "fail"

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#trigger-string").click()
    dash_duo.wait_for_element("#trigger-number").click()
    dash_duo.wait_for_text_to_equal(
        "#output-string-result",
        "success",
    )
    dash_duo.wait_for_text_to_equal(
        "#output-number-result",
        "success",
    )
