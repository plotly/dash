import dash
import dash_html_components as html
import dash_core_components as dcc


def test_grbs001_graph_without_ids(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Graph(className="graph-no-id-1"),
            dcc.Graph(className="graph-no-id-2"),
        ]
    )

    dash_duo.start_server(app)

    assert not dash_duo.wait_for_element(".graph-no-id-1").get_attribute(
        "id"
    ), "the graph should contain no more auto-generated id"
    assert not dash_duo.wait_for_element(".graph-no-id-2").get_attribute(
        "id"
    ), "the graph should contain no more auto-generated id"
