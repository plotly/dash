from dash import Dash, dcc, html
import numpy as np
import math


def test_slsh001_rangeslider_shorthand_props(dash_dcc):
    NUMBERS = [10 * N for N in np.arange(1, 2, 0.5)]
    # TEST_RANGES = []
    LAYOUT = []
    TEST_CASES = []

    for n in NUMBERS:
        TEST_CASES.extend(
            [
                [n, n * 1.5, abs(n * 1.5 - n) / 5],
                [-n, 0, n / 10],
                [-n, n, n / 10],
                [-1.5 * n, -1 * n, n / 7],
            ]
        )

    for t in TEST_CASES:
        min, max, steps = t
        marks = {
            i: "Label {}".format(i) if i == 1 else str(i)
            for i in range(math.ceil(min), math.floor(max))
        }

        LAYOUT.extend(
            [
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.Slider(min, max),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.RangeSlider(min, max),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}, {steps}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.Slider(min, max, steps),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}, {steps}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.RangeSlider(min, max, steps),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}, {steps}, value={min + steps}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.Slider(min, max, steps, value=min + steps),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}, {steps}, value=[{min + steps},{min + steps * 3}]",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.RangeSlider(
                            min, max, steps, value=[min + steps, min + steps * 3]
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}, {steps}, value={min + steps}, marks={marks}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.Slider(
                            min,
                            max,
                            steps,
                            value=min + steps,
                            marks=marks,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div(
                            f"{min} - {max}, {steps},value=[{min + steps},{min + steps * 3}], marks={marks}",
                            style={"marginBottom": 15, "marginTop": 25},
                        ),
                        dcc.RangeSlider(
                            min,
                            max,
                            steps,
                            value=[min + steps, min + steps * 3],
                            marks=marks,
                        ),
                    ]
                ),
            ]
        )

    app = Dash(__name__)
    app.layout = html.Div(LAYOUT)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".rc-slider")
    dash_dcc.percy_snapshot("slsh001 - test_slsh001_rangeslider_shorthand_props", True)
