from dash import (
    Dash,
    Input,
    Output,
    html,
    clientside_callback,
)


def test_cmorsnu001_clientside_multiple_output_return_single_no_update(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("trigger", id="trigger-demo"),
            html.Div("demo1", id="output-demo1"),
            html.Div("demo2", id="output-demo2"),
        ],
        style={"padding": 50},
    )

    clientside_callback(
        """(n_clicks) => {
            try {
                return window.dash_clientside.no_update;
            } catch (e) {
                return [null, null];
            }
        }""",
        Output("output-demo1", "children"),
        Output("output-demo2", "children"),
        Input("trigger-demo", "n_clicks"),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    trigger_clicker = dash_duo.wait_for_element("#trigger-demo")
    trigger_clicker.click()
    dash_duo.wait_for_text_to_equal(
        "#output-demo1",
        "demo1",
    )
    dash_duo.wait_for_text_to_equal(
        "#output-demo2",
        "demo2",
    )
