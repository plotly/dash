import pytest
from dash import Dash
from dash.dcc import Dropdown
from dash.html import Div, Label, P
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


def test_a11y001_label_focuses_dropdown(dash_duo):
    app = Dash(__name__)
    app.layout = Label(
        [
            P("Click me", id="label"),
            Dropdown(
                id="dropdown",
                options=[1, 2, 3],
                multi=True,
                placeholder="Testing label that wraps a dropdown can trigger the dropdown",
            ),
        ],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#dropdown")

    with pytest.raises(TimeoutException):
        dash_duo.wait_for_element(".dash-dropdown-options", timeout=0.25)

    dash_duo.find_element("#label").click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    assert dash_duo.get_logs() == []


def test_a11y002_label_with_htmlFor_can_focus_dropdown(dash_duo):
    app = Dash(__name__)
    app.layout = Div(
        [
            Label("Click me", htmlFor="dropdown", id="label"),
            Dropdown(
                id="dropdown",
                options=[1, 2, 3],
                multi=True,
                placeholder="Testing label with `htmlFor` triggers the dropdown",
            ),
        ],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#dropdown")

    with pytest.raises(TimeoutException):
        dash_duo.wait_for_element(".dash-dropdown-options", timeout=0.25)

    dash_duo.find_element("#label").click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    assert dash_duo.get_logs() == []


def test_a11y003_keyboard_navigation(dash_duo):
    def send_keys(key):
        actions = ActionChains(dash_duo.driver)
        actions.send_keys(key)
        actions.perform()

    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[i for i in range(0, 100)],
                multi=True,
                placeholder="Testing keyboard navigation",
            ),
        ],
    )

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    send_keys(
        Keys.ESCAPE
    )  # Expecting focus to remain on the dropdown after escaping out
    with pytest.raises(TimeoutException):
        dash_duo.wait_for_element(".dash-dropdown-options", timeout=0.25)

    send_keys(Keys.ARROW_DOWN)  # Expecting the dropdown to open up
    dash_duo.wait_for_element(".dash-dropdown-search")

    num_elements = len(dash_duo.find_elements(".dash-dropdown-option"))
    assert num_elements == 100

    send_keys(1)  # Expecting to be typing into the searh bar
    num_elements = len(dash_duo.find_elements(".dash-dropdown-option"))
    assert num_elements == 19

    send_keys(Keys.ARROW_DOWN)  # Expecting to be navigating through the options
    send_keys(Keys.SPACE)  # Expecting to be selecting
    assert dash_duo.find_element(".dash-dropdown-value").text == "1"

    send_keys(Keys.ARROW_DOWN)  # Expecting to be navigating through the options
    send_keys(Keys.SPACE)  # Expecting to be selecting
    assert dash_duo.find_element(".dash-dropdown-value").text == "1, 10"

    send_keys(Keys.SPACE)  # Expecting to be de-selecting
    assert dash_duo.find_element(".dash-dropdown-value").text == "1"

    send_keys(Keys.ARROW_UP)
    send_keys(Keys.ARROW_UP)
    send_keys(Keys.ARROW_UP)  # Expecting to wrap over to the last item
    send_keys(Keys.SPACE)
    assert dash_duo.find_element(".dash-dropdown-value").text == "1, 91"

    send_keys(
        Keys.ESCAPE
    )  # Expecting focus to remain on the dropdown after escaping out
    sleep(0.25)
    assert dash_duo.find_element(".dash-dropdown-value").text == "1, 91"

    assert dash_duo.get_logs() == []


def test_a11y004_selection_visibility_single(dash_duo):
    app = Dash(__name__)
    app.layout = (
        Dropdown(
            id="dropdown",
            options=[f"Option {i}" for i in range(0, 100)],
            value="Option 71",
            multi=False,
            placeholder="Testing selected item is visible on open",
        ),
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#dropdown")

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_element("#dropdown .dash-dropdown-options")

    # Assert that the selected option is visible in the dropdown
    selected_option = dash_duo.find_element(".dash-dropdown-option.selected")
    assert selected_option.text == "Option 71"
    assert selected_option.is_displayed()

    assert elements_are_visible(
        dash_duo, selected_option
    ), "Selected option should be visible when the dropdown opens"

    assert dash_duo.get_logs() == []


def test_a11y005_selection_visibility_multi(dash_duo):
    app = Dash(__name__)
    app.layout = (
        Dropdown(
            id="dropdown",
            options=[f"Option {i}" for i in range(0, 100)],
            value=[
                "Option 71",
                "Option 23",
                "Option 42",
            ],
            multi=True,
            placeholder="Testing selected item is visible on open",
        ),
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#dropdown")

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_element("#dropdown .dash-dropdown-options")

    # Assert that the selected option is visible in the dropdown
    selected_options = dash_duo.find_elements(".dash-dropdown-option.selected")
    assert elements_are_visible(
        dash_duo, selected_options
    ), "Selected options should be visible when the dropdown opens"

    assert dash_duo.get_logs() == []


def elements_are_visible(dash_duo, elements):
    # Check if the given elements are within the visible viewport of the dropdown
    elements = elements if isinstance(elements, list) else [elements]
    dropdown_content = dash_duo.find_element(".dash-dropdown-content")

    def is_visible(el):
        return dash_duo.driver.execute_script(
            """
            const option = arguments[0];
            const container = arguments[1];
            const optionRect = option.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            return optionRect.top >= containerRect.top &&
                optionRect.bottom <= containerRect.bottom;
            """,
            el,
            dropdown_content,
        )

    return all([is_visible(el) for el in elements])
