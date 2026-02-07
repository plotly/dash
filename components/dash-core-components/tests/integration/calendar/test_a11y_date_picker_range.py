from datetime import datetime
from dash import Dash, Input, Output
from dash.dcc import DatePickerRange
from dash.html import Div
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def send_keys(driver, key):
    """Send keyboard keys to the browser"""
    actions = ActionChains(driver)
    actions.send_keys(key)
    actions.perform()


def get_focused_text(driver):
    """Get the text content of the currently focused element"""
    return driver.execute_script("return document.activeElement.textContent;")


def test_a11y_range_001_keyboard_range_selection_with_highlights(dash_dcc):
    """Test keyboard-based range selection with highlight verification"""
    app = Dash(__name__)
    app.layout = Div(
        [
            DatePickerRange(
                id="date-picker-range",
                initial_visible_month=datetime(2021, 1, 1),
            ),
            Div(id="output-dates"),
        ]
    )

    @app.callback(
        Output("output-dates", "children"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_output(start_date, end_date):
        if start_date and end_date:
            return f"{start_date} to {end_date}"
        elif start_date:
            return f"Start: {start_date}"
        return ""

    dash_dcc.start_server(app)

    # Find the first input field and open calendar with keyboard
    date_picker_input = dash_dcc.find_element(".dash-datepicker-input")
    date_picker_input.send_keys(Keys.ARROW_DOWN)
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")
    # Wait for focus to be applied
    import time

    time.sleep(0.1)

    # Calendar opens with Jan 1 focused (first day of month since no dates selected)
    # Navigate: Arrow Down (Jan 1 -> 8)
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)

    # Verify focused date is Jan 8
    assert get_focused_text(dash_dcc.driver) == "8"

    # Press Space to select the first date (Jan 8)
    send_keys(dash_dcc.driver, Keys.SPACE)

    # Verify first date was selected (only start_date, no end_date yet)
    dash_dcc.wait_for_text_to_equal("#output-dates", "Start: 2021-01-08")

    # Navigate to another date: Arrow Down (1 week) + Arrow Right (1 day)
    # Jan 8 -> Jan 15 -> Jan 16
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)
    send_keys(dash_dcc.driver, Keys.ARROW_RIGHT)

    # Verify focused date is Jan 16
    assert get_focused_text(dash_dcc.driver) == "16"

    # Verify that days between Jan 8 and Jan 16 are highlighted
    # The highlighted dates should have the class 'dash-datepicker-calendar-date-highlighted'
    highlighted_dates = dash_dcc.driver.find_elements(
        "css selector", ".dash-datepicker-calendar-date-highlighted"
    )
    # Should have 9 highlighted dates (Jan 8 through Jan 16 inclusive)
    assert (
        len(highlighted_dates) == 9
    ), f"Expected 9 highlighted dates, got {len(highlighted_dates)}"

    # Press Enter to select the second date
    send_keys(dash_dcc.driver, Keys.ENTER)

    # Calendar should close
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=0.25)

    # Verify both dates were selected in the output
    dash_dcc.wait_for_text_to_equal("#output-dates", "2021-01-08 to 2021-01-16")

    assert dash_dcc.get_logs() == []


def test_a11y_range_002_keyboard_update_existing_range(dash_dcc):
    """Test keyboard-based updating of an existing date range"""
    app = Dash(__name__)
    app.layout = Div(
        [
            DatePickerRange(
                id="date-picker-range",
                start_date="2021-01-10",
                end_date="2021-01-20",
                initial_visible_month=datetime(2021, 1, 1),
            ),
            Div(id="output-dates"),
        ]
    )

    @app.callback(
        Output("output-dates", "children"),
        Input("date-picker-range", "start_date"),
        Input("date-picker-range", "end_date"),
    )
    def update_output(start_date, end_date):
        if start_date and end_date:
            return f"{start_date} to {end_date}"
        elif start_date:
            return f"Start: {start_date}"
        return ""

    dash_dcc.start_server(app)

    # Verify initial range is displayed
    dash_dcc.wait_for_text_to_equal("#output-dates", "2021-01-10 to 2021-01-20")

    # Find the first input field and open calendar with keyboard
    date_picker_input = dash_dcc.find_element(".dash-datepicker-input")
    date_picker_input.send_keys(Keys.ARROW_DOWN)
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")
    # Wait for focus to be applied
    import time

    time.sleep(0.1)

    # Calendar opens with Jan 10 focused (the current start date)
    # Navigate: Arrow Down (Jan 10 -> 17), then 5x Arrow Left (17 -> 16 -> 15 -> 14 -> 13 -> 12)
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)

    # Verify focused date is Jan 12
    assert get_focused_text(dash_dcc.driver) == "12"

    # Press Space to start a NEW range selection with Jan 12 as start_date
    # This should clear end_date and set only start_date
    send_keys(dash_dcc.driver, Keys.SPACE)

    # Verify new start date was selected (only start_date, no end_date)
    dash_dcc.wait_for_text_to_equal("#output-dates", "2021-01-12 to 2021-01-20")

    # Navigate to new end date: Arrow Down + Arrow Right (Jan 12 -> 19 -> 20)
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)
    send_keys(dash_dcc.driver, Keys.ARROW_RIGHT)

    # Verify focused date is Jan 20
    assert get_focused_text(dash_dcc.driver) == "20"

    # Verify that days between Jan 12 and Jan 20 are highlighted
    highlighted_dates = dash_dcc.driver.find_elements(
        "css selector", ".dash-datepicker-calendar-date-highlighted"
    )
    # Should have 9 highlighted dates (Jan 12 through 20 inclusive)
    assert (
        len(highlighted_dates) == 9
    ), f"Expected 9 highlighted dates, got {len(highlighted_dates)}"

    # Press Enter to select the new end date
    send_keys(dash_dcc.driver, Keys.ENTER)

    # Calendar should close
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=0.25)

    # Verify both dates were updated in the output
    dash_dcc.wait_for_text_to_equal("#output-dates", "2021-01-12 to 2021-01-20")

    assert dash_dcc.get_logs() == []
