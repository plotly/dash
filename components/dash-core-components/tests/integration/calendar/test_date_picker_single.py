from datetime import datetime, timedelta
import pandas as pd
import time

import pytest
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException

from dash import Dash, Input, Output, html, dcc, no_update


@pytest.mark.DCC652
def test_dtps001_simple_click(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=datetime(2010, 1, 1),
                max_date_allowed=datetime(2099, 12, 31),
                initial_visible_month=datetime.today().date() - timedelta(days=1),
                day_size=47,
            ),
        ],
        style={
            "width": "50%",
        },
    )
    dash_dcc.start_server(app)
    date = dash_dcc.find_element("#dps")
    assert not date.get_attribute("value")
    assert dash_dcc.select_date_single(
        "dps", index=3
    ), "Component should be clickable to choose a valid date"

    assert dash_dcc.get_logs() == []


def test_dtps010_local_and_session_persistence(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(id="dps-local", persistence=True, day_size=47),
            dcc.DatePickerSingle(
                id="dps-session",
                persistence=True,
                persistence_type="session",
                day_size=47,
            ),
        ]
    )

    dash_dcc.start_server(app)

    assert not dash_dcc.find_element("#dps-local").get_attribute(
        "value"
    ) and not dash_dcc.find_element("#dps-session").get_attribute(
        "value"
    ), "component should contain no initial date"

    for idx in range(3):
        local = dash_dcc.select_date_single("dps-local", day=idx)
        session = dash_dcc.select_date_single("dps-session", day=idx)
        dash_dcc.wait_for_page()
        time.sleep(0.5)
        assert dash_dcc.find_element("#dps-local").get_attribute("value") == local
        assert dash_dcc.find_element("#dps-session").get_attribute("value") == session

    assert dash_dcc.get_logs() == []


def test_dtps011_memory_persistence(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Button(id="switch", children="Switch"), html.Div(id="out")]
    )

    @app.callback(Output("out", "children"), [Input("switch", "n_clicks")])
    def cb(clicks):
        if clicks is None:
            return no_update
        if clicks % 2 == 1:
            return [
                dcc.DatePickerSingle(
                    id="dps-memory",
                    min_date_allowed=datetime(2010, 1, 1),
                    max_date_allowed=datetime(2099, 12, 31),
                    initial_visible_month=datetime.today().date() - timedelta(days=1),
                    persistence=True,
                    persistence_type="memory",
                    day_size=47,
                ),
                dcc.DatePickerSingle(
                    id="dps-none",
                    min_date_allowed=datetime(2010, 1, 1),
                    max_date_allowed=datetime(2099, 12, 31),
                    initial_visible_month=datetime.today().date() - timedelta(days=1),
                    day_size=47,
                ),
            ]
        else:
            return "switched"

    dash_dcc.start_server(app)

    switch = dash_dcc.find_element("#switch")
    switch.click()

    memorized = dash_dcc.select_date_single("dps-memory", day="4")
    amnesiaed = dash_dcc.select_date_single("dps-none", day="11")

    switch.click()
    assert dash_dcc.wait_for_text_to_equal("#out", "switched")
    switch.click()
    assert dash_dcc.find_element("#dps-memory").get_attribute("value") == memorized
    switched = dash_dcc.find_element("#dps-none").get_attribute("value")
    assert switched != amnesiaed and switched == ""

    assert dash_dcc.get_logs() == []


def test_dtps012_initial_visible_month(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                date="2020-06-15",
                initial_visible_month=datetime(2010, 1, 1),
            )
        ]
    )

    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#dps")
    date_picker.click()

    # Wait for calendar to open
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")

    # Check that calendar shows January 2010 (initial_visible_month), not June 2020 (date)
    month_dropdown = dash_dcc.find_element(".dash-datepicker-controls .dash-dropdown")
    year_input = dash_dcc.find_element(".dash-datepicker-controls input")

    assert "January" in month_dropdown.text, "Calendar should show January"
    assert year_input.get_attribute("value") == "2010", "Calendar should show year 2010"

    assert dash_dcc.get_logs() == []


def test_dtps013_min_max_date_allowed(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=datetime(2021, 1, 5),
                max_date_allowed=datetime(2021, 1, 25),
                initial_visible_month=datetime(2021, 1, 1),
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("dps", "date"),
    )
    def update_output(date):
        return f"Selected: {date}"

    dash_dcc.start_server(app)

    # Initially no date selected
    dash_dcc.wait_for_text_to_equal("#output", "Selected: None")

    # Try to select date before min_date_allowed - should not update
    try:
        dash_dcc.select_date_single("dps", day=3)
    except ElementClickInterceptedException:
        pass  # Expected - date is disabled with pointer-events: none
    dash_dcc.wait_for_text_to_equal("#output", "Selected: None")
    # Close calendar
    date_input = dash_dcc.find_element("#dps")
    date_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    # Try to select date after max_date_allowed - should not update
    try:
        dash_dcc.select_date_single("dps", day=28)
    except ElementClickInterceptedException:
        pass  # Expected - date is disabled with pointer-events: none
    dash_dcc.wait_for_text_to_equal("#output", "Selected: None")
    # Close calendar
    date_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    # Select date within allowed range - should update
    dash_dcc.select_date_single("dps", day=10)
    dash_dcc.wait_for_text_to_equal("#output", "Selected: 2021-01-10")

    assert dash_dcc.get_logs() == []


def test_dtps014_disabled_days_arent_clickable(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=datetime(2021, 1, 1),
                max_date_allowed=datetime(2021, 1, 31),
                initial_visible_month=datetime(2021, 1, 1),
                disabled_days=[datetime(2021, 1, 10)],
            ),
        ],
        style={"width": "50%"},
    )
    dash_dcc.start_server(app)
    date = dash_dcc.find_element("#dps")
    assert not date.get_attribute("value")

    # Try to click disabled day - should fail or be intercepted
    # (Selenium may throw ElementClickInterceptedException due to pointer-events: none)
    try:
        result = dash_dcc.select_date_single("dps", day=10)
        assert not result, "Disabled days should not be clickable"
    except ElementClickInterceptedException:
        pass  # Expected - date is disabled with pointer-events: none

    # Verify date wasn't selected
    assert not date.get_attribute("value")

    # Close calendar
    date.send_keys(Keys.ESCAPE)
    assert dash_dcc.select_date_single("dps", day=1), "Other days should be clickable"

    # open datepicker to take snapshot
    date.click()
    dash_dcc.percy_snapshot("dtps014 - disabled days")


def test_dtps0014_disabed_days_timeout(dash_dcc):
    app = Dash(__name__)

    min_date = pd.to_datetime("2010-01-01")
    max_date = pd.to_datetime("2099-01-01")
    disabled_days = [
        x for x in pd.date_range(min_date, max_date, freq="D") if x.day != 1
    ]

    app.layout = html.Div(
        [
            html.Label("Operating Date"),
            dcc.DatePickerSingle(
                id="dps",
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                disabled_days=disabled_days,
            ),
        ]
    )
    dash_dcc.start_server(app)
    date = dash_dcc.wait_for_element("#dps", timeout=5)

    """
    WebDriver click() function hangs at the time of the react code
    execution, so it necessary to check execution time.
    """
    start_time = time.time()
    date.click()
    assert time.time() - start_time < 5

    dash_dcc.wait_for_element(".dash-datepicker-calendar-container", timeout=5)
    assert dash_dcc.get_logs() == []


def test_dtps020_renders_date_picker(dash_dcc):
    """Test that DatePickerSingle renders correctly."""
    app = Dash(__name__)
    app.layout = html.Div([dcc.DatePickerSingle(id="dps")])

    dash_dcc.start_server(app)

    # Check that the datepicker element exists
    datepicker = dash_dcc.find_element(".dash-datepicker")
    assert datepicker is not None, "DatePickerSingle should render"

    # Check that input exists
    input_element = dash_dcc.find_element(".dash-datepicker-input")
    assert input_element is not None, "DatePickerSingle should have an input element"

    assert dash_dcc.get_logs() == []


def test_dtps022_custom_display_format(dash_dcc):
    """Test that dates display in custom format."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                display_format="MM/DD/YYYY",
                date="2025-10-17",
            ),
        ]
    )

    dash_dcc.start_server(app)

    # Check that input shows the date in custom format
    input_element = dash_dcc.find_element(".dash-datepicker-input")
    assert (
        input_element.get_attribute("value") == "10/17/2025"
    ), "Date should display in MM/DD/YYYY format"

    assert dash_dcc.get_logs() == []


def test_dtps023_default_display_format(dash_dcc):
    """Test that dates default to YYYY-MM-DD format and can be changed via callback."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Change Format", id="btn"),
            dcc.DatePickerSingle(
                id="dps",
                date="2025-01-10",
            ),
        ]
    )

    @app.callback(
        Output("dps", "display_format"),
        Input("btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def change_format(n_clicks):
        return "DD/MM/YYYY"

    dash_dcc.start_server(app)

    # Check that input shows the date in default YYYY-MM-DD format
    input_element = dash_dcc.find_element(".dash-datepicker-input")
    assert (
        input_element.get_attribute("value") == "2025-01-10"
    ), "Date should display in default YYYY-MM-DD format"

    # Click button to change format
    btn = dash_dcc.find_element("#btn")
    btn.click()

    # Wait for format to change and verify new format
    dash_dcc.wait_for_text_to_equal(".dash-datepicker-input", "10/01/2025", timeout=4)

    assert dash_dcc.get_logs() == []


def test_dtps023b_input_validation_and_blur(dash_dcc):
    """Test that typing into the input and blurring validates and reformats the date."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                display_format="MM/DD/YYYY",
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("dps", "date"),
    )
    def update_output(date):
        return f"Date: {date}"

    dash_dcc.start_server(app)

    # Initially no date
    dash_dcc.wait_for_text_to_equal("#output", "Date: None")

    input_element = dash_dcc.find_element("#dps")

    # Type a valid date in the custom format
    input_element.clear()
    input_element.send_keys("01/15/2025")
    input_element.send_keys(Keys.TAB)  # Blur the input

    # Should parse and set the date
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2025-01-15")

    # Input should still show in custom format after blur
    assert (
        input_element.get_attribute("value") == "01/15/2025"
    ), "Input should maintain custom format after blur"

    # Type an invalid date
    input_element.clear()
    input_element.send_keys("invalid")
    input_element.send_keys(Keys.TAB)  # Blur the input

    # Should revert to previous valid date
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2025-01-15")
    assert (
        input_element.get_attribute("value") == "01/15/2025"
    ), "Invalid input should revert to previous valid date in display format on blur"

    assert dash_dcc.get_logs() == []


def test_dtps024_rtl_directionality(dash_dcc):
    """Test that is_RTL prop applies correct directionality to input and calendar."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(id="dps-rtl", is_RTL=True),
            dcc.DatePickerSingle(id="dps-ltr", is_RTL=False),
            dcc.DatePickerSingle(id="dps-default"),
        ]
    )

    dash_dcc.start_server(app)

    # Wait for components to render and check dir attribute on input elements
    rtl_input = dash_dcc.wait_for_element(".dash-datepicker-input")
    assert (
        rtl_input.get_attribute("dir") == "rtl"
    ), "is_RTL=True should set dir='rtl' on input element"

    all_inputs = dash_dcc.find_elements(".dash-datepicker-input")
    assert len(all_inputs) == 3, "Should have 3 date picker inputs"

    ltr_input = all_inputs[1]
    assert (
        ltr_input.get_attribute("dir") == "ltr"
    ), "is_RTL=False should set dir='ltr' on input element"

    default_input = all_inputs[2]
    assert (
        default_input.get_attribute("dir") == "ltr"
    ), "Default (no is_RTL) should set dir='ltr' on input element"

    # Test calendar directionality when opened
    all_wrappers = dash_dcc.find_elements(".dash-datepicker-input-wrapper")
    all_wrappers[0].click()

    rtl_calendar = dash_dcc.wait_for_element(".dash-datepicker-calendar-container")
    assert (
        rtl_calendar.get_attribute("dir") == "rtl"
    ), "is_RTL=True should set dir='rtl' on calendar container"

    rtl_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    all_wrappers[1].click()
    ltr_calendar = dash_dcc.wait_for_element(".dash-datepicker-calendar-container")
    assert (
        ltr_calendar.get_attribute("dir") == "ltr"
    ), "is_RTL=False should set dir='ltr' on calendar container"

    ltr_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    all_wrappers[2].click()
    default_calendar = dash_dcc.wait_for_element(".dash-datepicker-calendar-container")
    assert (
        default_calendar.get_attribute("dir") == "ltr"
    ), "Default (no is_RTL) should set dir='ltr' on calendar container"

    assert dash_dcc.get_logs() == []


def test_dtps025_typing_disabled_day_should_not_trigger_callback(dash_dcc):
    """Test that manually typing a disabled day into the input does not set that date in callback."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                date="2025-01-10",
                display_format="MM/DD/YYYY",
                disabled_days=[datetime(2025, 1, 15)],
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("dps", "date"),
    )
    def update_output(date):
        return f"Date: {date}"

    dash_dcc.start_server(app)

    # Initially has a valid date
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2025-01-10")

    input_element = dash_dcc.find_element("#dps")

    # Verify initial display format is respected
    assert (
        input_element.get_attribute("value") == "01/10/2025"
    ), "Initial date should be displayed in custom format"

    # Type a disabled date (in the correct display format)
    input_element.clear()
    input_element.send_keys("01/15/2025")
    input_element.send_keys(Keys.TAB)  # Blur the input

    # The callback should NOT receive the disabled date
    time.sleep(0.5)  # Give it time to potentially (incorrectly) update
    output_text = dash_dcc.find_element("#output").text
    assert (
        output_text != "Date: 2025-01-15"
    ), f"Typing a disabled day should not trigger callback with that date, but got: {output_text}"

    # The input should revert to the previous valid date in the correct display format
    assert (
        input_element.get_attribute("value") == "01/10/2025"
    ), f"Input should revert to previous valid date in display format (MM/DD/YYYY), but got: {input_element.get_attribute('value')}"

    assert dash_dcc.get_logs() == []


def test_dtps026_input_click_opens_but_keeps_focus(dash_dcc):
    """Test that clicking the input opens the calendar but doesn't close it and maintains focus."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps",
                date="2025-01-10",
                display_format="MM/DD/YYYY",
            ),
        ]
    )

    dash_dcc.start_server(app)

    input_element = dash_dcc.find_element("#dps")

    # Initially, calendar should be closed
    assert not dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should be closed initially"

    # Click on the input
    input_element.click()

    # Calendar should now be open
    dash_dcc.wait_for_element(".dash-datepicker-calendar")
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should open after clicking input"

    # Input should still have focus (user should be able to type)
    active_element = dash_dcc.driver.switch_to.active_element
    assert (
        active_element.get_attribute("id") == "dps"
    ), "Input should maintain focus after opening calendar"

    # Click on the input again
    input_element.click()

    # Calendar should STILL be open (not toggled closed)
    time.sleep(0.2)  # Give it a moment to potentially close
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open after clicking input again"

    # Input should still have focus
    active_element = dash_dcc.driver.switch_to.active_element
    assert (
        active_element.get_attribute("id") == "dps"
    ), "Input should maintain focus after second click"

    # User should be able to type without popup closing
    # Type a date in a different month/year (June 2026)
    # Select all text using keyboard (cross-platform approach)
    input_element.send_keys(Keys.HOME)
    input_element.send_keys(Keys.SHIFT + Keys.END)
    input_element.send_keys("06/15/2026")

    # Calendar should still be open
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open while typing"

    # Press Tab to blur the input and trigger date parsing
    input_element.send_keys(Keys.TAB)
    time.sleep(0.3)  # Give calendar time to update

    # Calendar should still be open after blur
    assert dash_dcc.find_elements(
        ".dash-datepicker-calendar"
    ), "Calendar should remain open after blur"

    # Verify the input value was parsed correctly
    assert (
        input_element.get_attribute("value") == "06/15/2026"
    ), f"Input should show 06/15/2026, but shows: {input_element.get_attribute('value')}"

    # Calendar should now show June 2026
    month_dropdown = dash_dcc.find_element(".dash-datepicker .dash-dropdown-value")
    assert (
        month_dropdown.text == "June"
    ), f"Calendar should show June, but shows: {month_dropdown.text}"

    year_input = dash_dcc.find_element(".dash-datepicker .dash-input-container input")
    assert (
        year_input.get_attribute("value") == "2026"
    ), f"Calendar should show 2026, but shows: {year_input.get_attribute('value')}"

    assert dash_dcc.get_logs() == []


def test_dtps030_external_date_update(dash_dcc):
    """Test that DatePickerSingle accepts external date updates via callback without resetting."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button("Update to 2021-06-23", id="update-btn"),
            dcc.DatePickerSingle(
                id="dps",
                date="2024-11-25",
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(
        Output("dps", "date"),
        Input("update-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def update_date(n_clicks):
        return "2021-06-23"

    @app.callback(
        Output("output", "children"),
        Input("dps", "date"),
    )
    def display_date(date):
        return f"Date: {date}"

    dash_dcc.start_server(app)

    # Verify initial date
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2024-11-25")
    input_element = dash_dcc.find_element(".dash-datepicker-input")
    assert input_element.get_attribute("value") == "2024-11-25"

    # Click button to trigger external update
    btn = dash_dcc.find_element("#update-btn")
    btn.click()

    # Verify date was updated and stays updated (doesn't reset back)
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2021-06-23", timeout=4)

    # Give it a moment to potentially incorrectly reset
    time.sleep(0.5)

    # Verify it's still the new date
    assert (
        dash_dcc.find_element("#output").text == "Date: 2021-06-23"
    ), "Date should remain 2021-06-23 after external update"
    assert (
        input_element.get_attribute("value") == "2021-06-23"
    ), "Input should display 2021-06-23"

    assert dash_dcc.get_logs() == []
