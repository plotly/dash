import itertools
import pytest

from dash import Dash, Input, Output, html, dcc
import dash.testing.wait as wait


@pytest.mark.DCC594
def test_cdpr001_date_clearable_true_works(dash_dcc):

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(id="dpr", clearable=True),
            dcc.DatePickerSingle(id="dps", clearable=True),
        ]
    )

    dash_dcc.start_server(app)

    # DPR
    start_date, end_date = dash_dcc.select_date_range("dpr", (1, 28))
    close_btn = dash_dcc.wait_for_element('button[aria-label="Clear Dates"]')

    assert (
        "1" in start_date and "28" in end_date
    ), "both start date and end date should match the selected day"

    close_btn.click()
    start_date, end_date = dash_dcc.get_date_range("dpr")
    assert not start_date and not end_date, "both start and end dates should be cleared"

    # DPS
    selected = dash_dcc.select_date_single("dps", day="1")

    assert selected, "single date should get a value"
    close_btn = dash_dcc.wait_for_element("#dps button")
    close_btn.click()
    (single_date,) = dash_dcc.get_date_range("dps")
    assert not single_date, "date should be cleared"

    assert dash_dcc.get_logs() == []


def test_cdpr002_updatemodes(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="date-picker-range",
                start_date_id="startDate",
                end_date_id="endDate",
                start_date_placeholder_text="Select a start date!",
                end_date_placeholder_text="Select an end date!",
                updatemode="bothdates",
            ),
            html.Div(id="date-picker-range-output"),
        ]
    )

    @app.callback(
        Output("date-picker-range-output", "children"),
        [
            Input("date-picker-range", "start_date"),
            Input("date-picker-range", "end_date"),
        ],
    )
    def update_output(start_date, end_date):
        return f"{start_date} - {end_date}"

    dash_dcc.start_server(app=app)

    start_date = dash_dcc.find_element("#startDate")
    start_date.click()

    end_date = dash_dcc.find_element("#endDate")
    end_date.click()

    assert (
        dash_dcc.find_element("#date-picker-range-output").text == "None - None"
    ), "the output should not update when both clicked but no selection happen"

    start_date.click()

    dash_dcc.find_elements(dash_dcc.date_picker_day_locator)[4].click()
    assert (
        dash_dcc.find_element("#date-picker-range-output").text == "None - None"
    ), "the output should not update when only one is selected"

    eday = dash_dcc.find_elements(dash_dcc.date_picker_day_locator)[-4]
    wait.until(lambda: eday.is_displayed() and eday.is_enabled(), timeout=2)
    eday.click()

    date_tokens = set(start_date.get_attribute("value").split("/"))
    date_tokens.update(end_date.get_attribute("value").split("/"))

    assert (
        set(
            itertools.chain(
                *[
                    _.split("-")
                    for _ in dash_dcc.find_element(
                        "#date-picker-range-output"
                    ).text.split(" - ")
                ]
            )
        )
        == date_tokens
    ), "date should match the callback output"

    assert dash_dcc.get_logs() == []
