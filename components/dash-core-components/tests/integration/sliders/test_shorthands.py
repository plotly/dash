from dash import Dash, dcc, html
import numpy as np

def test_slsh001_rangeslider_shorthand_props(dash_dcc):
    NUMBERS = [10*N for N in np.arange(0, 2, 0.5)]
    TEST_RANGES = []
    LAYOUT = []
    TEST_CASES = []

    for n in NUMBERS:
        TEST_CASES.extend([
            [n, n * 1.5],
            [n * 0.9, n * 1.3],
            [n * -1, n + 0.1],
            [n * -1.5, n + 0.1],
            [-1 * n, 0.3 * n + 0.1],
            [0, n + 0.1],
            [0, n * 0.43]
        ])

    for t in TEST_CASES:
        LAYOUT.extend([
            html.Div(f'{t[0]} - {t[1]}'),
            dcc.Slider(t[0], t[1]),

            html.Div(f'{t[0]} - {t[1]}, {abs(t[1] - t[0]) / 5}'),
            dcc.Slider(t[0], t[1], abs(t[1] - t[0]) / 5),

            html.Div(f'{t[0]} - {t[1]}'),
            dcc.RangeSlider(t[0], t[1]),

            html.Div(f'{t[0]} - {t[1]}, {abs(t[1] - t[0]) / 5}'),
            dcc.RangeSlider(t[0], t[1], abs(t[1] - t[0]) / 5),
        ])

    app = Dash(__name__)
    app.layout = html.Div(LAYOUT)

    dash_dcc.start_server(app)
    dash_dcc.wait_for_element(".rc-slider")
    dash_dcc.percy_snapshot("slsh001 - test_slsh001_rangeslider_shorthand_props", True)
