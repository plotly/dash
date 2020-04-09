from multiprocessing import Lock

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html


def test_ldcp001_loading_component_initialization(dash_dcc):
    lock = Lock()

    app = dash.Dash(__name__)

    app.layout = html.Div(
        [dcc.Loading([html.Div(id="div-1")], className="loading")], id="root"
    )

    @app.callback(Output("div-1", "children"), [Input("root", "n_clicks")])
    def updateDiv(children):
        with lock:
            return "content"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.find_element(".loading .dash-spinner")
        # ensure inner component is also mounted
        dash_dcc.wait_for_text_to_equal("#div-1", "")

    dash_dcc.wait_for_text_to_equal("#div-1", "content")

    assert not dash_dcc.get_logs()


def test_ldcp002_loading_component_action(dash_dcc):
    lock = Lock()

    app = dash.Dash(__name__)

    app.layout = html.Div(
        [dcc.Loading([html.Div(id="div-1")], className="loading")], id="root"
    )

    @app.callback(Output("div-1", "children"), [Input("root", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed"

        return "content"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_text_to_equal("#div-1", "content")

        dash_dcc.find_element("#root").click()

        dash_dcc.find_element(".loading .dash-spinner")
        # mounted but hidden, so looks like no text
        dash_dcc.wait_for_text_to_equal("#div-1", "")

    dash_dcc.wait_for_text_to_equal("#div-1", "changed")

    assert not dash_dcc.get_logs()


def test_ldcp003_multiple_loading_components(dash_dcc):
    lock = Lock()

    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading([html.Button(id="btn-1")], className="loading-1"),
            dcc.Loading([html.Button(id="btn-2")], className="loading-2"),
        ],
        id="root",
    )

    @app.callback(Output("btn-1", "children"), [Input("btn-2", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed 1"

        return "content 1"

    @app.callback(Output("btn-2", "children"), [Input("btn-1", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed 2"

        return "content 2"

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#btn-1", "content 1")
    dash_dcc.wait_for_text_to_equal("#btn-2", "content 2")

    with lock:
        dash_dcc.find_element("#btn-1").click()

        dash_dcc.find_element(".loading-2 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-2", "")

    dash_dcc.wait_for_text_to_equal("#btn-2", "changed 2")

    with lock:
        dash_dcc.find_element("#btn-2").click()

        dash_dcc.find_element(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-1", "")

    dash_dcc.wait_for_text_to_equal("#btn-1", "changed 1")

    assert not dash_dcc.get_logs()


def test_ldcp004_nested_loading_components(dash_dcc):
    lock = Lock()

    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading(
                [
                    html.Button(id="btn-1"),
                    dcc.Loading([html.Button(id="btn-2")], className="loading-2"),
                ],
                className="loading-1",
            )
        ],
        id="root",
    )

    @app.callback(Output("btn-1", "children"), [Input("btn-2", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed 1"

        return "content 1"

    @app.callback(Output("btn-2", "children"), [Input("btn-1", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed 2"

        return "content 2"

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#btn-1", "content 1")
    dash_dcc.wait_for_text_to_equal("#btn-2", "content 2")

    with lock:
        dash_dcc.find_element("#btn-1").click()

        dash_dcc.find_element(".loading-2 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-2", "")

    dash_dcc.wait_for_text_to_equal("#btn-2", "changed 2")

    with lock:
        dash_dcc.find_element("#btn-2").click()

        dash_dcc.find_element(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-1", "")

    dash_dcc.wait_for_text_to_equal("#btn-1", "changed 1")

    assert not dash_dcc.get_logs()


def test_ldcp005_dynamic_loading_component(dash_dcc):
    lock = Lock()

    app = dash.Dash(__name__, suppress_callback_exceptions=True)

    app.layout = html.Div([html.Button(id="btn-1"), html.Div(id="div-1")])

    @app.callback(Output("div-1", "children"), [Input("btn-1", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is None:
            return

        with lock:
            return html.Div(
                [
                    html.Button(id="btn-2"),
                    dcc.Loading([html.Button(id="btn-3")], className="loading-1"),
                ]
            )

    @app.callback(Output("btn-3", "children"), [Input("btn-2", "n_clicks")])
    def updateDynamic(n_clicks):
        if n_clicks is None:
            return "content"

        with lock:
            return "changed"

    dash_dcc.start_server(app)

    dash_dcc.find_element("#btn-1")
    dash_dcc.wait_for_text_to_equal("#div-1", "")

    dash_dcc.find_element("#btn-1").click()

    dash_dcc.find_element("#div-1 #btn-2")
    dash_dcc.wait_for_text_to_equal("#btn-3", "content")

    with lock:
        dash_dcc.find_element("#btn-2").click()

        dash_dcc.find_element(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-3", "")

    dash_dcc.wait_for_text_to_equal("#btn-3", "changed")

    assert not dash_dcc.get_logs()


def test_ldcp006_children_identity(dash_dcc):
    lock = Lock()

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("click", id="btn"),
            dcc.Loading(dcc.Graph(id="graph"), className="loading"),
        ]
    )

    @app.callback(Output("graph", "figure"), [Input("btn", "n_clicks")])
    def update_graph(n):
        with lock:
            bars = list(range(2, (n or 0) + 5))
            return {
                "data": [{"type": "bar", "x": bars, "y": bars}],
                "layout": {"width": 400, "height": 400},
            }

    def get_graph_visibility():
        return dash_dcc.driver.execute_script(
            "var gd_ = document.querySelector('.js-plotly-plot');"
            "return getComputedStyle(gd_).visibility;"
        )

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.find_element(".loading .dash-spinner")
        dash_dcc.find_element("#graph .js-plotly-plot")
        dash_dcc.driver.execute_script(
            "window.gd = document.querySelector('.js-plotly-plot');"
            "window.gd.__test__ = 'boo';"
        )
        assert get_graph_visibility() == "hidden"

    test_identity = (
        "var gd_ = document.querySelector('.js-plotly-plot');"
        "return gd_ === window.gd && gd_.__test__ === 'boo';"
    )

    assert len(dash_dcc.find_elements(".js-plotly-plot .bars path")) == 3
    assert dash_dcc.driver.execute_script(test_identity)
    assert get_graph_visibility() == "visible"

    with lock:
        dash_dcc.find_element("#btn").click()
        dash_dcc.find_element(".loading .dash-spinner")
        assert len(dash_dcc.find_elements(".js-plotly-plot .bars path")) == 3
        assert dash_dcc.driver.execute_script(test_identity)
        assert get_graph_visibility() == "hidden"

    assert len(dash_dcc.find_elements(".js-plotly-plot .bars path")) == 4
    assert dash_dcc.driver.execute_script(test_identity)
    assert get_graph_visibility() == "visible"
