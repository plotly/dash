from dash import Dash, dcc, html


def test_ddsh001_dropdown_shorthand_properties(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(["a", "b", "c"]),
            dcc.Dropdown(["a", "b", "c"], "b"),
            dcc.Dropdown(["a", 3, "c"]),
            dcc.Dropdown(["a", 3, "c"], 3),
            dcc.Dropdown(["a", True, "c"]),
            dcc.Dropdown(["a", True, "c"], True),
            dcc.Dropdown(["a", 3, "c", True, False]),
            dcc.Dropdown(["a", 3, "c", True, False], False),
            dcc.Dropdown({"one": "One", "two": "Two", "three": "Three"}),
            dcc.Dropdown({"one": "One", "two": "Two", "three": "Three"}, "two"),
            dcc.Dropdown({"one": 1, "two": 2, "three": False}),
            dcc.Dropdown({"one": 1, "two": 2, "three": False}, "three"),
            dcc.Dropdown({"one": 1, "two": True, "three": 3}),
            dcc.Dropdown({"one": 1, "two": True, "three": 3}, "two"),
            dcc.Dropdown(
                [
                    {"label": "one", "value": 1},
                    {"label": "two", "value": True},
                    {"label": "three", "value": 3},
                ]
            ),
            dcc.Dropdown(
                [
                    {"label": "one", "value": 1},
                    {"label": "two", "value": True},
                    {"label": "three", "value": 3},
                ],
                True,
            ),
        ]
    )

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-dropdown")
    dash_dcc.percy_snapshot("ddsh001 - test_ddsh001_dropdown_shorthand_properties")
