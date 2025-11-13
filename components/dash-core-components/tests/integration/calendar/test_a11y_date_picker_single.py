from datetime import datetime
from dash import Dash, Input, Output
from dash.dcc import DatePickerSingle
from dash.html import Div, Label, P
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


def create_date_picker_app(date_picker_props):
    """Create a Dash app with a DatePickerSingle component and output callback"""
    app = Dash(__name__)
    app.layout = Div(
        [DatePickerSingle(id="date-picker", **date_picker_props), Div(id="output-date")]
    )

    @app.callback(Output("output-date", "children"), Input("date-picker", "date"))
    def update_output(date):
        return date or ""

    return app


def open_calendar(dash_dcc, date_picker):
    """Open the calendar and wait for it to be visible"""
    date_picker.click()
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")

    # Send focus onto the calendar
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)


def close_calendar(dash_dcc, driver):
    """Close the calendar with Escape and wait for it to disappear"""
    send_keys(driver, Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container")


def test_a11y001_label_focuses_date_picker(dash_dcc):
    app = Dash(__name__)
    app.layout = Label(
        [
            P("Click me", id="label"),
            DatePickerSingle(
                id="date-picker",
                initial_visible_month=datetime(2021, 1, 1),
            ),
        ],
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#date-picker")

    # Calendar should be closed initially
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=0.25)

    dash_dcc.find_element("#label").click()
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")

    assert dash_dcc.get_logs() == []


def test_a11y002_label_with_htmlFor_can_focus_date_picker(dash_dcc):
    app = Dash(__name__)
    app.layout = Div(
        [
            Label("Click me", htmlFor="date-picker", id="label"),
            DatePickerSingle(
                id="date-picker",
                initial_visible_month=datetime(2021, 1, 1),
            ),
        ],
    )

    dash_dcc.start_server(app)

    dash_dcc.wait_for_element("#date-picker")

    # Calendar should be closed initially
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=0.25)

    dash_dcc.find_element("#label").click()
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")

    assert dash_dcc.get_logs() == []


def test_a11y003_keyboard_navigation_arrows(dash_dcc):
    app = create_date_picker_app(
        {
            "date": "2021-01-15",
            "initial_visible_month": datetime(2021, 1, 1),
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")
    open_calendar(dash_dcc, date_picker)

    # Get the focused date element (should be Jan 15, 2021)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test ArrowRight - should move to Jan 16
    send_keys(dash_dcc.driver, Keys.ARROW_RIGHT)
    assert get_focused_text(dash_dcc.driver) == "16"

    # Test ArrowLeft - should move back to Jan 15
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test ArrowDown - should move to Jan 22 (one week down)
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)
    assert get_focused_text(dash_dcc.driver) == "22"

    # Test ArrowUp - should move back to Jan 15 (one week up)
    send_keys(dash_dcc.driver, Keys.ARROW_UP)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test PageDown - should move to Feb 15 (one month forward)
    send_keys(dash_dcc.driver, Keys.PAGE_DOWN)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test PageUp - should move back to Jan 15 (one month back)
    send_keys(dash_dcc.driver, Keys.PAGE_UP)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test Enter - should select the date and close calendar
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=0.25)

    assert dash_dcc.get_logs() == []


def test_a11y004_keyboard_navigation_home_end(dash_dcc):
    app = create_date_picker_app(
        {
            "date": "2021-01-15",  # Friday, Jan 15, 2021
            "initial_visible_month": datetime(2021, 1, 1),
            "first_day_of_week": 0,  # Sunday
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")
    open_calendar(dash_dcc, date_picker)

    # Get the focused date element (should be Jan 15, 2021 - Friday)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test Home key - should move to week start (Sunday, Jan 10)
    send_keys(dash_dcc.driver, Keys.HOME)
    assert get_focused_text(dash_dcc.driver) == "10"

    # Test End key - should move to week end (Saturday, Jan 16)
    send_keys(dash_dcc.driver, Keys.END)
    assert get_focused_text(dash_dcc.driver) == "16"

    # Test Home key again - should move to week start (Sunday, Jan 10)
    send_keys(dash_dcc.driver, Keys.HOME)
    assert get_focused_text(dash_dcc.driver) == "10"

    assert dash_dcc.get_logs() == []


def test_a11y005_keyboard_navigation_home_end_monday_start(dash_dcc):
    app = create_date_picker_app(
        {
            "date": "2021-01-15",  # Friday, Jan 15, 2021
            "initial_visible_month": datetime(2021, 1, 1),
            "first_day_of_week": 1,  # Monday
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")
    open_calendar(dash_dcc, date_picker)

    # Get the focused date element (should be Jan 15, 2021 - Friday)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Test Home key - should move to week start (Monday, Jan 11)
    send_keys(dash_dcc.driver, Keys.HOME)
    assert get_focused_text(dash_dcc.driver) == "11"

    # Test End key - should move to week end (Sunday, Jan 17)
    send_keys(dash_dcc.driver, Keys.END)
    assert get_focused_text(dash_dcc.driver) == "17"

    assert dash_dcc.get_logs() == []


def test_a11y006_keyboard_navigation_rtl(dash_dcc):
    app = create_date_picker_app(
        {
            "date": "2021-01-15",
            "initial_visible_month": datetime(2021, 1, 1),
            "is_RTL": True,
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")
    open_calendar(dash_dcc, date_picker)

    assert get_focused_text(dash_dcc.driver) == "15"

    # Moves to Jan 14 (reversed)
    send_keys(dash_dcc.driver, Keys.ARROW_RIGHT)
    assert get_focused_text(dash_dcc.driver) == "14"

    # Moves to Jan 15 (reversed)
    send_keys(dash_dcc.driver, Keys.ARROW_LEFT)
    assert get_focused_text(dash_dcc.driver) == "15"

    # Moves to week start
    send_keys(dash_dcc.driver, Keys.HOME)
    assert get_focused_text(dash_dcc.driver) == "10"

    # Moves to week end
    send_keys(dash_dcc.driver, Keys.END)
    assert get_focused_text(dash_dcc.driver) == "16"

    assert dash_dcc.get_logs() == []


def test_a11y007_all_keyboard_keys_respect_min_max(dash_dcc):
    app = create_date_picker_app(
        {
            "date": "2021-02-15",  # Monday
            "min_date_allowed": datetime(2021, 2, 15),  # Monday - same as start date
            "max_date_allowed": datetime(2021, 2, 20),  # Sat
            "initial_visible_month": datetime(2021, 2, 1),
            "first_day_of_week": 0,  # Sunday
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")
    initial_value = "2021-02-15"

    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test Arrow Down (would go to Feb 22, beyond max)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test Arrow Up (would go to Feb 8, before min)
    close_calendar(dash_dcc, dash_dcc.driver)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.ARROW_UP)
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test Home (would go to Feb 14 Sunday, before min Feb 15)
    close_calendar(dash_dcc, dash_dcc.driver)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.HOME)
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test End (would go to Feb 20 Saturday, at max - should succeed)
    close_calendar(dash_dcc, dash_dcc.driver)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.END)
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container")
    dash_dcc.wait_for_text_to_equal("#output-date", "2021-02-20")

    # Reset and test PageUp (would go to Jan 20, before min)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.PAGE_UP)
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#output-date", "2021-02-20")

    # Test PageDown (would go to Mar 20, after max)
    send_keys(dash_dcc.driver, Keys.PAGE_DOWN)
    send_keys(dash_dcc.driver, Keys.ENTER)
    dash_dcc.wait_for_text_to_equal("#output-date", "2021-02-20")

    assert dash_dcc.get_logs() == []


def test_a11y008_all_keyboard_keys_respect_disabled_days(dash_dcc):
    initial_value = "2021-02-15"
    app = create_date_picker_app(
        {
            "date": initial_value,  # Monday
            "disabled_days": [
                datetime(2021, 2, 14),  # Sunday - week start
                datetime(2021, 2, 16),  # Tuesday - ArrowRight target
                datetime(2021, 2, 20),  # Saturday - week end
                datetime(2021, 2, 22),  # Monday - ArrowDown target
                datetime(2021, 1, 15),  # PageUp target
                datetime(2021, 3, 15),  # PageDown target
            ],
            "initial_visible_month": datetime(2021, 2, 1),
            "first_day_of_week": 0,  # Sunday
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")

    # Wait for initial date to be set in output
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test Arrow Right (would go to Feb 16, disabled)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.ARROW_RIGHT)
    send_keys(dash_dcc.driver, Keys.ENTER)
    # Should remain at Feb 15 since Feb 16 is disabled
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test Arrow Down (would go to Feb 22, disabled)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.ARROW_DOWN)
    send_keys(dash_dcc.driver, Keys.ENTER)
    # Should remain at Feb 15 since Feb 22 is disabled
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test Home (would go to Feb 14 Sunday, disabled)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.HOME)
    send_keys(dash_dcc.driver, Keys.ENTER)
    # Should remain at Feb 15 since Feb 14 is disabled
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test End (would go to Feb 20 Saturday, disabled)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.END)
    send_keys(dash_dcc.driver, Keys.ENTER)
    # Should remain at Feb 15 since Feb 20 is disabled
    dash_dcc.wait_for_text_to_equal("#output-date", initial_value)

    # Test PageUp (navigates to previous month, but not a disabled day within that month)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.PAGE_UP)
    send_keys(dash_dcc.driver, Keys.ENTER)
    output_text = dash_dcc.find_element("#output-date").text
    assert output_text != "2021-01-15", "PageUp: Should not select disabled date"

    # Test PageDown (navigates to next month, but not a disabled day within that month)
    open_calendar(dash_dcc, date_picker)
    send_keys(dash_dcc.driver, Keys.PAGE_DOWN)
    send_keys(dash_dcc.driver, Keys.ENTER)
    output_text = dash_dcc.find_element("#output-date").text
    assert output_text != "2021-03-15", "PageDown: Should not select disabled date"

    assert dash_dcc.get_logs() == []


def test_a11y009_keyboard_space_selects_date(dash_dcc):
    app = create_date_picker_app(
        {
            "date": "2021-01-15",
            "initial_visible_month": datetime(2021, 1, 1),
        }
    )
    dash_dcc.start_server(app)

    date_picker = dash_dcc.find_element("#date-picker")
    dash_dcc.wait_for_text_to_equal("#output-date", "2021-01-15")

    open_calendar(dash_dcc, date_picker)

    send_keys(dash_dcc.driver, Keys.ARROW_RIGHT)
    assert get_focused_text(dash_dcc.driver) == "16"

    send_keys(dash_dcc.driver, Keys.SPACE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=0.25)

    dash_dcc.wait_for_text_to_equal("#output-date", "2021-01-16")

    assert dash_dcc.get_logs() == []
