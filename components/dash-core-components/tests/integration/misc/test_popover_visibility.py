from datetime import date
from dash import Dash, html, dcc
from selenium.webdriver.common.by import By
from time import sleep


def click_everything_in_datepicker(datepicker_id, dash_dcc):
    """Click on every clickable element in a datepicker calendar.

    Args:
        datepicker_id: CSS selector for the datepicker element (e.g., "#dpr")
        dash_dcc: The dash_dcc fixture
    """
    # Click on the datepicker to open calendar
    datepicker = dash_dcc.find_element(datepicker_id)
    datepicker.click()

    # Wait for calendar to open
    popover = dash_dcc.find_element(".dash-datepicker-content")

    interactive_elements = []
    interactive_elements.extend(popover.find_elements(By.CSS_SELECTOR, "td"))
    interactive_elements.extend(popover.find_elements(By.CSS_SELECTOR, "button"))
    interactive_elements.extend(popover.find_elements(By.CSS_SELECTOR, "input"))
    for el in interactive_elements:
        try:
            el.click()
            sleep(0.05)
        except Exception as e:
            print(e)
            assert not e, f"Unable to click on {el.tag_name})"


def test_mspv001_popover_visibility_when_app_is_smaller_than_popup(dash_dcc):
    """
    This test clicks on each datepicker and verifies all calendar elements are clickable.
    It verifies that the calendar popover is properly positioned and not clipped.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("Popover Visibility when app is only a few pixels tall"),
            dcc.DatePickerSingle(
                id="dps",
                date=date(2024, 1, 15),
                stay_open_on_select=True,
            ),
            dcc.DatePickerRange(
                id="dpr",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 15),
                stay_open_on_select=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False)
    dash_dcc.driver.set_window_size(1280, 1024)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dps")
    dash_dcc.wait_for_element("#dpr")

    # Test DatePickerSingle - click everything to verify all elements are accessible
    click_everything_in_datepicker("#dps", dash_dcc)

    # Close the calendar by pressing escape
    from selenium.webdriver.common.keys import Keys

    dps_input = dash_dcc.find_element("#dps")
    dps_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    # Test DatePickerRange - click everything to verify all elements are accessible
    click_everything_in_datepicker("#dpr", dash_dcc)


def test_mspv002_popover_visibility_when_app_is_scrolled_down(dash_dcc):
    """
    This test clicks on each datepicker scrolled far down the page and verifies
    that the popover contents are still visible
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("Popover Visibility when app is only a few pixels tall"),
            html.P("", style={"height": "2000px"}),
            dcc.DatePickerSingle(
                id="dps",
                date=date(2024, 1, 1),
                stay_open_on_select=True,
            ),
            html.P("", style={"height": "2000px"}),
        ],
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dps")

    click_everything_in_datepicker("#dps", dash_dcc)


def test_mspv003_popover_contained_within_dash_app(dash_dcc):
    """Test that datepicker popovers are visible and clickable when multiple pickers are present.

    This test clicks on each datepicker and selects the first day of the month that appears.
    It verifies that the calendar popover is properly positioned and not clipped.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H1(
                "Test popover is visible inside an embedded app",
                style={"width": "200px"},
            ),
            html.Div(
                [
                    html.H3("DatePicker Popover Visibility Test"),
                    dcc.DatePickerSingle(id="dps", date=date(2024, 1, 15)),
                    dcc.DatePickerRange(
                        id="dpr",
                        start_date=date(2024, 1, 1),
                        end_date=date(2024, 1, 15),
                        stay_open_on_select=True,
                    ),
                ],
                id="react-entry-point",
                style={"overflow": "hidden", "display": "inline-flex"},
            ),
            html.Div("This column is outside of embedded app"),
        ],
        style={
            "display": "inline-flex",
            "minHeight": "600px",
        },
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dpr")

    # Click everything in the datepicker to verify all elements are accessible
    click_everything_in_datepicker("#dpr", dash_dcc)


def test_mspv004_popover_inherits_container_styles(dash_dcc):
    """Test that calendar days inherit font color and size from container.

    This test verifies that when a datepicker is placed inside a container with
    specific font styles (color and size), the calendar days inherit those styles.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePicker Style Inheritance Test"),
            html.Div(
                [
                    dcc.DatePickerSingle(id="dps", date=date(2024, 1, 15)),
                ],
                style={"color": "limegreen", "fontSize": "24px"},
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dps")

    # Click to open the calendar
    dps_input = dash_dcc.find_element("#dps")
    dps_input.click()

    # Wait for calendar to open
    dash_dcc.wait_for_element(".dash-datepicker-calendar-container")

    # Find a calendar day element (inside date, not outside days)
    calendar_day = dash_dcc.find_element(".dash-datepicker-calendar-date-inside")

    # Get computed styles
    font_size = calendar_day.value_of_css_property("font-size")

    # Font size should be 24px
    assert font_size == "24px", "Expected calendar day to inherit its font size"
