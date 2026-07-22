from datetime import datetime

from dash import Dash, html, dcc, Input, Output
from selenium.webdriver.common.keys import Keys


def test_dtps030_french_localization_via_cdn(dash_dcc):
    """Test that French locale from CDN is applied to date picker."""
    app = Dash(
        __name__,
    )

    app.layout = html.Div(
        [
            html.P("DatePicker localization - translations in assets folder"),
            dcc.DatePickerSingle(
                id="dps",
                date="2025-01-15",
                initial_visible_month=datetime(2025, 1, 1),
                display_format="MMMM DD, YYYY",
                month_format="MMMM YYYY",
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

    # Wait for date picker to render
    input_element = dash_dcc.wait_for_element("#dps")

    # Check initial callback output shows ISO format date
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2025-01-15")

    # Check that display format uses French month name
    display_value = input_element.get_attribute("value")
    assert (
        "janvier" in display_value.lower()
    ), f"Display format should use French month name 'janvier', but got: {display_value}"

    # Test typing a French month name in the input
    input_element.clear()
    input_element.send_keys("février 20, 2025")
    input_element.send_keys(Keys.TAB)  # Blur to trigger parsing

    # Wait for the date to be parsed and formatted
    dash_dcc.wait_for_text_to_equal("#dps", "février 20, 2025")

    # Verify the input now shows the French formatted date
    display_value = input_element.get_attribute("value")
    assert (
        "février" in display_value.lower()
    ), f"Input should accept and display French month name 'février', but got: {display_value}"

    # Verify the callback received the correct ISO format date (locale-independent)
    dash_dcc.wait_for_text_to_equal("#output", "Date: 2025-02-20")

    # Open the calendar
    input_element.click()
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")

    # Check that days of the week are in French
    # French abbreviated days: Lu, Ma, Me, Je, Ve, Sa, Di
    day_headers = dash_dcc.find_elements(".dash-datepicker-calendar thead th span")
    day_texts = [header.text for header in day_headers]

    # Check for French day abbreviations (2-letter format)
    french_days = ["lu", "ma", "me", "je", "ve", "sa", "di"]
    assert (
        len(day_texts) == 7
    ), f"Should have 7 day headers, but got {len(day_texts)}: {day_texts}"

    for day_text in day_texts:
        assert any(
            french_day in day_text.lower() for french_day in french_days
        ), f"Day header '{day_text}' should be a French day abbreviation, expected one of: {french_days}"

    assert dash_dcc.get_logs() == []
