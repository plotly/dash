from dash import Dash, html, Input, Output, no_update

from dash_test_components import AddPropsComponent, ReceivePropsComponent


def test_rdarp001_add_receive_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            AddPropsComponent(
                ReceivePropsComponent(
                    id="test-receive1",
                    text="receive component1",
                ),
                id="test-add",
            ),
            ReceivePropsComponent(
                id="test-receive2",
                text="receive component2",
            ),
            html.Button(
                "load no pass props",
                id="load-no-pass-props",
            ),
            html.Pre("load-no-pass-props-output"),
            html.Div(id="load-no-pass-props-output"),
            html.Button(
                "load pass props",
                id="load-pass-props",
            ),
            html.Pre("load-pass-props-output"),
            html.Div(id="load-pass-props-output"),
        ]
    )

    @app.callback(
        Output("load-no-pass-props-output", "children"),
        Input("load-no-pass-props", "n_clicks"),
    )
    def load_no_pass_props(n_clicks):
        if n_clicks:
            return ReceivePropsComponent(
                id="test-receive-no-pass",
                text="receive component no pass",
            )
        return no_update

    @app.callback(
        Output("load-pass-props-output", "children"),
        Input("load-pass-props", "n_clicks"),
    )
    def load_pass_props(n_clicks):
        if n_clicks:
            return AddPropsComponent(
                ReceivePropsComponent(
                    id="test-receive-pass",
                    text="receive component pass",
                ),
                id="test-add-pass",
            )
        return no_update

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#test-receive1", "Element #test-add pass")
    dash_duo.wait_for_text_to_equal("#test-receive2", "receive component2")

    clicker_no_pass = dash_duo.wait_for_element("#load-no-pass-props")
    clicker_no_pass.click()
    dash_duo.wait_for_text_to_equal(
        "#test-receive-no-pass", "receive component no pass"
    )
    clicker_pass = dash_duo.wait_for_element("#load-pass-props")
    clicker_pass.click()
    dash_duo.wait_for_text_to_equal("#test-receive-pass", "Element #test-add-pass pass")
