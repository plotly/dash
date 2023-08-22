from multiprocessing import Lock
from selenium.webdriver.common.action_chains import ActionChains
from dash.testing.wait import until

from dash import Dash, Input, Output, dcc, html, no_update


def test_ttbs001_canonical_behavior(dash_dcc):
    lock = Lock()

    loading_text = "Waiting for Godot"

    fig = dict(
        data=[
            dict(
                x=[11, 22, 33], y=[333, 222, 111], mode="markers", marker=dict(size=40)
            )
        ],
        layout=dict(width=400, height=400, margin=dict(l=100, r=100, t=100, b=100)),
    )
    app = Dash(__name__)

    app.layout = html.Div(
        className="container",
        children=[
            dcc.Graph(id="graph", figure=fig, clear_on_unhover=True),
            dcc.Tooltip(id="graph-tooltip", loading_text=loading_text),
        ],
        style=dict(position="relative"),
    )

    # This callback is executed very quickly
    app.clientside_callback(
        """
        function show_tooltip(hoverData) {
            if(!hoverData) {
                return [false, dash_clientside.no_update];
            }
            var pt = hoverData.points[0];
            return [true, pt.bbox];
        }
        """,
        Output("graph-tooltip", "show"),
        Output("graph-tooltip", "bbox"),
        Input("graph", "hoverData"),
    )

    # This callback is executed after 1s to simulate a long-running process
    @app.callback(
        Output("graph-tooltip", "children"),
        Input("graph", "hoverData"),
    )
    def update_tooltip_content(hoverData):
        if hoverData is None:
            return no_update

        with lock:
            # Display the x0 and y0 coordinate
            bbox = hoverData["points"][0]["bbox"]
            return [
                html.P(f"x0={bbox['x0']}, y0={bbox['y0']}"),
            ]

    dash_dcc.start_server(app)

    until(lambda: not dash_dcc.find_element("#graph-tooltip").is_displayed(), 3)

    elem = dash_dcc.find_element("#graph .nsewdrag")

    with lock:
        # hover on the center of the graph
        ActionChains(dash_dcc.driver).move_to_element_with_offset(
            elem, elem.size["width"] / 2, elem.size["height"] / 2
        ).click().perform()
        dash_dcc.wait_for_text_to_equal("#graph-tooltip", loading_text)

    dash_dcc.wait_for_contains_text("#graph-tooltip", "x0=")
    tt_text = dash_dcc.find_element("#graph-tooltip").text
    coords = [float(part.split("=")[1]) for part in tt_text.split(",")]
    assert 175 < coords[0] < 185, "x0 is about 200 minus half a marker size"
    assert 175 < coords[1] < 185, "y0 is about 200 minus half a marker size"

    elem = dash_dcc.find_element("#graph .nsewdrag")

    ActionChains(dash_dcc.driver).move_to_element_with_offset(
        elem, 5, elem.size["height"] - 5
    ).perform()

    until(lambda: not dash_dcc.find_element("#graph-tooltip").is_displayed(), 3)
