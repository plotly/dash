# -*- coding: UTF-8 -*-
import dash_html_components as html
import dash_core_components as dcc

import dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


def test_dev001_python_errors(dash_duo):
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="python", children="Python exception", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("python", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            1 / 0
        elif n_clicks == 2:
            raise Exception("Special 2 clicks exception")

    dash_duo.start_app_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.percy_snapshot("devtools - python exception - start")

    dash_duo.find_element("#python").click()
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "1")
    dash_duo.percy_snapshot("devtools - python exception - closed")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - python exception - open")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.find_element("#python").click()
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "2")
    dash_duo.percy_snapshot("devtools - python exception - 2 errors")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - python exception - 2 errors open")


def test_dev002_prevent_update_not_in_error_msg(dash_duo):
    # raising PreventUpdate shouldn't display the error message
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="python", children="Prevent update", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("python", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            raise PreventUpdate
        if n_clicks == 2:
            raise Exception("An actual python exception")

        return "button clicks: {}".format(n_clicks)

    dash_duo.start_app_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    for _ in range(3):
        dash_duo.find_element("#python").click()

    assert (
        dash_duo.find_element("#output").text == "button clicks: 3"
    ), "the click counts correctly in output"

    # two exceptions fired, but only a single exception appeared in the UI:
    # the prevent default was not displayed
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "1")
    dash_duo.percy_snapshot(
        "devtools - prevent update - only a single exception"
    )


def test_dev003_validation_errors_in_place(dash_duo):
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="button", children="update-graph", n_clicks=0),
            dcc.Graph(id="output", figure={"data": [{"y": [3, 1, 2]}]}),
        ]
    )

    # animate is a bool property
    @app.callback(Output("output", "animate"), [Input("button", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            return n_clicks

    dash_duo.start_app_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.wait_for_element("#button").click()
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "1")
    dash_duo.percy_snapshot("devtools - validation exception - closed")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - validation exception - open")


def test_dev004_validation_errors_creation(dash_duo):
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="button", children="update-graph", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    # animate is a bool property
    @app.callback(Output("output", "children"), [Input("button", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            return dcc.Graph(
                id="output", animate=0, figure={"data": [{"y": [3, 1, 2]}]}
            )

    dash_duo.start_app_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.wait_for_element("#button").click()
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "1")
    dash_duo.percy_snapshot("devtools - validation creation exception - closed")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - validation creation exception - open")


def test_dev005_multiple_outputs(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(
                id="multi-output",
                children="trigger multi output update",
                n_clicks=0,
            ),
            html.Div(id="multi-1"),
            html.Div(id="multi-2"),
        ]
    )

    @app.callback(
        [Output("multi-1", "children"), Output("multi-2", "children")],
        [Input("multi-output", "n_clicks")],
    )
    def update_outputs(n_clicks):
        if n_clicks == 0:
            return [
                "Output 1 - {} Clicks".format(n_clicks),
                "Output 2 - {} Clicks".format(n_clicks),
            ]
        else:
            n_clicks / 0

    dash_duo.start_app_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.find_element("#multi-output").click()
    dash_duo.wait_for_text_to_equal(".test-devtools-error-count", "1")
    dash_duo.percy_snapshot("devtools - multi output python exception - closed")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - multi output python exception - open")
