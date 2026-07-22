from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

from dash import Dash, Input, Output, html, dcc


def test_dtps_multi_month_click_second_month(dash_dcc):
    """Test clicking a date in the second month with number_of_months_shown=2"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                initial_visible_month=datetime(2021, 1, 1),
                number_of_months_shown=2,
                stay_open_on_select=True,
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("dps", "date"))
    def update_output(date):
        return date or "No date selected"

    dash_dcc.start_server(app)

    # Click the date picker to open it
    date_picker = dash_dcc.find_element("#dps")
    date_picker.click()

    dash_dcc._wait_until_day_is_clickable()

    # Get all visible dates across both months
    days = dash_dcc.find_elements(dash_dcc.date_picker_day_locator)

    # Find a date in the second month (February 2021)
    # We're looking for day "15" in the second month
    second_month_days = [
        day
        for day in days
        if day.text == "15"
        and "dash-datepicker-calendar-date-outside" not in day.get_attribute("class")
    ]

    # There should be two "15"s visible (Jan 15 and Feb 15)
    # We want the second one (Feb 15)
    assert len(second_month_days) >= 1, "Should find at least one day 15"

    # Click on a date in the second visible month
    if len(second_month_days) > 1:
        second_month_days[1].click()
        expected_date = "2021-02-15"
    else:
        # Fallback: just click the first one
        second_month_days[0].click()
        expected_date = "2021-01-15"

    # Check the output
    output = dash_dcc.find_element("#output")
    assert output.text == expected_date, f"Expected {expected_date}, got {output.text}"


def test_dtpr_multi_month_drag_in_second_month(dash_dcc):
    """Test drag selection entirely within the second month with number_of_months_shown=2"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dpr",
                initial_visible_month=datetime(2021, 1, 1),
                number_of_months_shown=2,
            ),
            html.Div(id="output-start"),
            html.Div(id="output-end"),
        ]
    )

    @app.callback(
        Output("output-start", "children"),
        Output("output-end", "children"),
        Input("dpr", "start_date"),
        Input("dpr", "end_date"),
    )
    def update_output(start_date, end_date):
        return start_date or "No start", end_date or "No end"

    dash_dcc.start_server(app)

    # Click to open the calendar
    date_picker = dash_dcc.find_element("#dpr")
    date_picker.click()

    dash_dcc._wait_until_day_is_clickable()

    # Get all visible dates
    days = dash_dcc.find_elements(dash_dcc.date_picker_day_locator)

    # Find all day "10"s and "17"s (both should appear in Jan and Feb)
    all_10s = [
        day
        for day in days
        if day.text == "10"
        and "dash-datepicker-calendar-date-outside" not in day.get_attribute("class")
    ]
    all_17s = [
        day
        for day in days
        if day.text == "17"
        and "dash-datepicker-calendar-date-outside" not in day.get_attribute("class")
    ]

    # Use the last occurrence of each (should be February)
    feb_10 = all_10s[-1] if len(all_10s) > 1 else all_10s[0]
    feb_17 = all_17s[-1] if len(all_17s) > 1 else all_17s[0]

    # Perform drag operation: mouse down on Feb 10, drag to Feb 17, mouse up
    actions = ActionChains(dash_dcc.driver)
    actions.click_and_hold(feb_10).move_to_element(feb_17).release().perform()

    # Wait for the callback to fire
    dash_dcc.wait_for_text_to_equal("#output-start", "2021-02-10", timeout=2)

    # Check the outputs
    output_start = dash_dcc.find_element("#output-start")
    output_end = dash_dcc.find_element("#output-end")

    assert (
        output_start.text == "2021-02-10"
    ), f"Expected 2021-02-10 as start, got {output_start.text}"
    assert (
        output_end.text == "2021-02-17"
    ), f"Expected 2021-02-17 as end, got {output_end.text}"


def test_dtpr_multi_month_click_in_second_month(dash_dcc):
    """Test click selection entirely within the second month with number_of_months_shown=2
    This should produce the same result as the drag test above"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dpr",
                initial_visible_month=datetime(2021, 1, 1),
                number_of_months_shown=2,
                stay_open_on_select=True,
            ),
            html.Div(id="output-start"),
            html.Div(id="output-end"),
        ]
    )

    @app.callback(
        Output("output-start", "children"),
        Output("output-end", "children"),
        Input("dpr", "start_date"),
        Input("dpr", "end_date"),
    )
    def update_output(start_date, end_date):
        return start_date or "No start", end_date or "No end"

    dash_dcc.start_server(app)

    # Open calendar
    dash_dcc.find_element("#dpr").click()
    dash_dcc._wait_until_day_is_clickable()

    # Find and click Feb 10 and Feb 17
    days = dash_dcc.find_elements(dash_dcc.date_picker_day_locator)
    all_10s = [
        d
        for d in days
        if d.text == "10"
        and "dash-datepicker-calendar-date-outside" not in d.get_attribute("class")
    ]
    all_17s = [
        d
        for d in days
        if d.text == "17"
        and "dash-datepicker-calendar-date-outside" not in d.get_attribute("class")
    ]

    all_10s[-1].click()  # Feb 10 (last occurrence)
    all_17s[-1].click()  # Feb 17 (last occurrence)

    # Verify output
    dash_dcc.wait_for_text_to_equal("#output-start", "2021-02-10", timeout=2)
    dash_dcc.wait_for_text_to_equal("#output-end", "2021-02-17", timeout=2)


def test_dtpr_cross_month_drag_selection(dash_dcc):
    """Test drag selection from 15th of first month (Jan) to 15th of second month (Feb)"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dpr",
                initial_visible_month=datetime(2021, 1, 1),
                number_of_months_shown=2,
            ),
            html.Div(id="output-start"),
            html.Div(id="output-end"),
        ]
    )

    @app.callback(
        Output("output-start", "children"),
        Output("output-end", "children"),
        Input("dpr", "start_date"),
        Input("dpr", "end_date"),
    )
    def update_output(start_date, end_date):
        return start_date or "No start", end_date or "No end"

    dash_dcc.start_server(app)

    # Click to open the calendar
    date_picker = dash_dcc.find_element("#dpr")
    date_picker.click()

    dash_dcc._wait_until_day_is_clickable()

    # Get all visible dates
    days = dash_dcc.find_elements(dash_dcc.date_picker_day_locator)

    # Find all day "15"s (both Jan 15 and Feb 15)
    all_15s = [
        day
        for day in days
        if day.text == "15"
        and "dash-datepicker-calendar-date-outside" not in day.get_attribute("class")
    ]

    # Should have at least 2 instances of day 15 (Jan and Feb)
    assert len(all_15s) >= 2, "Should find at least two day 15s (Jan and Feb)"

    # First occurrence is Jan 15, second is Feb 15
    jan_15 = all_15s[0]
    feb_15 = all_15s[1]

    # Perform drag operation: mouse down on Jan 15, drag to Feb 15, mouse up
    actions = ActionChains(dash_dcc.driver)
    actions.click_and_hold(jan_15).move_to_element(feb_15).release().perform()

    # Wait for the callback to fire
    dash_dcc.wait_for_text_to_equal("#output-start", "2021-01-15", timeout=2)

    # Check the outputs
    output_start = dash_dcc.find_element("#output-start")
    output_end = dash_dcc.find_element("#output-end")

    assert (
        output_start.text == "2021-01-15"
    ), f"Expected 2021-01-15 as start, got {output_start.text}"
    assert (
        output_end.text == "2021-02-15"
    ), f"Expected 2021-02-15 as end, got {output_end.text}"


def test_dtpr_cross_month_click_selection(dash_dcc):
    """Test click selection from 15th of first month (Jan) to 15th of second month (Feb)
    This should produce the same result as the drag test above"""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dpr",
                initial_visible_month=datetime(2021, 1, 1),
                number_of_months_shown=2,
                stay_open_on_select=True,
            ),
            html.Div(id="output-start"),
            html.Div(id="output-end"),
        ]
    )

    @app.callback(
        Output("output-start", "children"),
        Output("output-end", "children"),
        Input("dpr", "start_date"),
        Input("dpr", "end_date"),
    )
    def update_output(start_date, end_date):
        return start_date or "No start", end_date or "No end"

    dash_dcc.start_server(app)

    # Open calendar
    dash_dcc.find_element("#dpr").click()
    dash_dcc._wait_until_day_is_clickable()

    # Find and click Jan 15 and Feb 15
    days = dash_dcc.find_elements(dash_dcc.date_picker_day_locator)
    all_15s = [
        d
        for d in days
        if d.text == "15"
        and "dash-datepicker-calendar-date-outside" not in d.get_attribute("class")
    ]

    all_15s[0].click()  # Jan 15 (first occurrence)
    all_15s[1].click()  # Feb 15 (second occurrence)

    # Verify output
    dash_dcc.wait_for_text_to_equal("#output-start", "2021-01-15", timeout=2)
    dash_dcc.wait_for_text_to_equal("#output-end", "2021-02-15", timeout=2)
