# -*- coding: utf-8 -*-
import pytest
import time
import json
from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def findSyncPlotlyJs(scripts):
    for script in scripts:
        if "dash_core_components/plotly-" in script.get_attribute("src"):
            return script


def findAsyncPlotlyJs(scripts):
    for script in scripts:
        if "dash_core_components/async-plotlyjs" in script.get_attribute("src"):
            return script


def findAsyncMathJax(scripts):
    for script in scripts:
        if "dash_core_components/async-mathjax" in script.get_attribute("src"):
            return script


def findSyncMathJax(scripts):
    for script in scripts:
        if "dash_core_components/mathjax" in script.get_attribute("src"):
            return script


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva001_candlestick(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div(
        [
            html.Button(id="button", children="Update Candlestick", n_clicks=0),
            dcc.Graph(id="graph"),
        ]
    )

    @app.callback(Output("graph", "figure"), [Input("button", "n_clicks")])
    def update_graph(n_clicks):
        return {
            "data": [
                {
                    "open": [1] * 5,
                    "high": [3] * 5,
                    "low": [0] * 5,
                    "close": [2] * 5,
                    "x": [n_clicks] * 5,
                    "type": "candlestick",
                }
            ]
        }

    dash_dcc.start_server(app=app)

    button = dash_dcc.wait_for_element("#button")

    # wait for Graph to be ready
    WebDriverWait(dash_dcc.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "#graph .main-svg"))
    )

    dash_dcc.percy_snapshot(
        "candlestick - initial ({})".format("eager" if is_eager else "lazy")
    )
    button.click()
    time.sleep(1)
    dash_dcc.percy_snapshot(
        "candlestick - 1 click ({})".format("eager" if is_eager else "lazy")
    )

    button.click()
    time.sleep(1)
    dash_dcc.percy_snapshot(
        "candlestick - 2 click ({})".format("eager" if is_eager else "lazy")
    )

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva002_graphs_with_different_figures(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)
    app.layout = html.Div(
        [
            dcc.Graph(
                id="example-graph",
                figure={
                    "data": [
                        {"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "SF"},
                        {
                            "x": [1, 2, 3],
                            "y": [2, 4, 5],
                            "type": "bar",
                            "name": u"Montréal",
                        },
                    ],
                    "layout": {"title": "Dash Data Visualization"},
                },
            ),
            dcc.Graph(
                id="example-graph-2",
                figure={
                    "data": [
                        {
                            "x": [20, 24, 33],
                            "y": [5, 2, 3],
                            "type": "bar",
                            "name": "SF",
                        },
                        {
                            "x": [11, 22, 33],
                            "y": [22, 44, 55],
                            "type": "bar",
                            "name": u"Montréal",
                        },
                    ],
                    "layout": {"title": "Dash Data Visualization"},
                },
            ),
            html.Div(id="restyle-data"),
            html.Div(id="relayout-data"),
        ]
    )

    @app.callback(
        Output("restyle-data", "children"),
        [Input("example-graph", "restyleData")],
    )
    def show_restyle_data(data):
        if data is None:  # ignore initial
            return ""
        return json.dumps(data)

    @app.callback(
        Output("relayout-data", "children"),
        [Input("example-graph", "relayoutData")],
    )
    def show_relayout_data(data):
        if data is None or "autosize" in data:  # ignore initial & auto width
            return ""
        return json.dumps(data)

    dash_dcc.start_server(app)

    # use this opportunity to test restyleData, since there are multiple
    # traces on this graph
    legendToggle = dash_dcc.driver.find_element_by_css_selector(
        "#example-graph .traces:first-child .legendtoggle"
    )
    legendToggle.click()
    dash_dcc.wait_for_text_to_equal(
        "#restyle-data", '[{"visible": ["legendonly"]}, [0]]'
    )

    # move snapshot after click, so it's more stable with the wait
    dash_dcc.percy_snapshot(
        "2 graphs with different figures ({})".format("eager" if is_eager else "lazy")
    )

    # and test relayoutData while we're at it
    autoscale = dash_dcc.driver.find_element_by_css_selector("#example-graph .ewdrag")
    autoscale.click()
    autoscale.click()
    dash_dcc.wait_for_text_to_equal("#relayout-data", '{"xaxis.autorange": true}')

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva003_empty_graph(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

    app.layout = html.Div(
        [
            html.Button(id="click", children="Click me"),
            dcc.Graph(
                id="graph",
                figure={"data": [dict(x=[1, 2, 3], y=[1, 2, 3], type="scatter")]},
            ),
        ]
    )

    @app.callback(
        Output("graph", "figure"),
        [Input("click", "n_clicks")],
        [State("graph", "figure")],
    )
    def render_content(click, prev_graph):
        if click:
            return {}
        return prev_graph

    dash_dcc.start_server(app)
    button = dash_dcc.wait_for_element("#click")
    button.click()
    time.sleep(2)  # Wait for graph to re-render
    dash_dcc.percy_snapshot(
        "render-empty-graph ({})".format("eager" if is_eager else "lazy")
    )

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva004_graph_prepend_trace(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

    def generate_with_id(id, data=None):
        if data is None:
            data = [{"x": [10, 11, 12, 13, 14], "y": [0, 0.5, 1, 0.5, 0]}]

        return html.Div(
            [
                html.P(id),
                dcc.Graph(id=id, figure=dict(data=data)),
                html.Div(id="output_{}".format(id)),
            ]
        )

    figs = [
        "trace_will_prepend",
        "trace_will_prepend_with_no_indices",
        "trace_will_prepend_with_max_points",
    ]

    layout = [generate_with_id(id) for id in figs]

    figs.append("trace_will_allow_repeated_prepend")
    data = [{"y": [0, 0, 0]}]
    layout.append(generate_with_id(figs[-1], data))

    figs.append("trace_will_prepend_selectively")
    data = [
        {"x": [10, 11, 12, 13, 14], "y": [0, 0.5, 1, 0.5, 0]},
        {"x": [10, 11, 12, 13, 14], "y": [1, 1, 1, 1, 1]},
    ]
    layout.append(generate_with_id(figs[-1], data))

    layout.append(
        dcc.Interval(
            id="interval_prependablegraph_update",
            interval=10,
            n_intervals=0,
            max_intervals=1,
        )
    )

    layout.append(
        dcc.Interval(
            id="interval_prependablegraph_prependtwice",
            interval=500,
            n_intervals=0,
            max_intervals=2,
        )
    )

    app.layout = html.Div(layout)

    @app.callback(
        Output("trace_will_allow_repeated_prepend", "prependData"),
        [Input("interval_prependablegraph_prependtwice", "n_intervals")],
    )
    def trace_will_allow_repeated_prepend(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        return dict(y=[[0.1, 0.2, 0.3, 0.4, 0.5]])

    @app.callback(
        Output("trace_will_prepend", "prependData"),
        [Input("interval_prependablegraph_update", "n_intervals")],
    )
    def trace_will_prepend(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new]), [0]

    @app.callback(
        Output("trace_will_prepend_selectively", "prependData"),
        [Input("interval_prependablegraph_update", "n_intervals")],
    )
    def trace_will_prepend_selectively(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new]), [1]

    @app.callback(
        Output("trace_will_prepend_with_no_indices", "prependData"),
        [Input("interval_prependablegraph_update", "n_intervals")],
    )
    def trace_will_prepend_with_no_indices(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new])

    @app.callback(
        Output("trace_will_prepend_with_max_points", "prependData"),
        [Input("interval_prependablegraph_update", "n_intervals")],
    )
    def trace_will_prepend_with_max_points(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new]), [0], 7

    for id in figs:

        @app.callback(
            Output("output_{}".format(id), "children"),
            [Input(id, "prependData")],
            [State(id, "figure")],
        )
        def display_data(trigger, fig):
            return json.dumps(fig["data"])

    dash_dcc.start_server(app)

    comparison = json.dumps(
        [
            dict(
                x=[5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                y=[0.1, 0.2, 0.3, 0.4, 0.5, 0, 0.5, 1, 0.5, 0],
            )
        ]
    )
    dash_dcc.wait_for_text_to_equal("#output_trace_will_prepend", comparison)
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_prepend_with_no_indices", comparison
    )
    comparison = json.dumps(
        [
            dict(x=[10, 11, 12, 13, 14], y=[0, 0.5, 1, 0.5, 0]),
            dict(
                x=[5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                y=[0.1, 0.2, 0.3, 0.4, 0.5, 1, 1, 1, 1, 1],
            ),
        ]
    )
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_prepend_selectively", comparison
    )

    comparison = json.dumps(
        [
            dict(
                x=[5, 6, 7, 8, 9, 10, 11],
                y=[0.1, 0.2, 0.3, 0.4, 0.5, 0, 0.5],
            )
        ]
    )
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_prepend_with_max_points", comparison
    )

    comparison = json.dumps(
        [dict(y=[0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5, 0, 0, 0])]
    )
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_allow_repeated_prepend", comparison
    )

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva005_graph_extend_trace(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

    def generate_with_id(id, data=None):
        if data is None:
            data = [{"x": [0, 1, 2, 3, 4], "y": [0, 0.5, 1, 0.5, 0]}]

        return html.Div(
            [
                html.P(id),
                dcc.Graph(id=id, figure=dict(data=data)),
                html.Div(id="output_{}".format(id)),
            ]
        )

    figs = [
        "trace_will_extend",
        "trace_will_extend_with_no_indices",
        "trace_will_extend_with_max_points",
    ]

    layout = [generate_with_id(id) for id in figs]

    figs.append("trace_will_allow_repeated_extend")
    data = [{"y": [0, 0, 0]}]
    layout.append(generate_with_id(figs[-1], data))

    figs.append("trace_will_extend_selectively")
    data = [
        {"x": [0, 1, 2, 3, 4], "y": [0, 0.5, 1, 0.5, 0]},
        {"x": [0, 1, 2, 3, 4], "y": [1, 1, 1, 1, 1]},
    ]
    layout.append(generate_with_id(figs[-1], data))

    layout.append(
        dcc.Interval(
            id="interval_extendablegraph_update",
            interval=10,
            n_intervals=0,
            max_intervals=1,
        )
    )

    layout.append(
        dcc.Interval(
            id="interval_extendablegraph_extendtwice",
            interval=500,
            n_intervals=0,
            max_intervals=2,
        )
    )

    app.layout = html.Div(layout)

    @app.callback(
        Output("trace_will_allow_repeated_extend", "extendData"),
        [Input("interval_extendablegraph_extendtwice", "n_intervals")],
    )
    def trace_will_allow_repeated_extend(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        return dict(y=[[0.1, 0.2, 0.3, 0.4, 0.5]])

    @app.callback(
        Output("trace_will_extend", "extendData"),
        [Input("interval_extendablegraph_update", "n_intervals")],
    )
    def trace_will_extend(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new]), [0]

    @app.callback(
        Output("trace_will_extend_selectively", "extendData"),
        [Input("interval_extendablegraph_update", "n_intervals")],
    )
    def trace_will_extend_selectively(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new]), [1]

    @app.callback(
        Output("trace_will_extend_with_no_indices", "extendData"),
        [Input("interval_extendablegraph_update", "n_intervals")],
    )
    def trace_will_extend_with_no_indices(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new])

    @app.callback(
        Output("trace_will_extend_with_max_points", "extendData"),
        [Input("interval_extendablegraph_update", "n_intervals")],
    )
    def trace_will_extend_with_max_points(n_intervals):
        if n_intervals is None or n_intervals < 1:
            raise PreventUpdate

        x_new = [5, 6, 7, 8, 9]
        y_new = [0.1, 0.2, 0.3, 0.4, 0.5]
        return dict(x=[x_new], y=[y_new]), [0], 7

    for id in figs:

        @app.callback(
            Output("output_{}".format(id), "children"),
            [Input(id, "extendData")],
            [State(id, "figure")],
        )
        def display_data(trigger, fig):
            return json.dumps(fig["data"])

    dash_dcc.start_server(app)

    comparison = json.dumps(
        [
            dict(
                x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                y=[0, 0.5, 1, 0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5],
            )
        ]
    )
    dash_dcc.wait_for_text_to_equal("#output_trace_will_extend", comparison)
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_extend_with_no_indices", comparison
    )
    comparison = json.dumps(
        [
            dict(x=[0, 1, 2, 3, 4], y=[0, 0.5, 1, 0.5, 0]),
            dict(
                x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                y=[1, 1, 1, 1, 1, 0.1, 0.2, 0.3, 0.4, 0.5],
            ),
        ]
    )
    dash_dcc.wait_for_text_to_equal("#output_trace_will_extend_selectively", comparison)

    comparison = json.dumps(
        [
            dict(
                x=[3, 4, 5, 6, 7, 8, 9],
                y=[0.5, 0, 0.1, 0.2, 0.3, 0.4, 0.5],
            )
        ]
    )
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_extend_with_max_points", comparison
    )

    comparison = json.dumps(
        [dict(y=[0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.1, 0.2, 0.3, 0.4, 0.5])]
    )
    dash_dcc.wait_for_text_to_equal(
        "#output_trace_will_allow_repeated_extend", comparison
    )

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva006_unmounted_graph_resize(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager)

    app.layout = html.Div(
        children=[
            dcc.Tabs(
                id="tabs",
                children=[
                    dcc.Tab(
                        label="Tab one",
                        children=[
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="eg-graph-1",
                                        figure={
                                            "data": [
                                                {
                                                    "x": [1, 2, 3],
                                                    "y": [4, 1, 2],
                                                    "type": "scattergl",
                                                    "name": "SF",
                                                },
                                                {
                                                    "x": [1, 2, 3],
                                                    "y": [2, 4, 5],
                                                    "type": "scattergl",
                                                    "name": u"Montréal",
                                                },
                                            ]
                                        },
                                    )
                                ],
                                id="graph-tab-1",
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="Tab two",
                        children=[
                            dcc.Graph(
                                id="eg-graph-2",
                                figure={
                                    "data": [
                                        {
                                            "x": [1, 2, 3],
                                            "y": [1, 4, 1],
                                            "type": "scattergl",
                                            "name": "SF",
                                        },
                                        {
                                            "x": [1, 2, 3],
                                            "y": [1, 2, 3],
                                            "type": "scattergl",
                                            "name": u"Montréal",
                                        },
                                    ]
                                },
                            )
                        ],
                        id="graph-tab-2",
                    ),
                ],
            )
        ]
    )

    dash_dcc.start_server(app)

    try:
        dash_dcc.wait_for_element("#eg-graph-1")
    except Exception as e:
        print(
            dash_dcc.wait_for_element("#_dash-app-content").get_attribute("innerHTML")
        )
        raise e

    WebDriverWait(dash_dcc.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "graph-tab-2"))
    )

    tab_two = dash_dcc.wait_for_element("#graph-tab-2")

    tab_two.click()

    # save the current window size
    window_size = dash_dcc.driver.get_window_size()

    # resize
    dash_dcc.driver.set_window_size(800, 600)

    # set back to original size
    dash_dcc.driver.set_window_size(window_size["width"], window_size["height"])

    assert dash_dcc.get_logs() == []


def test_grva007_external_plotlyjs_prevents_lazy(dash_dcc):
    app = Dash(
        __name__,
        eager_loading=False,
        external_scripts=["https://unpkg.com/plotly.js-dist-min/plotly.min.js"],
    )

    app.layout = html.Div(id="div", children=[html.Button(id="btn")])

    @app.callback(Output("div", "children"), [Input("btn", "n_clicks")])
    def load_chart(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return dcc.Graph(id="output", figure={"data": [{"y": [3, 1, 2]}]})

    dash_dcc.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    # Give time for the async dependency to be requested (if any)
    time.sleep(2)

    scripts = dash_dcc.driver.find_elements(By.CSS_SELECTOR, "script")
    assert findSyncPlotlyJs(scripts) is None
    assert findAsyncPlotlyJs(scripts) is None

    dash_dcc.find_element("#btn").click()

    # Give time for the async dependency to be requested (if any)
    time.sleep(2)

    scripts = dash_dcc.driver.find_elements(By.CSS_SELECTOR, "script")
    assert findSyncPlotlyJs(scripts) is None
    assert findAsyncPlotlyJs(scripts) is None

    assert dash_dcc.get_logs() == []


def test_grva008_shapes_not_lost(dash_dcc):
    # See issue #879 and pr #905
    app = Dash(__name__)

    fig = {"data": [], "layout": {"dragmode": "drawrect"}}
    graph = dcc.Graph(id="graph", figure=fig, style={"height": "400px"})

    app.layout = html.Div(
        [
            graph,
            html.Br(),
            html.Button(id="button", children="Clone figure"),
            html.Div(id="output", children=""),
        ]
    )

    app.clientside_callback(
        """
        function clone_figure(_, figure) {
            const new_figure = {...figure};
            const shapes = new_figure.layout.shapes || [];
            return [new_figure, shapes.length];
        }
        """,
        Output("graph", "figure"),
        Output("output", "children"),
        Input("button", "n_clicks"),
        State("graph", "figure"),
    )

    dash_dcc.start_server(app)
    button = dash_dcc.wait_for_element("#button")
    dash_dcc.wait_for_text_to_equal("#output", "0")

    # Draw a shape
    dash_dcc.click_and_hold_at_coord_fractions("#graph", 0.25, 0.25)
    dash_dcc.move_to_coord_fractions("#graph", 0.35, 0.75)
    dash_dcc.release()

    # Click to trigger an update of the output, the shape should survive
    dash_dcc.wait_for_text_to_equal("#output", "0")
    button.click()
    dash_dcc.wait_for_text_to_equal("#output", "1")

    # Draw another shape
    dash_dcc.click_and_hold_at_coord_fractions("#graph", 0.75, 0.25)
    dash_dcc.move_to_coord_fractions("#graph", 0.85, 0.75)
    dash_dcc.release()

    # Click to trigger an update of the output, the shape should survive
    dash_dcc.wait_for_text_to_equal("#output", "1")
    button.click()
    dash_dcc.wait_for_text_to_equal("#output", "2")

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("mutate_fig", [True, False])
def test_grva009_originals_maintained_for_responsive_override(mutate_fig, dash_dcc):
    # In #905 we made changes to prevent shapes from being lost.
    # This test makes sure that the overrides applied by the `responsive`
    # prop are "undone" when the `responsive` prop changes.

    app = Dash(__name__)

    graph = dcc.Graph(
        id="graph",
        figure={"data": [{"y": [1, 2]}], "layout": {"width": 300, "height": 250}},
        style={"height": "400px", "width": "500px"},
    )
    responsive_size = [500, 400]
    fixed_size = [300, 250]

    app.layout = html.Div(
        [
            graph,
            html.Br(),
            html.Button(id="edit_figure", children="Edit figure"),
            html.Button(id="edit_responsive", children="Edit responsive"),
            html.Div(id="output", children=""),
        ]
    )

    if mutate_fig:
        # Modify the layout in place (which still has changes made by responsive)
        change_fig = """
            figure.layout.title = {text: String(n_fig || 0)};
            const new_figure = {...figure};
        """
    else:
        # Or create a new one each time
        change_fig = """
            const new_figure = {
                data: [{y: [1, 2]}],
                layout: {width: 300, height: 250, title: {text: String(n_fig || 0)}}
            };
        """

    callback = (
        """
        function clone_figure(n_fig, n_resp, figure) {
        """
        + change_fig
        + """
            let responsive = [true, false, 'auto'][(n_resp || 0) % 3];
            return [new_figure, responsive, (n_fig || 0) + ' ' + responsive];
        }
        """
    )

    app.clientside_callback(
        callback,
        Output("graph", "figure"),
        Output("graph", "responsive"),
        Output("output", "children"),
        Input("edit_figure", "n_clicks"),
        Input("edit_responsive", "n_clicks"),
        State("graph", "figure"),
    )

    dash_dcc.start_server(app)
    edit_figure = dash_dcc.wait_for_element("#edit_figure")
    edit_responsive = dash_dcc.wait_for_element("#edit_responsive")

    def graph_dims():
        return dash_dcc.driver.execute_script(
            """
            const layout = document.querySelector('.js-plotly-plot')._fullLayout;
            return [layout.width, layout.height];
            """
        )

    dash_dcc.wait_for_text_to_equal("#output", "0 true")
    dash_dcc.wait_for_text_to_equal(".gtitle", "0")
    assert graph_dims() == responsive_size

    edit_figure.click()
    dash_dcc.wait_for_text_to_equal("#output", "1 true")
    dash_dcc.wait_for_text_to_equal(".gtitle", "1")
    assert graph_dims() == responsive_size

    edit_responsive.click()
    dash_dcc.wait_for_text_to_equal("#output", "1 false")
    dash_dcc.wait_for_text_to_equal(".gtitle", "1")
    assert graph_dims() == fixed_size

    edit_figure.click()
    dash_dcc.wait_for_text_to_equal("#output", "2 false")
    dash_dcc.wait_for_text_to_equal(".gtitle", "2")
    assert graph_dims() == fixed_size

    edit_responsive.click()
    dash_dcc.wait_for_text_to_equal("#output", "2 auto")
    dash_dcc.wait_for_text_to_equal(".gtitle", "2")
    assert graph_dims() == fixed_size

    edit_figure.click()
    dash_dcc.wait_for_text_to_equal("#output", "3 auto")
    dash_dcc.wait_for_text_to_equal(".gtitle", "3")
    assert graph_dims() == fixed_size

    edit_responsive.click()
    dash_dcc.wait_for_text_to_equal("#output", "3 true")
    dash_dcc.wait_for_text_to_equal(".gtitle", "3")
    assert graph_dims() == responsive_size

    assert dash_dcc.get_logs() == []


def test_grva010_external_mathjax_prevents_lazy(dash_dcc):
    app = Dash(
        __name__,
        eager_loading=False,
        external_scripts=["https://cdn.jsdelivr.net/npm/mathjax@3.2.0/es5/tex-svg.js"],
    )

    app.layout = html.Div(id="div", children=[html.Button(id="btn")])

    @app.callback(Output("div", "children"), [Input("btn", "n_clicks")])
    def load_chart(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return dcc.Graph(
            mathjax=True,
            id="output",
            figure={
                "data": [{"y": [3, 1, 2]}],
                "layout": {"title": {"text": "$E=mc^2$"}},
            },
        )

    dash_dcc.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    # Give time for the async dependency to be requested (if any)
    dash_dcc.wait_for_element("button#btn")

    scripts = dash_dcc.driver.find_elements(By.CSS_SELECTOR, "script")
    assert findSyncMathJax(scripts) is None
    assert findAsyncMathJax(scripts) is None

    dash_dcc.find_element("#btn").click()
    dash_dcc.wait_for_element(".gtitle-math")

    scripts = dash_dcc.driver.find_elements(By.CSS_SELECTOR, "script")
    assert findSyncMathJax(scripts) is None
    assert findAsyncMathJax(scripts) is None

    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva011_without_mathjax(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager, assets_folder="../../assets")

    app.layout = html.Div(
        [
            dcc.Graph(
                id="output",
                figure={
                    "data": [{"y": [3, 1, 2]}],
                    "layout": {"title": {"text": "Apple: $2, Orange: $3"}},
                },
            )
        ]
    )

    dash_dcc.start_server(app)
    assert dash_dcc.wait_for_element(".gtitle").text == "Apple: $2, Orange: $3"
    assert dash_dcc.get_logs() == []


@pytest.mark.parametrize("is_eager", [True, False])
def test_grva012_with_mathjax(dash_dcc, is_eager):
    app = Dash(__name__, eager_loading=is_eager, assets_folder="../../assets")

    app.layout = html.Div(
        [
            dcc.Graph(
                mathjax=True,
                id="output",
                figure={
                    "data": [{"y": [3, 1, 2]}],
                    "layout": {"title": {"text": "Equation: $E=mc^2$"}},
                },
            )
        ]
    )

    dash_dcc.start_server(app)
    assert dash_dcc.get_logs() == []
