from multiprocessing import Lock
from dash import Dash, Input, Output, dcc, html
from dash.testing import wait
import time


def test_ldcp001_loading_component_initialization(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

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

    assert dash_dcc.get_logs() == []


def test_ldcp002_loading_component_action(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

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

    assert dash_dcc.get_logs() == []


def test_ldcp003_multiple_loading_components(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading([html.Button(id="btn-1")], className="loading-1"),
            dcc.Loading([html.Button(id="btn-2")], className="loading-2"),
        ],
        id="root",
    )

    @app.callback(Output("btn-1", "children"), [Input("btn-2", "n_clicks")])
    def updateDiv1(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed 1"

        return "content 1"

    @app.callback(Output("btn-2", "children"), [Input("btn-1", "n_clicks")])
    def updateDiv2(n_clicks):
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

    assert dash_dcc.get_logs() == []


def test_ldcp004_nested_loading_components(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

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
    def updateDiv1(n_clicks):
        if n_clicks is not None:
            with lock:
                return "changed 1"

        return "content 1"

    @app.callback(Output("btn-2", "children"), [Input("btn-1", "n_clicks")])
    def updateDiv2(n_clicks):
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

    assert dash_dcc.get_logs() == []


def test_ldcp005_dynamic_loading_component(dash_dcc):
    lock = Lock()

    app = Dash(__name__, suppress_callback_exceptions=True)

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

    assert dash_dcc.get_logs() == []


def test_ldcp006_children_identity(dash_dcc):
    lock = Lock()

    app = Dash(__name__)
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

    wait.until(
        lambda: len(dash_dcc.find_elements(".js-plotly-plot .bars path")) == 3, 3
    )
    assert dash_dcc.driver.execute_script(test_identity)
    assert get_graph_visibility() == "visible"

    with lock:
        dash_dcc.find_element("#btn").click()
        dash_dcc.find_element(".loading .dash-spinner")
        assert len(dash_dcc.find_elements(".js-plotly-plot .bars path")) == 3
        assert dash_dcc.driver.execute_script(test_identity)
        assert get_graph_visibility() == "hidden"

    wait.until(
        lambda: len(dash_dcc.find_elements(".js-plotly-plot .bars path")) == 4, 3
    )
    assert dash_dcc.driver.execute_script(test_identity)
    assert get_graph_visibility() == "visible"

    assert dash_dcc.get_logs() == []


def test_ldcp007_class_and_style_props(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("click", id="btn"),
            dcc.Loading(
                id="loading",
                className="spinner-class",
                parent_className="parent-class",
                style={"background-color": "rgb(255,192,203)"},
                # rgb(240, 248, 255) = aliceblue
                parent_style={"border": "3px solid rgb(240, 248, 255)"},
                children=html.Div(id="loading-child"),
            ),
        ]
    )

    @app.callback(Output("loading-child", "children"), [Input("btn", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks is None:
            return

        with lock:
            return "sample text content"

    dash_dcc.start_server(app)

    dash_dcc.wait_for_style_to_equal(
        ".parent-class", "border-color", "rgb(240, 248, 255)"
    )

    with lock:
        button = dash_dcc.find_element("#btn")
        button.click()
        dash_dcc.wait_for_style_to_equal(
            ".spinner-class", "background-color", "rgba(255, 192, 203, 1)"
        )

    assert dash_dcc.get_logs() == []


def test_ldcp008_graph_in_loading_fits_container_height(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        className="outer-container",
        children=[
            html.Div(
                dcc.Loading(
                    parent_style={"height": "100%"},
                    children=dcc.Graph(
                        style={"height": "100%"},
                        figure={
                            "data": [
                                {
                                    "x": [1, 2, 3, 4],
                                    "y": [4, 1, 6, 9],
                                    "line": {"shape": "spline"},
                                }
                            ]
                        },
                    ),
                ),
            )
        ],
        style={"display": "flex", "height": "300px"},
    )

    dash_dcc.start_server(app)

    with lock:
        dash_dcc.wait_for_style_to_equal(".js-plotly-plot", "height", "300px")

        assert dash_dcc.wait_for_element(".js-plotly-plot").size.get(
            "height"
        ) == dash_dcc.wait_for_element(".outer-container").size.get("height")

    assert dash_dcc.get_logs() == []


def test_ldcp009_loading_component_overlay_style(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading(
                [html.Div(id="div-1")],
                className="loading",
                overlay_style={
                    "visibility": "visible",
                    "opacity": 0.5,
                    "backgroundColor": "white",
                },
            )
        ],
        id="root",
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
        # unlike the default, the content should be visible
        dash_dcc.wait_for_text_to_equal("#div-1", "content")
        dash_dcc.wait_for_style_to_equal("#root > div", "opacity", "0.5")

    dash_dcc.wait_for_text_to_equal("#div-1", "changed")

    assert dash_dcc.get_logs() == []


# multiple components, only one triggers the spinner
def test_ldcp010_loading_component_target_components(dash_dcc):

    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading(
                [
                    html.Button(id="btn-1"),
                    html.Button(id="btn-2"),
                ],
                className="loading-1",
                target_components={"btn-2": "children"},
            )
        ],
        id="root",
    )

    @app.callback(Output("btn-1", "children"), [Input("btn-2", "n_clicks")])
    def updateDiv1(n_clicks):
        if n_clicks:
            with lock:
                return "changed 1"

        return "content 1"

    @app.callback(Output("btn-2", "children"), [Input("btn-1", "n_clicks")])
    def updateDiv2(n_clicks):
        if n_clicks:
            with lock:
                return "changed 2"

        return "content 2"

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#btn-1", "content 1")
    dash_dcc.wait_for_text_to_equal("#btn-2", "content 2")

    with lock:
        dash_dcc.find_element("#btn-1").click()

        dash_dcc.find_element(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-2", "")

    dash_dcc.wait_for_text_to_equal("#btn-2", "changed 2")

    with lock:
        dash_dcc.find_element("#btn-2").click()
        spinners = dash_dcc.find_elements(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-1", "")

    dash_dcc.wait_for_text_to_equal("#btn-1", "changed 1")
    assert spinners == []

    assert dash_dcc.get_logs() == []


# update multiple props of same component, only targeted id/prop triggers spinner
def test_ldcp011_loading_component_target_components(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading(
                [
                    html.Button(id="btn-1"),
                    html.Button(id="btn-2"),
                    html.Button(id="btn-3"),
                ],
                className="loading-1",
                target_components={"btn-1": "className"},
            )
        ],
        id="root",
    )

    @app.callback(Output("btn-1", "children"), [Input("btn-2", "n_clicks")])
    def updateDiv1(n_clicks):
        if n_clicks:
            with lock:
                return "changed 1"
        return "content 1"

    @app.callback(Output("btn-1", "className"), [Input("btn-3", "n_clicks")])
    def updateDiv2(n_clicks):
        if n_clicks:
            with lock:
                return "new-class"
        return ""

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal("#btn-1", "content 1")

    with lock:
        dash_dcc.find_element("#btn-2").click()

        spinners = dash_dcc.find_elements(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-1", "")
    dash_dcc.wait_for_text_to_equal("#btn-1", "changed 1")
    assert spinners == []

    with lock:
        dash_dcc.find_element("#btn-3").click()

        dash_dcc.find_element(".loading-1 .dash-spinner")
        dash_dcc.wait_for_text_to_equal("#btn-1", "")

    dash_dcc.wait_for_class_to_equal("#btn-1", "new-class")

    assert dash_dcc.get_logs() == []


def test_ldcp012_loading_component_custom_spinner(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading(
                [html.Div(id="div-1")],
                className="loading",
                custom_spinner=html.Div(id="my-spinner"),
            )
        ],
        id="root",
    )

    @app.callback(Output("div-1", "children"), [Input("root", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks:
            with lock:
                return "changed"
        return "content"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_text_to_equal("#div-1", "content")

        dash_dcc.find_element("#root").click()

        dash_spinner = dash_dcc.find_elements(".loading .dash-spinner")
        dash_dcc.find_element("#my-spinner")
        # mounted but hidden, so looks like no text
        dash_dcc.wait_for_text_to_equal("#div-1", "")

    dash_dcc.wait_for_text_to_equal("#div-1", "changed")
    assert dash_spinner == []

    assert dash_dcc.get_logs() == []


def test_ldcp013_loading_component_display_show(dash_dcc):

    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Loading(
                [html.Div("content", id="div-1")], className="loading", display="show"
            )
        ],
        id="root",
    )
    dash_dcc.start_server(app)

    dash_dcc.find_element(".loading .dash-spinner")
    # mounted but hidden, so looks like no text
    dash_dcc.wait_for_text_to_equal("#div-1", "")

    assert dash_dcc.get_logs() == []


# Same as ldcp002, but with the display="hide", the spinner should not show
def test_ldcp014_loading_component_delay_hide(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [dcc.Loading([html.Div(id="div-1")], className="loading", display="hide")],
        id="root",
    )

    @app.callback(Output("div-1", "children"), [Input("root", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks:
            with lock:
                return "changed"
        return "content"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_text_to_equal("#div-1", "content")

        dash_dcc.find_element("#root").click()

        spinners = dash_dcc.find_elements(".loading .dash-spinner")

    dash_dcc.wait_for_text_to_equal("#div-1", "changed")
    assert spinners == []

    assert dash_dcc.get_logs() == []


# Same as ldcp002, but with the delay, the spinner should not show
def test_ldcp015_loading_component_delay_show(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [dcc.Loading([html.Div(id="div-1")], className="loading", delay_show=2500)],
        id="root",
    )

    @app.callback(Output("div-1", "children"), [Input("root", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks:
            with lock:
                return "changed"
        return "content"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_text_to_equal("#div-1", "content")

        dash_dcc.find_element("#root").click()

        spinners = dash_dcc.find_elements(".loading .dash-spinner")
        # mounted but hidden, so looks like no text
        dash_dcc.wait_for_text_to_equal("#div-1", "")

    dash_dcc.wait_for_text_to_equal("#div-1", "changed")
    assert spinners == []

    assert dash_dcc.get_logs() == []


def test_ldcp016_loading_component_delay_hide(dash_dcc):
    lock = Lock()

    app = Dash(__name__)

    app.layout = html.Div(
        [dcc.Loading([html.Div(id="div-1")], className="loading", delay_hide=300)],
        id="root",
    )

    @app.callback(Output("div-1", "children"), [Input("root", "n_clicks")])
    def updateDiv(n_clicks):
        if n_clicks:
            with lock:
                return "changed"
        return "content"

    with lock:
        dash_dcc.start_server(app)
        dash_dcc.wait_for_text_to_equal("#div-1", "content")

        dash_dcc.find_element("#root").click()
        dash_dcc.find_element(".loading .dash-spinner")

    time.sleep(0.2)
    dash_dcc.find_element(".loading .dash-spinner")
    dash_dcc.wait_for_text_to_equal("#div-1", "changed")

    assert dash_dcc.get_logs() == []
