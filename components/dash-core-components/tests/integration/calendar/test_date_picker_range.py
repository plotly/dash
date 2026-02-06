from datetime import datetime
import time

from dash import Dash, Input, Output, html, dcc
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.common.keys import Keys


def test_dtpr001_initial_month_provided(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
                initial_visible_month=datetime(2019, 10, 28),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()

    dash_dcc.wait_for_text_to_equal(
        ".dash-datepicker .dash-dropdown-value",
        "October",
        1,
    )

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert year_input.get_attribute("value") == "2019"

    assert dash_dcc.get_logs() == []


def test_dtpr002_no_initial_month_min_date(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()

    dash_dcc.wait_for_text_to_equal(
        ".dash-datepicker .dash-dropdown-value",
        "January",
        1,
    )

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert year_input.get_attribute("value") == "2010"

    assert dash_dcc.get_logs() == []


def test_dtpr003_no_initial_month_no_min_date_start_date(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                start_date=datetime(2019, 8, 13),
                max_date_allowed=datetime(2099, 12, 31),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dps-initial-month")
    date_picker.click()

    dash_dcc.wait_for_text_to_equal(
        ".dash-datepicker .dash-dropdown-value",
        "August",
        1,
    )

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert year_input.get_attribute("value") == "2019"

    assert dash_dcc.get_logs() == []


def test_dtpr004_max_and_min_dates_are_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dps-initial-month",
                display_format="MM/DD/YYYY",
                start_date=datetime(2021, 1, 11),
                end_date=datetime(2021, 1, 19),
                max_date_allowed=datetime(2021, 1, 20),
                min_date_allowed=datetime(2021, 1, 10),
            )
        ]
    )

    dash_dcc.start_server(app)

    dash_dcc.select_date_range("dps-initial-month", (10, 20))

    start_date = dash_dcc.find_element(".dash-datepicker-start-date")
    assert start_date.get_attribute("value") == "01/10/2021"

    end_date = dash_dcc.find_element(".dash-datepicker-end-date")
    assert end_date.get_attribute("value") == "01/20/2021"

    assert dash_dcc.get_logs() == []


def test_dtpr005_disabled_days_arent_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerRange(
                id="dpr",
                min_date_allowed=datetime(2021, 1, 1),
                max_date_allowed=datetime(2021, 1, 31),
                initial_visible_month=datetime(2021, 1, 1),
                disabled_days=[datetime(2021, 1, 10), datetime(2021, 1, 11)],
            ),
        ],
        style={"width": "50%"},
    )
    dash_dcc.start_server(app)
    date = dash_dcc.find_element("#dpr")
    assert not date.get_attribute("value")

    # Try to click disabled days
    date.click()
    try:
        dash_dcc.select_date_range("dpr", day_range=(10, 11))
        date.click()
    except (ElementClickInterceptedException, TimeoutException):
        pass  # Expected - dates are disabled with pointer-events: none

    assert all(
        dash_dcc.select_date_range("dpr", day_range=(1, 2))
    ), "Other days should be clickable"

    # open datepicker to take snapshot
    date.click()
    dash_dcc.percy_snapshot("dtpr005 - disabled days")


def test_dtpr006_minimum_nights_forward_selection(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Booking Date"),
            dcc.DatePickerRange(
                id="dpr-min-nights",
                min_date_allowed=datetime(2021, 1, 1),
                max_date_allowed=datetime(2021, 1, 31),
                initial_visible_month=datetime(2021, 1, 1),
                minimum_nights=3,
                display_format="MM/DD/YYYY",
            ),
        ],
        style={"width": "50%"},
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dpr-min-nights")

    # Try to select dates that violate minimum_nights (Jan 10 -> Jan 11)
    # This should fail because minimum_nights=3 requires at least 3 days between
    date_picker.click()
    try:
        dash_dcc.select_date_range("dpr-min-nights", day_range=(10, 11))
        date_picker.click()
    except (ElementClickInterceptedException, TimeoutException):
        pass  # Expected - day 11 is disabled with pointer-events: none

    # Try another invalid range (Jan 10 -> Jan 12)
    date_picker.click()
    try:
        dash_dcc.select_date_range("dpr-min-nights", day_range=(10, 12))
        date_picker.click()
    except (ElementClickInterceptedException, TimeoutException):
        pass  # Expected - day 12 is also disabled

    # Now select a valid range that respects minimum_nights (Jan 10 -> Jan 13)
    # This should succeed because there are 3 days between them
    result = dash_dcc.select_date_range("dpr-min-nights", day_range=(10, 13))
    assert result == ("01/10/2021", "01/13/2021")

    assert dash_dcc.get_logs() == []


def test_dtpr007_minimum_nights_backward_selection(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Booking Date"),
            dcc.DatePickerRange(
                id="dpr-min-nights-backward",
                min_date_allowed=datetime(2021, 1, 1),
                max_date_allowed=datetime(2021, 1, 31),
                initial_visible_month=datetime(2021, 1, 1),
                minimum_nights=2,
                display_format="MM/DD/YYYY",
            ),
        ],
        style={"width": "50%"},
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dpr-min-nights-backward")

    # Try to select dates that violate minimum_nights backward (Jan 15 -> Jan 14)
    date_picker.click()
    try:
        dash_dcc.select_date_range("dpr-min-nights-backward", day_range=(15, 14))
        date_picker.click()
    except (ElementClickInterceptedException, TimeoutException):
        pass  # Expected - day 14 is disabled with pointer-events: none

    # Now select a valid backward range that respects minimum_nights (Jan 15 -> Jan 13)
    # This should succeed because there are 2 days between them
    # When clicking 15 then 13, the component normalizes to start=13, end=15
    result = dash_dcc.select_date_range("dpr-min-nights-backward", day_range=(15, 13))
    assert result == ("01/13/2021", "01/15/2021")

    assert dash_dcc.get_logs() == []


def test_dtpr008_input_click_opens_but_keeps_focus(dash_dcc):
    """Test that clicking either input opens the calendar but doesn't close it and maintains focus."""
    import time

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerRange(
                id="dpr",
                start_date="2025-01-10",
                end_date="2025-01-15",
                display_format="MM/DD/YYYY",
            ),
        ]
    )

    dash_dcc.start_server(app)

    start_input = dash_dcc.find_element(".dash-datepicker-start-date")
    end_input = dash_dcc.find_element(".dash-datepicker-end-date")

    # Initially, calendar should be closed
    assert not dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should be closed initially"

    # Click on the start input
    start_input.click()

    # Calendar should now be open
    dash_dcc.wait_for_element(".dash-datepicker-calendar")
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should open after clicking start input"

    # Start input should still have focus
    active_element = dash_dcc.driver.switch_to.active_element
    assert "dash-datepicker-start-date" in active_element.get_attribute(
        "class"
    ), "Start input should maintain focus"

    # Click on the end input (switching between inputs)
    end_input.click()

    # Calendar should STILL be open
    time.sleep(0.2)  # Give it a moment to potentially close
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open when clicking end input"

    # End input should now have focus
    active_element = dash_dcc.driver.switch_to.active_element
    assert "dash-datepicker-end-date" in active_element.get_attribute(
        "class"
    ), "End input should have focus after clicking it"

    # Click on the end input again
    end_input.click()

    # Calendar should STILL be open (not toggled closed)
    time.sleep(0.2)
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open after clicking end input again"

    # User should be able to type in end input without popup closing
    # Type a date in a different month/year (August 2026)
    # Select all text using keyboard (cross-platform approach)
    end_input.send_keys(Keys.HOME)
    end_input.send_keys(Keys.SHIFT + Keys.END)
    end_input.send_keys("08/20/2026")

    # Calendar should still be open
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open while typing in end input"

    # Press Tab to blur and trigger date parsing
    end_input.send_keys(Keys.TAB)
    time.sleep(0.3)  # Give calendar time to update

    # Calendar should still be open after blur
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open after blur"

    # Verify the input value was parsed correctly
    assert (
        end_input.get_attribute("value") == "08/20/2026"
    ), f"End input should show 08/20/2026, but shows: {end_input.get_attribute('value')}"

    # Calendar should now show August 2026
    month_dropdown = dash_dcc.find_element(".dash-datepicker .dash-dropdown-value")
    assert (
        month_dropdown.text == "August"
    ), f"Calendar should show August, but shows: {month_dropdown.text}"

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert (
        year_input.get_attribute("value") == "2026"
    ), f"Calendar should show 2026, but shows: {year_input.get_attribute('value')}"

    # Click on start input and type a date in yet another month (March 2026)
    start_input.click()
    # Select all text using keyboard (cross-platform approach)
    start_input.send_keys(Keys.HOME)
    start_input.send_keys(Keys.SHIFT + Keys.END + Keys.DELETE)
    start_input.send_keys("03/05/2026")
    start_input.send_keys(Keys.ARROW_DOWN)
    time.sleep(0.3)

    # Calendar should still be open and now show March 2026
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open while typing in start input"

    # Verify the input value was parsed correctly
    assert (
        start_input.get_attribute("value") == "03/05/2026"
    ), f"Start input should show 03/05/2026, but shows: {start_input.get_attribute('value')}"

    month_dropdown = dash_dcc.find_element(".dash-datepicker .dash-dropdown-value")
    assert (
        month_dropdown.text == "March"
    ), f"Calendar should show March, but shows: {month_dropdown.text}"

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert (
        year_input.get_attribute("value") == "2026"
    ), f"Calendar should show 2026, but shows: {year_input.get_attribute('value')}"

    assert dash_dcc.get_logs() == []


def test_dtpr030_external_date_range_update(dash_dcc):
    """Test that DatePickerRange accepts external date updates via callback without resetting."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Update dates", id="update-btn"),
            dcc.DatePickerRange(
                id="dpr",
                start_date="2024-01-01",
                end_date="2024-12-31",
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("dpr", "start_date"),
        Output("dpr", "end_date"),
        Input("update-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_dates(n_clicks):
        return "2021-06-01", "2021-06-30"

    @app.callback(
        Output("output", "children"),
        Input("dpr", "start_date"),
        Input("dpr", "end_date"),
    )
    def display_dates(start_date, end_date):
        return f"Start: {start_date}, End: {end_date}"

    dash_dcc.start_server(app)

    # Verify initial dates
    dash_dcc.wait_for_text_to_equal("#output", "Start: 2024-01-01, End: 2024-12-31")
    start_input = dash_dcc.find_element(".dash-datepicker-start-date")
    end_input = dash_dcc.find_element(".dash-datepicker-end-date")
    assert start_input.get_attribute("value") == "2024-01-01"
    assert end_input.get_attribute("value") == "2024-12-31"

    # Click button to trigger external update
    btn = dash_dcc.find_element("#update-btn")
    btn.click()

    # Verify dates were updated and stay updated (don't reset back)
    dash_dcc.wait_for_text_to_equal(
        "#output", "Start: 2021-06-01, End: 2021-06-30", timeout=4
    )

    # Give it a moment to potentially incorrectly reset
    time.sleep(0.5)

    # Verify they're still the new dates
    assert (
        dash_dcc.find_element("#output").text == "Start: 2021-06-01, End: 2021-06-30"
    ), "Dates should remain updated after external update"
    assert (
        start_input.get_attribute("value") == "2021-06-01"
    ), "Start input should display 2021-06-01"
    assert (
        end_input.get_attribute("value") == "2021-06-30"
    ), "End input should display 2021-06-30"

    assert dash_dcc.get_logs() == []
