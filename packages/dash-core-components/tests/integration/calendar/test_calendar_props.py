import itertools
import pytest

import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output
import dash.testing.wait as wait

from consts import DATE_PICKER_DAY_SELECTOR


@pytest.mark.DCC594
def test_cdpr001_date_clearable_true_works(dash_duo):

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(id="dpr", clearable=True),
            dcc.DatePickerSingle(id="dps", clearable=True),
        ]
    )

    dash_duo.start_server(app)

    # DPR
    start_date = dash_duo.find_element('input[aria-label="Start Date"]')
    end_date = dash_duo.find_element('input[aria-label="End Date"]')

    start_date.click()

    dash_duo.find_elements(DATE_PICKER_DAY_SELECTOR)[0].click()
    dash_duo.find_elements(DATE_PICKER_DAY_SELECTOR)[-1].click()

    close_btn = dash_duo.wait_for_element('button[aria-label="Clear Dates"]')

    assert start_date.get_attribute("value") and end_date.get_attribute(
        "value"
    ), "both start date and end date should get values"

    close_btn.click()
    assert not start_date.get_attribute("value") and not end_date.get_attribute(
        "value"
    ), "both start and end dates should be cleared"

    # DPS
    date = dash_duo.find_element("#dps input")
    date.click()

    dash_duo.find_elements(DATE_PICKER_DAY_SELECTOR)[0].click()
    close_btn = dash_duo.wait_for_element("#dps button")

    assert date.get_attribute("value"), "single date should get a value"
    close_btn.click()
    assert not date.get_attribute("value"), "date should be cleared"


def test_cdpr002_updatemodes(dash_duo):
    app = dash.Dash(__name__)

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
        return "{} - {}".format(start_date, end_date)

    dash_duo.start_server(app=app)

    start_date = dash_duo.find_element("#startDate")
    start_date.click()

    end_date = dash_duo.find_element("#endDate")
    end_date.click()

    assert (
        dash_duo.find_element("#date-picker-range-output").text == "None - None"
    ), "the output should not update when both clicked but no selection happen"

    start_date.click()

    dash_duo.find_elements(DATE_PICKER_DAY_SELECTOR)[4].click()
    assert (
        dash_duo.find_element("#date-picker-range-output").text == "None - None"
    ), "the output should not update when only one is selected"

    eday = dash_duo.find_elements(DATE_PICKER_DAY_SELECTOR)[-4]
    wait.until(lambda: eday.is_displayed() and eday.is_enabled(), timeout=2)
    eday.click()

    date_tokens = set(start_date.get_attribute("value").split("/"))
    date_tokens.update(end_date.get_attribute("value").split("/"))

    assert (
        set(
            itertools.chain(
                *[
                    _.split("-")
                    for _ in dash_duo.find_element(
                        "#date-picker-range-output"
                    ).text.split(" - ")
                ]
            )
        )
        == date_tokens
    ), "date should match the callback output"
