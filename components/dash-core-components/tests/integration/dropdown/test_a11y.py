import pytest
from dash import Dash, Input, Output
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
    dropdown.send_keys(Keys.ENTER)  # Open with Enter key
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
    sleep(0.1)  # Wait for search filtering to complete
    num_elements = len(dash_duo.find_elements(".dash-dropdown-option"))
    assert num_elements == 19

    send_keys(Keys.ARROW_DOWN)  # Expecting to be navigating through the options
    send_keys(Keys.SPACE)  # Expecting to be selecting
    value_items = dash_duo.find_elements(".dash-dropdown-value-item")
    assert len(value_items) == 1
    assert value_items[0].text == "1"

    send_keys(Keys.ARROW_DOWN)  # Expecting to be navigating through the options
    send_keys(Keys.SPACE)  # Expecting to be selecting
    value_items = dash_duo.find_elements(".dash-dropdown-value-item")
    assert len(value_items) == 2
    assert [item.text for item in value_items] == ["1", "10"]

    send_keys(Keys.SPACE)  # Expecting to be de-selecting
    value_items = dash_duo.find_elements(".dash-dropdown-value-item")
    assert len(value_items) == 1
    assert value_items[0].text == "1"

    send_keys(Keys.ARROW_UP)
    send_keys(Keys.ARROW_UP)
    send_keys(Keys.ARROW_UP)  # Expecting to wrap over to the last item
    send_keys(Keys.SPACE)
    value_items = dash_duo.find_elements(".dash-dropdown-value-item")
    assert len(value_items) == 2
    assert [item.text for item in value_items] == ["1", "91"]

    send_keys(
        Keys.ESCAPE
    )  # Expecting focus to remain on the dropdown after escaping out
    sleep(0.25)
    value_items = dash_duo.find_elements(".dash-dropdown-value-item")
    assert len(value_items) == 2
    assert [item.text for item in value_items] == ["1", "91"]

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
    dash_duo.wait_for_element(".dash-dropdown-options")

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
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Assert that the selected option is visible in the dropdown
    selected_options = dash_duo.find_elements(".dash-dropdown-option.selected")
    assert elements_are_visible(
        dash_duo, selected_options
    ), "Selected options should be visible when the dropdown opens"

    assert dash_duo.get_logs() == []


def test_a11y006_multi_select_keyboard_focus_retention(dash_duo):
    def send_keys(key):
        actions = ActionChains(dash_duo.driver)
        actions.send_keys(key)
        actions.perform()

    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[f"Option {i}" for i in range(0, 10)],
                value=[],
                multi=True,
                searchable=True,
            ),
            Div(id="output"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        Input("dropdown", "value"),
    )
    def update_output(value):
        return f"Selected: {value}"

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Select 3 items by alternating ArrowDown and Spacebar
    send_keys(Keys.ARROW_DOWN)  # Move to first option
    sleep(0.05)
    send_keys(Keys.SPACE)  # Select Option 0
    dash_duo.wait_for_text_to_equal("#output", "Selected: ['Option 0']")

    send_keys(Keys.ARROW_DOWN)  # Move to second option
    sleep(0.05)
    send_keys(Keys.SPACE)  # Select Option 1
    dash_duo.wait_for_text_to_equal("#output", "Selected: ['Option 0', 'Option 1']")

    send_keys(Keys.ARROW_DOWN)  # Move to third option
    sleep(0.05)
    send_keys(Keys.SPACE)  # Select Option 2
    dash_duo.wait_for_text_to_equal(
        "#output", "Selected: ['Option 0', 'Option 1', 'Option 2']"
    )

    assert dash_duo.get_logs() == []


def test_a11y007_opens_and_closes_without_races(dash_duo):
    def send_keys(key):
        actions = ActionChains(dash_duo.driver)
        actions.send_keys(key)
        actions.perform()

    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[f"Option {i}" for i in range(0, 10)],
                value="Option 5",
                multi=False,
            ),
            Div(id="output"),
        ]
    )

    def assert_focus_in_dropdown():
        # Verify focus is inside the dropdown
        assert dash_duo.driver.execute_script(
            """
            const activeElement = document.activeElement;
            const dropdownContent = document.querySelector('.dash-dropdown-content');
            return dropdownContent && dropdownContent.contains(activeElement);
            """
        ), "Focus must be inside the dropdown when it opens"

    @app.callback(
        Output("output", "children"),
        Input("dropdown", "value"),
    )
    def update_output(value):
        return f"Selected: {value}"

    dash_duo.start_server(app)

    # Verify initial value is set
    dash_duo.wait_for_text_to_equal("#output", "Selected: Option 5")

    dropdown = dash_duo.find_element("#dropdown")

    # Test repeated open/close to confirm no race conditions or side effects
    for i in range(3):
        # Open with Enter
        dropdown.send_keys(Keys.ENTER)
        dash_duo.wait_for_element(".dash-dropdown-options")
        assert_focus_in_dropdown()

        # Verify the value is still "Option 5" (not cleared)
        dash_duo.wait_for_text_to_equal("#output", "Selected: Option 5")

        # Close with Escape
        send_keys(Keys.ESCAPE)
        sleep(0.1)

        # Verify the value is still "Option 5"
        dash_duo.wait_for_text_to_equal("#output", "Selected: Option 5")

    for i in range(3):
        # Open with mouse
        dropdown.click()
        dash_duo.wait_for_element(".dash-dropdown-options")
        assert_focus_in_dropdown()

        # Verify the value is still "Option 5" (not cleared)
        dash_duo.wait_for_text_to_equal("#output", "Selected: Option 5")

        # Close with Escape
        dropdown.click()
        sleep(0.1)

        # Verify the value is still "Option 5"
        dash_duo.wait_for_text_to_equal("#output", "Selected: Option 5")

    assert dash_duo.get_logs() == []


def test_a11y008_home_end_pageup_pagedown_navigation(dash_duo):
    def send_keys(key):
        actions = ActionChains(dash_duo.driver)
        actions.send_keys(key)
        actions.perform()

    def get_focused_option_text():
        return dash_duo.driver.execute_script(
            """
            const focused = document.activeElement;
            if (focused && focused.closest('.dash-options-list-option')) {
                return focused.closest('.dash-options-list-option').textContent.trim();
            }
            return null;
            """
        )

    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[f"Option {i}" for i in range(0, 50)],
                multi=True,
            ),
        ]
    )

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.send_keys(Keys.ENTER)  # Open with Enter key
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Navigate from search input to options
    send_keys(Keys.ARROW_DOWN)  # Move from search to first option
    sleep(0.05)
    send_keys(Keys.ARROW_DOWN)  # Move to second option
    sleep(0.05)
    send_keys(Keys.ARROW_DOWN)  # Move to third option
    sleep(0.05)
    send_keys(Keys.ARROW_DOWN)  # Move to fourth option
    sleep(0.05)
    assert get_focused_option_text() == "Option 3"

    send_keys(Keys.HOME)  # Should go back to search input (index 0)
    # Verify we're back at search input
    assert dash_duo.driver.execute_script(
        "return document.activeElement.type === 'search';"
    )

    # Now arrow down to first option
    send_keys(Keys.ARROW_DOWN)
    assert get_focused_option_text() == "Option 0"

    # Test End key - should go to last option
    send_keys(Keys.END)
    assert get_focused_option_text() == "Option 49"

    # Test PageUp - should jump up by 10
    send_keys(Keys.PAGE_UP)
    assert get_focused_option_text() == "Option 39"

    # Test PageDown - should jump down by 10
    send_keys(Keys.PAGE_DOWN)
    assert get_focused_option_text() == "Option 49"

    # Test PageUp from middle
    send_keys(Keys.HOME)  # Back to search input (index 0)
    send_keys(Keys.PAGE_DOWN)  # Jump to index 10 (Option 9)
    send_keys(Keys.PAGE_DOWN)  # Jump to index 20 (Option 19)
    assert get_focused_option_text() == "Option 19"

    send_keys(Keys.PAGE_UP)  # Jump to index 10 (Option 9)
    assert get_focused_option_text() == "Option 9"

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
