from dash import Dash, dcc, html


def test_ddsh001_dropdown_shorthand_properties(dash_dcc):
    app = Dash(__name__)

    TEST_OPTIONS_N_VALUES = [
        (["a", "b", "c"]),
        (["a", "b", "c"], "b"),
        (["a", 3, "c"]),
        (["a", 3, "c"], 3),
        (["a", True, "c"]),
        (["a", True, "c"], True),
        (["a", 3, "c", True, False]),
        (["a", 3, "c", True, False], False),
        ({"one": "One", "two": "Two", "three": "Three"}),
        ({"one": "One", "two": "Two", "three": "Three"}, "two"),
        ({"one": 1, "two": 2, "three": False}),
        ({"one": 1, "two": 2, "three": False}, "three"),
        ({"one": 1, "two": True, "three": 3}),
        ({"one": 1, "two": True, "three": 3}, "two"),
        (
            [
                {"label": "one", "value": 1},
                {"label": "two", "value": True},
                {"label": "three", "value": 3},
            ]
        ),
        (
            [
                {"label": "one", "value": 1},
                {"label": "two", "value": True},
                {"label": "three", "value": 3},
            ],
            True,
        ),
    ]

    layout = []
    for definition in TEST_OPTIONS_N_VALUES:
        option, value = definition
        layout.extend(
            [html.Div(f"Options={option}, Value={value}"), dcc.Dropdown(option, value)]
        )

    app.layout = html.Div(layout)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-dropdown")
    dash_dcc.percy_snapshot("ddsh001 - test_ddsh001_dropdown_shorthand_properties")
