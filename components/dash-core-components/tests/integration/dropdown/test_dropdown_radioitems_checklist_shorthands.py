from dash import Dash, dcc, html


def test_ddsh001_test_dropdown_radioitems_checklist_shorthands(dash_dcc):
    app = Dash(__name__)

    TEST_OPTIONS_N_VALUES = [
        [["a", "b", "c"]],
        [["a", "b", "c"], "b"],
        [["a", 3, "c"]],
        [["a", 3, "c"], 3],
        [["a", True, "c"]],
        [["a", True, "c"], True],
        [["a", 3, "c", True, False]],
        [["a", 3, "c", True, False], False],
        # {`value1`: `label1`, `value2`, `label2`, ...}
        [{"one": "One", "two": "Two", "three": "Three"}],
        [{"one": "One", "two": "Two", "three": "Three"}, "two"],
        [{"one": 1, "two": 2, "three": False}],
        [{"one": 1, "two": 2, "three": False}, "three"],
        [{"one": 1, "two": True, "three": 3}],
        [{"one": 1, "two": True, "three": 3}, "two"],
        # original options format
        [
            [
                {"label": "one", "value": 1},
                {"label": "two", "value": True},
                {"label": "three", "value": 3},
            ]
        ],
        [
            [
                {"label": "one", "value": 1},
                {"label": "two", "value": True},
                {"label": "three", "value": 3},
            ],
            True,
        ],
    ]

    layout = []
    for definition in TEST_OPTIONS_N_VALUES:
        (option, value) = definition if len(definition) > 1 else [definition[0], None]
        layout.extend(
            [
                html.Div(
                    [
                        html.Div(
                            f"Options={option}, Value={value}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.Dropdown(option, value),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"Options={option}, Value={value}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.RadioItems(option, value=value),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"Options={option}, Value={value}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.Checklist(option, value=[value]),
                    ]
                ),
            ]
        )

    app.layout = html.Div(layout)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".dash-dropdown")
    dash_dcc.percy_snapshot(
        "ddsh001 - test_ddsh001_test_dropdown_radioitems_checklist_shorthands"
    )
