from datetime import date
from dash import Dash, html, dcc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import pytest


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
    interactive_elements.extend(popover.find_elements(By.CSS_SELECTOR, "input"))

    buttons = reversed(
        popover.find_elements(By.CSS_SELECTOR, "button")
    )  # reversed so that "close" button will be clicked after all other buttons
    interactive_elements.extend(buttons)  # Add close buttons last

    for el in interactive_elements:
        try:
            el.click()
            sleep(0.05)
        except Exception as e:
            print(e)
            assert not e, f"Unable to click on {el.tag_name})"


def test_dppt000_datepicker_single_default(dash_dcc):
    """Test DatePickerSingle with default (no portal) configuration.

    Verifies that the calendar opens without portal and all elements are clickable.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePickerSingle Default"),
            dcc.DatePickerSingle(
                id="dps-default",
                date=date(2024, 1, 15),
                stay_open_on_select=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    dash_dcc.wait_for_element("#dps-default")

    click_everything_in_datepicker("#dps-default", dash_dcc)

    dps_input = dash_dcc.find_element("#dps-default")
    dps_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    assert dash_dcc.get_logs() == []


def test_dppt001_datepicker_single_with_portal(dash_dcc):
    """Test DatePickerSingle with with_portal=True.

    Verifies that the calendar opens in a portal (document.body) and all
    elements are clickable.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePickerSingle with Portal"),
            dcc.DatePickerSingle(
                id="dps-portal",
                date=date(2024, 1, 15),
                stay_open_on_select=True,
                with_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dps-portal")

    # Test DatePickerSingle with portal - click everything to verify all elements are accessible
    click_everything_in_datepicker("#dps-portal", dash_dcc)

    # Close the calendar by pressing escape
    dps_input = dash_dcc.find_element("#dps-portal")
    dps_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    assert dash_dcc.get_logs() == []


def test_dppt006_fullscreen_portal_close_button_keyboard(dash_dcc):
    """Test fullscreen portal dismiss behavior and keyboard accessibility.

    Verifies clicking background doesn't close the portal and close button
    is keyboard-accessible.
    """
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps-fullscreen",
                date=date(2024, 1, 15),
                with_full_screen_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)
    dash_dcc.wait_for_element("#dps-fullscreen")

    dps = dash_dcc.find_element("#dps-fullscreen")
    dps.click()

    popover = dash_dcc.find_element(".dash-datepicker-content")
    assert popover.is_displayed()

    action = ActionChains(dash_dcc.driver)
    action.move_to_element_with_offset(popover, 10, 10).click().perform()
    sleep(0.2)

    popover = dash_dcc.find_element(".dash-datepicker-content")
    assert (
        popover.is_displayed()
    ), "Fullscreen portal should not close when clicking background"

    dash_dcc.find_element(".dash-datepicker-close-button")

    action.send_keys(Keys.TAB).perform()
    sleep(0.1)
    action.send_keys(Keys.ENTER).perform()
    sleep(0.2)

    dash_dcc.wait_for_no_elements(".dash-datepicker-content", timeout=2)
    assert dash_dcc.get_logs() == []


def test_dppt007_portal_close_by_clicking_outside(dash_dcc):
    """Test regular portal closes when clicking outside the calendar."""
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.DatePickerSingle(
                id="dps-portal",
                date=date(2024, 1, 15),
                with_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)
    dash_dcc.wait_for_element("#dps-portal")

    dps = dash_dcc.find_element("#dps-portal")
    dps.click()

    popover = dash_dcc.find_element(".dash-datepicker-content")
    assert popover.is_displayed()

    popover.click()
    sleep(0.2)

    dash_dcc.wait_for_no_elements(".dash-datepicker-content", timeout=2)
    assert dash_dcc.get_logs() == []


def test_dppt001a_datepicker_range_default(dash_dcc):
    """Test DatePickerRange with default (no portal) configuration.

    Verifies that the calendar opens without portal and all elements are clickable.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePickerRange Default"),
            dcc.DatePickerRange(
                id="dpr-default",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 15),
                stay_open_on_select=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    dash_dcc.wait_for_element("#dpr-default")

    click_everything_in_datepicker("#dpr-default", dash_dcc)

    dpr_input = dash_dcc.find_element("#dpr-default")
    dpr_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    assert dash_dcc.get_logs() == []


def test_dppt002_datepicker_range_with_portal(dash_dcc):
    """Test DatePickerRange with with_portal=True.

    Verifies that the calendar opens in a portal (document.body) and all
    elements are clickable.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePickerRange with Portal"),
            dcc.DatePickerRange(
                id="dpr-portal",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 15),
                stay_open_on_select=True,
                with_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dpr-portal")

    # Test DatePickerRange with portal - click everything to verify all elements are accessible
    click_everything_in_datepicker("#dpr-portal", dash_dcc)

    # Close the calendar by pressing escape
    dpr_input = dash_dcc.find_element("#dpr-portal")
    dpr_input.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)


def test_dppt003_datepicker_single_with_fullscreen_portal(dash_dcc):
    """Test DatePickerSingle with with_full_screen_portal=True.

    Verifies that the calendar opens in a full-screen portal overlay and all
    elements are clickable. Also verifies that the fullscreen CSS class is applied.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePickerSingle with Full Screen Portal"),
            dcc.DatePickerSingle(
                id="dps-fullscreen",
                date=date(2024, 1, 15),
                stay_open_on_select=True,
                with_full_screen_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dps-fullscreen")

    # Click to open the calendar
    dps = dash_dcc.find_element("#dps-fullscreen")
    dps.click()

    # Wait for calendar to open
    popover = dash_dcc.find_element(".dash-datepicker-content")

    # Verify fullscreen class is applied
    assert "dash-datepicker-fullscreen" in popover.get_attribute(
        "class"
    ), "Full screen portal should have dash-datepicker-fullscreen class"

    # Verify the popover has fixed positioning (full screen overlay)
    position = popover.value_of_css_property("position")
    assert position == "fixed", "Full screen portal should use fixed positioning"

    # Close to prepare for click everything test
    dps.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    # Test clicking everything to verify all elements are accessible
    click_everything_in_datepicker("#dps-fullscreen", dash_dcc)


@pytest.mark.flaky(max_runs=3)
def test_dppt004_datepicker_range_with_fullscreen_portal(dash_dcc):
    """Test DatePickerRange with with_full_screen_portal=True.

    Verifies that the calendar opens in a full-screen portal overlay and all
    elements are clickable. Also verifies that the fullscreen CSS class is applied.

    Note: Marked as flaky due to headless Chrome layout issues with wide calendars
    (2 months shown by default in DatePickerRange). Test passes consistently in
    non-headless mode.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("DatePickerRange with Full Screen Portal"),
            dcc.DatePickerRange(
                id="dpr-fullscreen",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 15),
                stay_open_on_select=True,
                with_full_screen_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dpr-fullscreen")

    # Click to open the calendar
    dpr = dash_dcc.find_element("#dpr-fullscreen")
    dpr.click()

    # Wait for calendar to open
    popover = dash_dcc.find_element(".dash-datepicker-content")

    # Verify fullscreen class is applied
    assert "dash-datepicker-fullscreen" in popover.get_attribute(
        "class"
    ), "Full screen portal should have dash-datepicker-fullscreen class"

    # Verify the popover has fixed positioning (full screen overlay)
    position = popover.value_of_css_property("position")
    assert position == "fixed", "Full screen portal should use fixed positioning"

    # Close to prepare for click everything test
    dpr.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-calendar-container", timeout=2)

    # Test clicking everything to verify all elements are accessible
    click_everything_in_datepicker("#dpr-fullscreen", dash_dcc)


def test_dppt005_portal_has_correct_classes(dash_dcc):
    """Test that portal datepickers have the correct CSS classes.

    Verifies that default datepickers don't have portal classes, while
    with_portal=True datepickers have the portal class but not fullscreen class.
    """
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H3("Default (no portal)"),
            dcc.DatePickerSingle(
                id="dps-default",
                date=date(2024, 1, 15),
            ),
            html.H3("With portal", style={"marginTop": "50px"}),
            dcc.DatePickerSingle(
                id="dps-with-portal",
                date=date(2024, 1, 15),
                with_portal=True,
            ),
        ]
    )

    dash_dcc.start_server(app, debug=True, use_reloader=False, dev_tools_ui=False)

    # Wait for the page to load
    dash_dcc.wait_for_element("#dps-default")
    dash_dcc.wait_for_element("#dps-with-portal")

    # Open default datepicker
    dps_default = dash_dcc.find_element("#dps-default")
    dps_default.click()

    # Wait for calendar to open
    popover_default = dash_dcc.find_element(".dash-datepicker-content")

    # Verify it doesn't have fullscreen class
    assert "dash-datepicker-fullscreen" not in popover_default.get_attribute(
        "class"
    ), "Default datepicker should not have fullscreen class"

    # Close default
    dps_default.send_keys(Keys.ESCAPE)
    dash_dcc.wait_for_no_elements(".dash-datepicker-content", timeout=2)

    # Open portal datepicker
    dps_portal = dash_dcc.find_element("#dps-with-portal")
    dps_portal.click()

    # Wait for calendar to open
    popover_portal = dash_dcc.find_element(".dash-datepicker-content")

    # Verify it has portal class but not fullscreen class
    assert "dash-datepicker-portal" in popover_portal.get_attribute(
        "class"
    ), "Portal should have dash-datepicker-portal class"
    assert "dash-datepicker-fullscreen" not in popover_portal.get_attribute(
        "class"
    ), "Portal (non-fullscreen) should not have fullscreen class"

    # Verify it uses fixed positioning (both portal types use fixed positioning)
    position = popover_portal.value_of_css_property("position")
    assert position == "fixed", "Portal should use fixed positioning"

    assert dash_dcc.get_logs() == []
