import pytest
from datetime import date
from dash import Dash, Input, Output, dcc, html

test_cases = [
    {
        "min": date(2026, 1, 1),
        "max": date(2026, 1, 11),
        "step": 2,
        "step_unit": "days",
        "value": date(2026, 1, 5),
    },
    {
        "min": date(2026, 1, 1),
        "max": date(2026, 1, 29),
        "step": 7,
        "step_unit": "days",
        "value": date(2026, 1, 1),
    },
    {
        "min": date(2026, 1, 1),
        "max": date(2026, 12, 1),
        "step": 1,
        "step_unit": "months",
        "value": date(2026, 1, 1),
    },
    {
        "min": date(2026, 1, 1),
        "max": date(2026, 10, 1),
        "step": 3,
        "step_unit": "months",
        "value": date(2026, 4, 1),
    },
]


def slider_value_divisible_by_step(slider_args, slider_value) -> bool:
    if type(slider_value) is str:
        slider_value = slider_value.split()[-1]

    current_date = date.fromisoformat(slider_value)

    if current_date == slider_args["min"] or current_date == slider_args["max"]:
        return True

    step = slider_args["step"]

    if slider_args["step_unit"] == "days":
        remainder = (current_date - slider_args["min"]).days % step
        return remainder == 0

    elif slider_args["step_unit"] == "months":
        year_diff = current_date.year - slider_args["min"].year
        month_diff = current_date.month - slider_args["min"].month
        total_months = (year_diff * 12) + month_diff
        remainder = total_months % step

        if step == 1:
            return True

        if step > 1:
            return remainder in (0, 1, step - 1)

        return remainder == 0


@pytest.mark.parametrize("test_case", test_cases)
def test_dslst001_date_step_params(dash_dcc, test_case):

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DateSlider(id="slider", display_format="YYYY-MM-DD", **test_case),
            html.Div(id="out"),
        ]
    )

    @app.callback(Output("out", "children"), [Input("slider", "value")])
    def update_output(value):
        return f"{value}"

    dash_dcc.start_server(app)
    dash_dcc.driver.set_window_size(800, 600)

    dash_dcc.wait_for_element(".dash-slider-root")
    marks = dash_dcc.find_elements(".dash-slider-mark")

    # Expect to find some amount of marks in between the first and last mark
    assert len(marks) >= 2

    # Every mark must be divisible by the given step
    for mark in marks:
        if mark.text:
            value = mark.text
            assert slider_value_divisible_by_step(test_case, value)

    i = 0.01
    while i < 1:
        slider = dash_dcc.find_element(".dash-slider-root")
        dash_dcc.click_at_coord_fractions(slider, i, 0.5)
        value = dash_dcc.find_element("#out").text
        assert slider_value_divisible_by_step(test_case, value)
        i += 0.05

    assert dash_dcc.get_logs() == []
