import json
import pytest
import pandas as pd
from multiprocessing import Value, Lock
import numpy as np
from time import sleep
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

import dash.testing.wait as wait


@pytest.mark.parametrize("is_eager", [True, False])
def test_grbs001_graph_without_ids(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)
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

    app = Dash(__name__, eager_loading=is_eager)
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
    app = Dash(__name__, suppress_callback_exceptions=True)
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
    app = Dash(__name__, suppress_callback_exceptions=True)
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


def test_grbs005_graph_customdata(dash_dcc):
    app = Dash(__name__)

    df = px.data.tips()
    df["id"] = df.index

    app.layout = html.Div(
        [
            dcc.Graph(
                id="pie-chart",
                figure=go.Figure(
                    data=[
                        go.Pie(
                            labels=df["day"], ids=df["id"].map(str), customdata=df["id"]
                        )
                    ]
                ),
            ),
            dcc.Textarea(id="text-area"),
        ]
    )

    @app.callback(Output("text-area", "value"), Input("pie-chart", "clickData"))
    def handleClick(clickData):
        return json.dumps(clickData)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#pie-chart")

    dash_dcc.find_elements("g .slice")[0].click()

    data = dash_dcc.wait_for_element("#text-area").get_attribute("value")
    assert data != "", "graph clickData must contain data"

    data = json.loads(data)
    assert "customdata" in data["points"][0], "graph clickData must contain customdata"
    assert data["points"][0]["customdata"][0] == data["points"][0]["pointNumbers"][0]


def test_grbs006_graph_update_frames(dash_dcc):
    app = Dash(__name__)

    def get_scatter(multiplier, offset):
        return go.Scatter(
            x=list(map(lambda n: n * multiplier, [0, 1, 2])),
            y=list(map(lambda n: n + offset, [0, 1, 2])),
            mode="markers",
        )

    def get_figure(data, frames, title):
        return go.Figure(
            data=data,
            layout=go.Layout(
                title=title,
                yaxis=dict(range=[-1, 5]),
                xaxis=dict(range=[-3, 3]),
                updatemenus=[
                    dict(
                        type="buttons",
                        buttons=[
                            dict(
                                label="Play",
                                method="animate",
                                args=[
                                    None,
                                    {
                                        "frame": {"duration": 100, "redraw": True},
                                        "fromcurrent": False,
                                        "transition": {
                                            "duration": 500,
                                            "easing": "quadratic-in-out",
                                        },
                                    },
                                ],
                            )
                        ],
                    )
                ],
            ),
            frames=frames,
        )

    app.layout = html.Div(
        [
            html.Label("Choose dataset"),
            dcc.RadioItems(
                id="change-data",
                options=[
                    {"label": "No data", "value": 0},
                    {"label": "Data A", "value": 1},
                    {"label": "Data B", "value": 2},
                ],
                value=0,
            ),
            dcc.Graph(
                id="test-change",
                animate=True,
                animation_options={"frame": {"redraw": True}},
            ),
            html.Div(id="relayout-data"),
        ]
    )

    @app.callback(
        Output("relayout-data", "children"),
        [Input("test-change", "figure")],
    )
    def show_relayout_data(data):
        frames = data.get("frames", [])
        if frames:
            return json.dumps(frames[0]["data"][0]["x"])
        return ""

    @app.callback(
        Output("test-change", "figure"),
        Input("change-data", "value"),
    )
    def set_data(dataset):
        if dataset == 1:
            title = "Dataset A"
            data = get_scatter(1, 0)
            frames = [
                go.Frame(data=get_scatter(1, 1)),
            ]
        elif dataset == 2:
            title = "Dataset B"
            data = get_scatter(-1, 0)
            frames = [
                go.Frame(data=get_scatter(-1, 1)),
            ]
        else:
            title = "Select a dataset"
            data = []
            frames = []

        fig = get_figure(data, frames, title)
        return fig

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#test-change")

    dash_dcc.find_elements('input[type="radio"]')[0].click()
    assert dash_dcc.wait_for_text_to_equal(
        "#relayout-data", ""
    ), "initial graph data must contain empty string"

    dash_dcc.find_elements('input[type="radio"]')[1].click()
    assert dash_dcc.wait_for_text_to_equal(
        "#relayout-data", "[0, 1, 2]"
    ), "graph data must contain frame [0,1,2]"

    dash_dcc.find_elements('input[type="radio"]')[2].click()
    assert dash_dcc.wait_for_text_to_equal(
        "#relayout-data", "[0, -1, -2]"
    ), "graph data must contain frame [0,-1,-2]"


def test_grbs007_graph_scatter_lines_customdata(dash_dcc):
    app = Dash(__name__)

    expected_value = "obj-1"

    scatter_figures = go.Figure(
        data=[
            go.Scatter(
                x=[0, 1, 1, 0, 0],
                y=[1, 1, 2, 2, 1],
                mode="lines",
                fill="toself",
                customdata=[expected_value],
            )
        ]
    )

    app.layout = html.Div(
        [
            dcc.Graph(
                id="scatter-lines",
                figure=scatter_figures,
                style={"width": 600, "height": 300},
            ),
            dcc.Textarea(id="test-text-area"),
        ],
        style={"width": 1000, "height": 500},
    )

    @app.callback(
        Output("test-text-area", "value"), Input("scatter-lines", "clickData")
    )
    def handleClick(clickData):
        return json.dumps(clickData)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#scatter-lines")

    dash_dcc.find_elements("g .xy")[0].click()

    data = dash_dcc.wait_for_element("#test-text-area").get_attribute("value")
    assert data != "", "graph clickData must contain data"

    data = json.loads(data)
    assert "customdata" in data["points"][0], "graph clickData must contain customdata"
    assert data["points"][0]["customdata"][0] == expected_value
