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

    dash_dcc.wait_for_element("#graph .js-plotly-plot")
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


@pytest.mark.skip(reason="customdata has broken with plotly.py 6")
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

    # The clickData callback also fires once on load with clickData=None (value
    # "null"); wait for the click's real payload before parsing, otherwise we
    # race that initial value and json.loads returns None.
    wait.until(
        lambda: (dash_dcc.find_element("#test-text-area").get_attribute("value") or "")
        not in ("", "null"),
        timeout=3,
    )

    data = dash_dcc.find_element("#test-text-area").get_attribute("value")
    assert data != "", "graph clickData must contain data"

    data = json.loads(data)
    assert "customdata" in data["points"][0], "graph clickData must contain customdata"
    assert data["points"][0]["customdata"][0] == expected_value


def test_grbs008_graph_with_empty_figure(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Toggle graph", id="btn"),
            dcc.Graph(
                id="graph",
                figure=None,
            ),
        ]
    )

    @app.callback(Output("graph", "figure"), [Input("btn", "n_clicks")])
    def toggle_figure(n_clicks):
        if int(n_clicks or 0) % 2 == 0:
            # a valid figure
            return go.Figure([], layout=go.Layout(title="Valid Figure"))
        else:
            # an invalid figure
            return None

    dash_dcc.start_server(app)

    # Click the toggle button a couple of times and expect the graph to change between the
    # valid and invalid figures, using the "title" as the indicator.
    dash_dcc.wait_for_element("#graph")
    wait.until(
        lambda: dash_dcc.find_element(".gtitle").text == "Valid Figure", timeout=2
    )

    dash_dcc.find_element("#btn").click()
    wait.until(lambda: len(dash_dcc.find_elements(".gtitle")) == 0, timeout=2)

    dash_dcc.find_element("#btn").click()
    wait.until(
        lambda: dash_dcc.find_element(".gtitle").text == "Valid Figure", timeout=2
    )

    assert dash_dcc.get_logs() == []


def test_grbs009_graph_click_same_point_twice(dash_dcc):
    """Clicking the same point twice should trigger callback both times."""
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Graph(
                id="graph",
                figure=go.Figure(
                    data=[go.Scatter(x=[1, 2, 3], y=[1, 2, 3], mode="markers")],
                ),
                style={"width": 600, "height": 400},
            ),
            html.Div(id="output", children="[]"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("graph", "clickData"),
        prevent_initial_call=True,
    )
    def on_click(click_data):
        # Return the timestamp to verify each click has a unique one
        return json.dumps(click_data.get("timestamp", "missing"))

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")

    # Click on the graph area - uses the drag overlay which receives clicks
    graph = dash_dcc.find_element("#graph .nsewdrag")
    graph.click()

    # Wait for callback to fire and verify timestamp exists
    dash_dcc.wait_for_contains_text("#output", "")
    first_output = dash_dcc.find_element("#output").text
    assert first_output != "[]", "First click should trigger callback"
    assert first_output != '"missing"', "clickData should contain timestamp"

    # Click again - should trigger callback with different timestamp
    graph.click()
    sleep(0.5)
    second_output = dash_dcc.find_element("#output").text
    assert (
        second_output != first_output
    ), "Second click should trigger callback with new timestamp"

    assert dash_dcc.get_logs() == []


def test_grbs010_graph_patch_deeply_nested_figure(dash_dcc):
    """Patching deeply nested figure properties should work correctly."""
    from dash import Patch

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Graph(
                id="graph",
                figure={
                    "data": [
                        {
                            "x": [1, 2, 3],
                            "y": [1, 2, 3],
                            "marker": {"color": "red", "size": 10},
                            "type": "scatter",
                            "mode": "markers",
                        }
                    ],
                    "layout": {"title": {"text": "Initial Title"}},
                },
                style={"width": 600, "height": 400},
            ),
            html.Button("Patch Color", id="patch-color-btn"),
            html.Button("Patch Title", id="patch-title-btn"),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("graph", "figure"),
        Input("patch-color-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def patch_color(n):
        p = Patch()
        p.data[0].marker.color = "blue" if n % 2 else "green"
        return p

    @app.callback(
        Output("graph", "figure", allow_duplicate=True),
        Input("patch-title-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def patch_title(n):
        p = Patch()
        p.layout.title.text = f"Updated Title {n}"
        return p

    @app.callback(
        Output("output", "children"),
        Input("graph", "figure"),
    )
    def show_figure_state(figure):
        color = figure.get("data", [{}])[0].get("marker", {}).get("color", "unknown")
        title = figure.get("layout", {}).get("title", {}).get("text", "unknown")
        return f"color={color}, title={title}"

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")

    # Initial state
    dash_dcc.wait_for_text_to_equal("#output", "color=red, title=Initial Title")

    # Patch the color
    dash_dcc.find_element("#patch-color-btn").click()
    dash_dcc.wait_for_text_to_equal("#output", "color=blue, title=Initial Title")

    # Patch the title
    dash_dcc.find_element("#patch-title-btn").click()
    dash_dcc.wait_for_text_to_equal("#output", "color=blue, title=Updated Title 1")

    # Patch color again - should toggle
    dash_dcc.find_element("#patch-color-btn").click()
    dash_dcc.wait_for_text_to_equal("#output", "color=green, title=Updated Title 1")

    # Multiple rapid patches
    dash_dcc.find_element("#patch-title-btn").click()
    dash_dcc.find_element("#patch-title-btn").click()
    dash_dcc.wait_for_text_to_equal("#output", "color=green, title=Updated Title 3")

    assert dash_dcc.get_logs() == []


def test_grbs011_clickanywhere_hoveranywhere(dash_dcc):
    """
    When clickanywhere and hoveranywhere are enabled, clickData and hoverData include xvals and yvals
    Note - xPixel and yPixel requires Plotly>=7
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Graph(
                id="graph",
                figure=go.Figure(
                    layout=go.Layout(hoveranywhere=True, clickanywhere=True)
                ),
                style={"width": 600, "height": 400},
            ),
            html.Div(id="output", children="[]"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("graph", "clickData"),
        Input("graph", "hoverData"),
        prevent_initial_call=True,
    )
    def on_event(click_data, hover_data):
        result = {
            "click_x": (click_data or {}).get("xvals", [None])[0],
            "click_y": (click_data or {}).get("yvals", [None])[0],
            "hover_x": (hover_data or {}).get("xvals", [None])[0],
            "hover_y": (hover_data or {}).get("yvals", [None])[0],
            "click_xPixel": (click_data or {}).get("xPixel"),
            "click_yPixel": (click_data or {}).get("yPixel"),
            "hover_xPixel": (hover_data or {}).get("xPixel"),
            "hover_yPixel": (hover_data or {}).get("yPixel"),
        }
        return json.dumps(result)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")

    graph = dash_dcc.find_element("#graph .nsewdrag")
    graph.click()

    dash_dcc.wait_for_contains_text("#output", "{")

    out = json.loads(dash_dcc.find_element("#output").text)

    # click/hover anywhere should produce coordinates
    for key in (
        "click_x",
        "click_y",
        "hover_x",
        "hover_y",
        "click_xPixel",
        "click_yPixel",
        "hover_xPixel",
        "hover_yPixel",
    ):
        assert out[key] is not None


def test_grbs012_graph_patch_keeps_relayout_ranges(dash_dcc):
    """Panning/zooming then applying a Patch should keep the new axis range.

    Regression test for https://github.com/plotly/dash/issues/3810 - since
    getLayout() clones the layout, user relayout changes must be synced back
    to the figure prop or a subsequent Patch reverts them.
    """
    from dash import Patch
    from dash.exceptions import PreventUpdate

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Graph(
                id="graph",
                figure={
                    "data": [
                        {
                            "x": list(range(10)),
                            "y": list(range(10)),
                            "type": "scatter",
                            "mode": "lines+markers",
                        }
                    ],
                    "layout": {"xaxis": {"range": [2, 8], "autorange": False}},
                },
                style={"width": 600, "height": 400},
            ),
            html.Div(id="range-output"),
        ]
    )

    @app.callback(
        Output("graph", "figure"),
        Input("graph", "relayoutData"),
        prevent_initial_call=True,
    )
    def on_relayout(relayout_data):
        if not relayout_data or "xaxis.range[0]" not in relayout_data:
            raise PreventUpdate
        # Data-only patch: the axis range must survive from the figure prop
        p = Patch()
        p.data[0].y = [i * 2 for i in range(10)]
        return p

    @app.callback(
        Output("range-output", "children"),
        Input("graph", "figure"),
    )
    def show_range(figure):
        xrange = figure.get("layout", {}).get("xaxis", {}).get("range", "none")
        return json.dumps(xrange)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")
    dash_dcc.wait_for_text_to_equal("#range-output", "[2, 8]")

    # Simulate a user pan - Plotly.relayout fires the same plotly_relayout
    # event as a drag interaction
    dash_dcc.driver.execute_script(
        "Plotly.relayout("
        "document.querySelector('#graph .js-plotly-plot'),"
        "{'xaxis.range[0]': 3, 'xaxis.range[1]': 5})"
    )

    # The relayout triggers the data-only Patch; the panned range must
    # survive in both the figure prop and the rendered graph
    dash_dcc.wait_for_text_to_equal("#range-output", "[3, 5]")

    def rendered_range():
        return dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot')"
            ".layout.xaxis.range"
        )

    wait.until(lambda: rendered_range() == [3, 5], timeout=3)
    # Verify the patch was applied on top of the panned figure
    wait.until(
        lambda: dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot').data[0].y[9]"
        )
        == 18,
        timeout=3,
    )
    assert rendered_range() == [3, 5]

    assert dash_dcc.get_logs() == []


def test_grbs013_graph_uirevision_keeps_zoom(dash_dcc):
    """A zoom must survive new figures and Patches while uirevision is unchanged.

    Regression test for https://github.com/plotly/dash/issues/4093 - syncing
    the zoom into the figure prop must not make plotly.js forget it.
    """
    from dash import Patch
    from selenium.webdriver.common.action_chains import ActionChains

    def make_figure(showlegend):
        return {
            "data": [{"x": list(range(10)), "y": [x**2 for x in range(10)]}],
            "layout": {"showlegend": showlegend, "uirevision": True},
        }

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("figure", id="figure-btn", n_clicks=0),
            html.Button("patch", id="patch-btn", n_clicks=0),
            dcc.Graph(
                id="graph",
                figure=make_figure(True),
                style={"width": 600, "height": 400},
            ),
            html.Div(id="range-output"),
        ]
    )

    @app.callback(
        Output("graph", "figure", allow_duplicate=True),
        Input("figure-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def new_figure(n_clicks):
        return make_figure(n_clicks % 2 == 0)

    @app.callback(
        Output("graph", "figure"),
        Input("patch-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def patch_figure(n_clicks):
        p = Patch()
        p.data[0].y = [(n_clicks + 1) * x**2 for x in range(10)]
        return p

    @app.callback(Output("range-output", "children"), Input("graph", "figure"))
    def show_range(figure):
        return json.dumps(figure["layout"].get("xaxis", {}).get("range"))

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")
    dash_dcc.wait_for_text_to_equal("#range-output", "null")

    def rendered_range():
        return dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot')"
            "._fullLayout.xaxis.range.slice()"
        )

    initial = rendered_range()
    drag = dash_dcc.find_element("#graph .nsewdrag")
    width = drag.size["width"]
    ActionChains(dash_dcc.driver).move_to_element_with_offset(
        drag, -width // 4, 0
    ).click_and_hold().move_by_offset(width // 4, 5).release().perform()
    wait.until(lambda: rendered_range() != initial, timeout=3)
    zoomed = rendered_range()
    # The zoom is synced into the figure prop
    wait.until(lambda: dash_dcc.find_element("#range-output").text != "null", timeout=3)

    dash_dcc.find_element("#figure-btn").click()
    dash_dcc.wait_for_text_to_equal("#range-output", "null")
    sleep(0.5)
    assert rendered_range() == zoomed

    dash_dcc.find_element("#patch-btn").click()
    wait.until(
        lambda: dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot').data[0].y[9]"
        )
        == 162,
        timeout=3,
    )
    dash_dcc.find_element("#figure-btn").click()
    wait.until(
        lambda: dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot').data[0].y[9]"
        )
        == 81,
        timeout=3,
    )
    sleep(0.5)
    assert rendered_range() == zoomed

    assert dash_dcc.get_logs() == []


def test_grbs014_graph_uirevision_keeps_untracked_edit(dash_dcc):
    """An edit that uirevision does not track must not be undone by the sync.

    plotly.js only keeps some layout edits under uirevision (axis ranges,
    shapes, ...). The fix for #4093 must leave the others, like an edited
    legend title, as the user left them.
    """
    from dash import Patch

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("patch", id="patch-btn", n_clicks=0),
            dcc.Graph(
                id="graph",
                figure={
                    "data": [{"y": [1, 3, 2]}, {"y": [2, 1, 3]}],
                    "layout": {
                        "uirevision": True,
                        "showlegend": True,
                        "legend": {"title": {"text": "original"}},
                    },
                },
                config={"editable": True},
            ),
        ]
    )

    @app.callback(
        Output("graph", "figure"),
        Input("patch-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def patch_figure(n_clicks):
        p = Patch()
        p.data[0].y = [n_clicks, 3, 2]
        return p

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element("#graph .main-svg")

    def legend_title():
        return dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot')"
            "._fullLayout.legend.title.text"
        )

    # Same as plotly.js's own guiEdit wrapper for an edit made in the graph
    dash_dcc.driver.execute_script(
        "var gd = document.querySelector('#graph .js-plotly-plot');"
        "gd._fullLayout._guiEditing = true;"
        "Plotly.relayout(gd, {'legend.title.text': 'edited'});"
        "gd._fullLayout._guiEditing = false;"
    )
    wait.until(lambda: legend_title() == "edited", timeout=3)
    sleep(0.5)
    assert legend_title() == "edited"

    dash_dcc.find_element("#patch-btn").click()
    wait.until(
        lambda: dash_dcc.driver.execute_script(
            "return document.querySelector('#graph .js-plotly-plot').data[0].y[0]"
        )
        == 1,
        timeout=3,
    )
    assert legend_title() == "edited"

    assert dash_dcc.get_logs() == []
