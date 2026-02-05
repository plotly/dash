import itertools
import pytest
from time import sleep
from dash import Dash, Input, Output, html, dcc
import dash.testing.wait as wait


@pytest.mark.DCC594
def test_cdpr001_date_clearable_true_works(dash_dcc):

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(id="dpr", clearable=True),
            dcc.DatePickerSingle(id="dps", clearable=True),
            html.Div(id="dpr-output"),
            html.Div(id="dps-output"),
        ]
    )

    @app.callback(
        Output("dpr-output", "children"),
        Input("dpr", "start_date"),
        Input("dpr", "end_date"),
    )
    def display_range_dates(start_date, end_date):
        return f"Range: {start_date} - {end_date}"

    @app.callback(
        Output("dps-output", "children"),
        Input("dps", "date"),
    )
    def display_single_date(date):
        return f"Single: {date}"

    dash_dcc.start_server(app)

    # DPR
    start_date, end_date = dash_dcc.select_date_range("dpr", (1, 28))
    close_btn = dash_dcc.wait_for_element("#dpr-wrapper .dash-datepicker-clear")

    assert (
        "1" in start_date and "28" in end_date
    ), "both start date and end date should match the selected day"

    # Verify callback received the dates
    dash_dcc.wait_for_text_to_equal("#dpr-output", f"Range: {start_date} - {end_date}")

    close_btn.click()
    sleep(0.25)
    start_date, end_date = dash_dcc.get_date_range("dpr")
    assert not start_date and not end_date, "both start and end dates should be cleared"

    # Verify callback received the cleared dates (None)
    dash_dcc.wait_for_text_to_equal("#dpr-output", "Range: None - None")

    # DPS
    selected = dash_dcc.select_date_single("dps", day="1")

    assert selected, "single date should get a value"

    # Verify callback received the date
    dash_dcc.wait_for_text_to_equal("#dps-output", f"Single: {selected}")

    close_btn = dash_dcc.wait_for_element("#dps-wrapper .dash-datepicker-clear")
    close_btn.click()
    sleep(0.25)
    (single_date,) = dash_dcc.get_date_range("dps")
    assert not single_date, "date should be cleared"

    # Verify callback received the cleared date (None)
    dash_dcc.wait_for_text_to_equal("#dps-output", "Single: None")

    assert dash_dcc.get_logs() == []


def test_cdpr002_updatemodes(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="date-picker-range",
                display_format="MM/DD/YYYY",
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
