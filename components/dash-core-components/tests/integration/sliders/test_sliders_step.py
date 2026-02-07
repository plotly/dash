import pytest
from dash import Dash, Input, Output, dcc, html
from humanfriendly import parse_size

test_cases = [
    {"step": 2, "min": 0, "max": 10, "value": 6},
    {"step": 3, "min": 0, "max": 100, "value": 33},
    {"step": 0.05, "min": 0, "max": 1, "value": 0.5},
    {"step": 1_000_000, "min": 1e9, "max": 1e10, "value": 1e10},
]


def slider_value_divisible_by_step(slider_args, slider_value) -> bool:
    if type(slider_value) is str:
        slider_value = float(slider_value.split()[-1])

    if slider_value == slider_args["min"] or slider_value == slider_args["max"]:
        return True

    step = slider_args["step"]
    remainder = slider_value % step

    # For float equality, we check if the remainder is close to 0 or close to step
    return remainder < 1e-10 or abs(remainder - step) < 1e-10


@pytest.mark.parametrize("test_case", test_cases)
def test_slst001_step_params(dash_dcc, test_case):

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Slider(id="slider", **test_case),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"{value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)

    slider = dash_dcc.find_element("#slider")
    marks = dash_dcc.find_elements(".dash-slider-mark")

    # Expect to find some amount of marks in between the first and last mark
    assert len(marks) > 2

    # Every mark must be divisible by the given `step`.
    for mark in marks:
        value = parse_size(mark.text)
        assert slider_value_divisible_by_step(test_case, value)

    # Perform multiple clicks along the slider track. After every click, the
    # resulting slider value must be divisible by the step
    i = 0
    while i < 1:
        dash_dcc.click_at_coord_fractions(slider, i, 0.25)
        value = dash_dcc.find_element("#out").text
        assert slider_value_divisible_by_step(test_case, value)
        i += 0.05

    assert dash_dcc.get_logs() == []
