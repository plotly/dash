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

    n = 10

    N_K = 10000
    N_M = 10000000
    N_mu = 0.00001

    min_k = -n * N_K
    max_k = (-n + 10) * N_K

    min_M = -n * N_M
    max_M = (n + 10) * N_M

    min_mu = -n * N_mu
    max_mu = (-n + 10) * N_mu

    LAYOUT.extend(
        [
            html.Div(
                [
                    html.Div(
                        f"{min_k} - {max_k}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.Slider(min_k, max_k),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_k} - {max_k}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.RangeSlider(min_k, max_k),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_M} - {max_M}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.Slider(min_M, max_M),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_M} - {max_M}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.RangeSlider(min_M, max_M),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_mu} - {max_mu}, {N_mu}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.Slider(min_mu, max_mu, N_mu),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_mu} - {max_mu}, {N_mu}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.RangeSlider(min_mu, max_mu, N_mu),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_mu} - {max_mu}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.Slider(min_mu, max_mu),
                ]
            ),
            html.Div(
                [
                    html.Div(
                        f"{min_mu} - {max_mu}",
                        style={"marginBottom": 15, "marginTop": 25},
                    ),
                    dcc.RangeSlider(min_mu, max_mu),
                ]
            ),
        ]
    )
    app = Dash(__name__)
    app.layout = html.Div(LAYOUT)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".rc-slider")
    dash_dcc.percy_snapshot("slsh001 - test_slsh001_rangeslider_shorthand_props", True)
