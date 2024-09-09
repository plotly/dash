from dash import (
    Dash,
    Input,
    Output,
    html,
    clientside_callback,
)


def test_clol001_clientside_outputs_list_by_single_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("trigger", id="trigger-demo"), html.Pre(id="output-demo")],
        style={"padding": 50},
    )

    clientside_callback(
        """(n_clicks) => {
            return JSON.stringify(window.dash_clientside.callback_context.outputs_list);
        }""",
        Output("output-demo", "children"),
        Input("trigger-demo", "n_clicks"),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    trigger_clicker = dash_duo.wait_for_element("#trigger-demo")
    trigger_clicker.click()
    dash_duo.wait_for_text_to_equal(
        "#output-demo",
        '{"id":"output-demo","property":"children"}',
    )


def test_clol002_clientside_outputs_list_by_multiple_output1(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("trigger", id="trigger-demo"),
            html.Pre(id="output-demo1"),
            html.Pre(id="output-demo2"),
        ],
        style={"padding": 50},
    )

    clientside_callback(
        """(n_clicks) => {
            return [JSON.stringify(window.dash_clientside.callback_context.outputs_list), JSON.stringify(window.dash_clientside.callback_context.outputs_list)];
        }""",
        [Output("output-demo1", "children"), Output("output-demo2", "children")],
        Input("trigger-demo", "n_clicks"),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#trigger-demo").click()
    dash_duo.wait_for_text_to_equal(
        "#output-demo1",
        '[{"id":"output-demo1","property":"children"},{"id":"output-demo2","property":"children"}]',
    )
    dash_duo.wait_for_text_to_equal(
        "#output-demo2",
        '[{"id":"output-demo1","property":"children"},{"id":"output-demo2","property":"children"}]',
    )


def test_clol003_clientside_outputs_list_by_multiple_output2(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("trigger1", id="trigger-demo1"),
            html.Button("trigger2", id="trigger-demo2"),
            html.Pre(id="output-demo1"),
            html.Pre(id="output-demo2"),
        ],
        style={"padding": 50},
    )

    clientside_callback(
        """(n_clicks1, n_clicks2) => {
            if (window.dash_clientside.callback_context.triggered_id === 'trigger-demo1') {
                return [JSON.stringify(window.dash_clientside.callback_context.outputs_list), window.dash_clientside.no_update];
            } else if (window.dash_clientside.callback_context.triggered_id === 'trigger-demo2') {
                return [window.dash_clientside.no_update, JSON.stringify(window.dash_clientside.callback_context.outputs_list)];
            }
            return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        }""",
        [Output("output-demo1", "children"), Output("output-demo2", "children")],
        [Input("trigger-demo1", "n_clicks"), Input("trigger-demo2", "n_clicks")],
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#trigger-demo1").click()
    dash_duo.wait_for_text_to_equal(
        "#output-demo1",
        '[{"id":"output-demo1","property":"children"},{"id":"output-demo2","property":"children"}]',
    )
    dash_duo.find_element("#trigger-demo2").click()
    dash_duo.wait_for_text_to_equal(
        "#output-demo2",
        '[{"id":"output-demo1","property":"children"},{"id":"output-demo2","property":"children"}]',
    )


def test_clol004_clientside_outputs_list_by_no_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button("trigger", id="trigger-demo"), html.Pre(id="output-demo")],
        style={"padding": 50},
    )

    clientside_callback(
        """(n_clicks) => {
            window.dash_clientside.set_props('output-demo', {'children': JSON.stringify(window.dash_clientside.callback_context.outputs_list)});
        }""",
        Input("trigger-demo", "n_clicks"),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#trigger-demo").click()
    dash_duo.wait_for_text_to_equal(
        "#output-demo",
        "",
    )
