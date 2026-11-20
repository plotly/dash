import json
import os

from dash import Dash, dcc, html


def check_graph_config_shape(dash_dcc):
    config_schema = dash_dcc.driver.execute_script(
        "return Plotly.PlotSchema.get().config;"
    )
    with open(os.path.join(dcc.__path__[0], "metadata.json")) as meta:
        graph_meta = json.load(meta)["src/components/Graph.react.js"]
        config_prop_shape = graph_meta["props"]["config"]["type"]["value"]

    ignored_config = [
        "setBackground",
        "showSources",
        "logging",
        "globalTransforms",
        "notifyOnLogging",
        "role",
        "typesetMath",
        "displayNotifier",
    ]

    def crawl(schema, props):
        for prop_name in props:
            assert prop_name in schema, (
                f"Prop {prop_name!r} is in DCC metadata"
                " but not in Plotly.PlotSchema config"
            )

        for item_name, item in schema.items():
            if item_name in ignored_config:
                continue

            assert item_name in props, (
                f"Schema entry {item_name!r} is in Plotly.PlotSchema config"
                " but not in DCC metadata"
            )
            if "valType" not in item:
                crawl(item, props[item_name]["value"])

    crawl(config_schema, config_prop_shape)


def test_grco001_graph_config_matches_plotly_schema(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Graph(
                id="graph",
                figure={
                    "data": [{"x": [1, 2, 3], "y": [3, 1, 2], "type": "bar"}]
                },
            )
        ]
    )

    dash_dcc.start_server(app)
    check_graph_config_shape(dash_dcc)
    assert dash_dcc.get_logs() == []