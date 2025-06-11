import numpy as np
import plotly.graph_objects as go
import pytest
import flaky

from dash import Dash, Input, Output, State, dcc, html
import plotly.graph_objects as go

from dash.exceptions import PreventUpdate
from dash.testing import wait


@pytest.mark.parametrize("responsive", [True, False, None])
@pytest.mark.parametrize("autosize", [True, False, None])
@pytest.mark.parametrize("height", [600, None])
@pytest.mark.parametrize("width", [600, None])
@pytest.mark.parametrize("is_responsive", [True, False, "auto"])
def test_grrs001_graph(dash_dcc, responsive, autosize, height, width, is_responsive):
    app = Dash(__name__, eager_loading=True)

    header_style = dict(padding="10px", backgroundColor="yellow", flex="0 0 100px")

    graph_style = dict(padding="10px", backgroundColor="red", flex="1 0 0")

    card_style = dict(
        display="flex",
        flexFlow="column",
        backgroundColor="green",
        padding="10px",
        height="500px",
        width="1000px",
    )

    header = html.Div(
        id="header",
        style=header_style,
        children=[html.Button(id="resize", children=["Resize"])],
    )

    graph = html.Div(
        style=graph_style,
        children=[
            dcc.Graph(
                id="graph",
                responsive=is_responsive,
                style=dict(height="100%", width="100%"),
                config=dict(responsive=responsive),
                figure=dict(
                    layout=dict(autosize=autosize, height=height, width=width),
                    data=[
                        dict(
                            x=[1, 2, 3, 4],
                            y=[5, 4, 3, 6],
                            line=dict(shape="spline"),
                        )
                    ],
                ),
            )
        ],
    )

    app.layout = html.Div(
        [
            html.Div(
                [
                    f"responsive: {responsive}, ",
                    f"autosize: {autosize}, ",
                    f"height: {height}, ",
                    f"width: {width}, ",
                    f"is_responsive: {is_responsive}",
                ]
            ),
            html.Div(id="card", style=card_style, children=[header, graph]),
        ]
    )

    @app.callback(
        Output("header", "style"),
        [Input("resize", "n_clicks")],
        [State("header", "style")],
    )
    def resize(n_clicks, style):
        if n_clicks is None:
            raise PreventUpdate

        return dict(style, **dict(flex="0 0 200px"))

    dash_dcc.start_server(app)

    # autosize=true|udefined will make the graph fit its parent on first render, responsive has no impact on that behavior
    #
    # responsive=true will make the graph resize only if autosize=true|undefined, interestingly enough, responsive=undefined
    # behaves the same as responsive=false (https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js#L122)

    initial_responsive = is_responsive is True or (
        is_responsive == "auto"
        and autosize is not False
        and (height is None or width is None)
    )

    resize_responsive = is_responsive is True or (
        is_responsive == "auto"
        and responsive is True
        and autosize is not False
        and (height is None or width is None)
    )

    initial_height = (
        360
        if (initial_responsive and (height is None or is_responsive is True))
        else 450
        if height is None
        else height
    )

    resize_height = (
        260
        if (resize_responsive and (height is None or is_responsive is True))
        else initial_height
        if height is None
        else height
    )

    # 500px card minus (100px header + 20px padding) minus (20px padding on container) -> 360px left
    wait.until(
        lambda: dash_dcc.wait_for_element("#graph svg.main-svg").size.get("height", -1)
        == initial_height,
        3,
    )

    dash_dcc.wait_for_element("#resize").click()

    # 500px card minus (200px header + 20px padding) minus (20px padding on container) -> 260px left
    wait.until(
        lambda: dash_dcc.wait_for_element("#graph svg.main-svg").size.get("height", -1)
        == resize_height,
        3,
    )

    assert dash_dcc.get_logs() == []


def test_grrs002_responsive_parent_height(dash_dcc):
    app = Dash(__name__, eager_loading=True)

    x, y = np.random.uniform(size=50), np.random.uniform(size=50)

    fig = go.Figure(
        data=[go.Scattergl(x=x, y=y, mode="markers")],
        layout=dict(margin=dict(l=0, r=0, t=0, b=0), height=600, width=600),
    )

    app.layout = html.Div(
        dcc.Graph(
            id="graph",
            figure=fig,
            responsive=True,
        ),
        style={"borderStyle": "solid", "height": 300, "width": 100},
    )

    dash_dcc.start_server(app)

    wait.until(
        lambda: dash_dcc.wait_for_element("#graph svg.main-svg").size.get("height", -1)
        == 300,
        3,
    )

    assert dash_dcc.get_logs() == []


@flaky.flaky(max_runs=3)
def test_grrs003_graph(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("Generate Figures", id="generate-btn", n_clicks=0),
            html.Button("Get Bounding Box", id="bounding-btn"),
            html.Div(
                id="graph-container",
                children=[
                    html.Div(id="bounding-output"),
                    dcc.Graph(
                        id="prec-climate-daily",
                        style={"height": "45vh"},
                        config={"responsive": True},
                    ),
                    dcc.Graph(
                        id="temp-climate-daily",
                        style={"height": "45vh"},
                        config={"responsive": True},
                    ),
                ],
                style={"display": "none"},
            ),
        ]
    )

    app.clientside_callback(
        """() => {
            pcd_container = document.querySelector("#prec-climate-daily")
            pcd_container_bbox = pcd_container.getBoundingClientRect()
            pcd_graph = pcd_container.querySelector('.main-svg')
            pcd_graph_bbox = pcd_graph.getBoundingClientRect()
            tcd_container = document.querySelector("#temp-climate-daily")
            tcd_container_bbox = tcd_container.getBoundingClientRect()
            tcd_graph = tcd_container.querySelector('.main-svg')
            tcd_graph_bbox = tcd_graph.getBoundingClientRect()
            return JSON.stringify(
            pcd_container_bbox.height == pcd_graph_bbox.height &&
            pcd_container_bbox.width == pcd_graph_bbox.width &&
            tcd_container_bbox.height == tcd_graph_bbox.height &&
            tcd_container_bbox.width == tcd_graph_bbox.width
            )
        }""",
        Output("bounding-output", "children"),
        Input("bounding-btn", "n_clicks"),
        prevent_initial_call=True,
    )

    @app.callback(
        [
            Output("prec-climate-daily", "figure"),
            Output("temp-climate-daily", "figure"),
            Output("graph-container", "style"),
            Output("bounding-output", "children", allow_duplicate=True),
        ],
        [Input("generate-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def update_figures(n_clicks):
        fig_acc = go.Figure(data=[go.Scatter(x=[0, 1, 2], y=[0, 1, 0], mode="lines")])
        fig_daily = go.Figure(data=[go.Scatter(x=[0, 1, 2], y=[1, 0, 1], mode="lines")])
        return fig_acc, fig_daily, {"display": "block"}, "loaded"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_text_to_equal("#generate-btn", "Generate Figures")
    dash_dcc.find_element("#generate-btn").click()
    dash_dcc.wait_for_text_to_equal("#bounding-output", "loaded")
    dash_dcc.wait_for_element(".dash-graph .js-plotly-plot.dash-graph--pending")
    dash_dcc.wait_for_element(".dash-graph .js-plotly-plot:not(.dash-graph--pending)")
    dash_dcc.find_element("#bounding-btn").click()
    dash_dcc.wait_for_text_to_equal("#bounding-output", "true")
