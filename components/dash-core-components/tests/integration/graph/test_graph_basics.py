import pytest
import pandas as pd
from multiprocessing import Value, Lock
import numpy as np
from time import sleep

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash.testing.wait as wait


@pytest.mark.parametrize("is_eager", [True, False])
def test_grbs001_graph_without_ids(dash_dcc, is_eager):
    app = dash.Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div(
        [dcc.Graph(className="graph-no-id-1"), dcc.Graph(className="graph-no-id-2")]
    )

    dash_dcc.start_server(app)

    assert not dash_dcc.wait_for_element(".graph-no-id-1").get_attribute(
        "id"
    ), "the graph should contain no more auto-generated id"
    assert not dash_dcc.wait_for_element(".graph-no-id-2").get_attribute(
        "id"
    ), "the graph should contain no more auto-generated id"

    assert dash_dcc.get_logs() == []


@pytest.mark.DCC608
@pytest.mark.parametrize("is_eager", [True, False])
def test_grbs002_wrapped_graph_has_no_infinite_loop(dash_dcc, is_eager):

    df = pd.DataFrame(np.random.randn(50, 50))
    figure = {
        "data": [{"x": df.columns, "y": df.index, "z": df.values, "type": "heatmap"}],
        "layout": {"xaxis": {"scaleanchor": "y"}},
    }

    app = dash.Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div(
        style={
            "backgroundColor": "red",
            "height": "100vmin",
            "width": "100vmin",
            "overflow": "hidden",
            "position": "relative",
        },
        children=[
            dcc.Loading(
                children=[
                    dcc.Graph(
                        id="graph",
                        figure=figure,
                        style={
                            "position": "absolute",
                            "top": 0,
                            "left": 0,
                            "backgroundColor": "blue",
                            "width": "100%",
                            "height": "100%",
                            "overflow": "hidden",
                        },
                    )
                ]
            )
        ],
    )
    call_count = Value("i", 0)

    @app.callback(Output("graph", "figure"), [Input("graph", "relayoutData")])
    def selected_df_figure(selection):
        call_count.value += 1
        figure["data"][0]["x"] = df.columns
        figure["data"][0]["y"] = df.index
        figure["data"][0]["z"] = df.values
        return figure

    dash_dcc.start_server(app)

    wait.until(lambda: dash_dcc.driver.title == "Dash", timeout=2)
    sleep(1)
    # TODO: not sure 2 calls actually makes sense here, shouldn't it be 1?
    # but that's what we had as of the 608 fix, PR 621, so let's lock that
    # in for now.
    assert call_count.value == 2

    assert dash_dcc.get_logs() == []


@pytest.mark.DCC672
def test_grbs003_graph_wrapped_in_loading_component_does_not_fail(dash_dcc):
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.H1("subplot issue"),
            dcc.Location(id="url", refresh=False),
            dcc.Loading(id="page-content"),
        ]
    )

    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def render_page(url):
        return [
            dcc.Dropdown(
                id="my-dropdown",
                options=[
                    {"label": "option 1", "value": "1"},
                    {"label": "option 2", "value": "2"},
                ],
                value="1",
            ),
            dcc.Graph(id="my-graph"),
        ]

    @app.callback(Output("my-graph", "figure"), [Input("my-dropdown", "value")])
    def update_graph(value):
        values = [1, 2, 3]
        ranges = [1, 2, 3]

        return {
            "data": [{"x": ranges, "y": values, "line": {"shape": "spline"}}],
        }

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#my-graph .main-svg")

    assert dash_dcc.get_logs() == []


@pytest.mark.DCC837
def test_grbs004_graph_loading_state_updates(dash_dcc):
    lock = Lock()
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            html.H1(id="title", children="loading state updates"),
            dcc.Graph(id="my-graph"),
        ]
    )

    @app.callback(Output("my-graph", "figure"), [Input("title", "n_clicks")])
    def update_graph(n_clicks):
        values = [0, n_clicks]
        ranges = [0, n_clicks]

        with lock:
            return {
                "data": [{"x": ranges, "y": values, "line": {"shape": "spline"}}],
            }

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#my-graph:not([data-dash-is-loading])")

    with lock:
        title = dash_dcc.wait_for_element("#title")
        title.click()
        dash_dcc.wait_for_element('#my-graph[data-dash-is-loading="true"]')

    dash_dcc.wait_for_element("#my-graph:not([data-dash-is-loading])")

    assert dash_dcc.get_logs() == []
