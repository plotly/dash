from dash import Dash, html, Output, Input, State, no_update


def test_cbop001_optional_input(dash_duo):
    app = Dash(suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button(id="button1", children="Button 1"),
            html.Div(id="button-container"),
            html.Div(id="test-out"),
            html.Div(id="test-out2"),
        ]
    )

    @app.callback(
        Output("button-container", "children"),
        Input("button1", "n_clicks"),
        State("button-container", "children"),
        prevent_initial_call=True,
    )
    def _(_, c):
        if not c:
            return html.Button(id="button2", children="Button 2")
        return no_update

    @app.callback(
        Output("test-out", "children"),
        Input("button1", "n_clicks"),
        Input("button2", "n_clicks", allow_optional=True),
        prevent_inital_call=True,
    )
    def display(n, n2):
        return f"{n} - {n2}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#button1", "Button 1")
    assert dash_duo.get_logs() == []
    dash_duo.wait_for_text_to_equal("#test-out", "None - None")
    dash_duo.find_element("#button1").click()
    dash_duo.wait_for_text_to_equal("#test-out", "1 - None")

    dash_duo.find_element("#button2").click()
    dash_duo.wait_for_text_to_equal("#test-out", "1 - 1")
    assert dash_duo.get_logs() == []


def test_cbop002_optional_state(dash_duo):
    app = Dash(suppress_callback_exceptions=True)

    app.layout = html.Div(
        [
            html.Button(id="button1", children="Button 1"),
            html.Div(id="button-container"),
            html.Div(id="test-out"),
            html.Div(id="test-out2"),
        ]
    )

    @app.callback(
        Output("button-container", "children"),
        Input("button1", "n_clicks"),
        State("button-container", "children"),
        prevent_initial_call=True,
    )
    def _(_, c):
        if not c:
            return html.Button(id="button2", children="Button 2")
        return no_update

    @app.callback(
        Output("test-out", "children"),
        Input("button1", "n_clicks"),
        State("button2", "n_clicks", allow_optional=True),
        prevent_inital_call=True,
    )
    def display(n, n2):
        return f"{n} - {n2}"

    @app.callback(
        Output("test-out2", "children"),
        Input("button2", "n_clicks", allow_optional=True),
    )
    def test(n):
        if n:
            return n
        return no_update

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#button1", "Button 1")
    assert dash_duo.get_logs() == []
    dash_duo.wait_for_text_to_equal("#test-out", "None - None")
    dash_duo.find_element("#button1").click()
    dash_duo.wait_for_text_to_equal("#test-out", "1 - None")

    dash_duo.find_element("#button2").click()
    dash_duo.wait_for_text_to_equal("#test-out2", "1")
    dash_duo.wait_for_text_to_equal("#test-out", "1 - None")
    dash_duo.find_element("#button1").click()
    dash_duo.wait_for_text_to_equal("#test-out", "2 - 1")
    assert dash_duo.get_logs() == []
