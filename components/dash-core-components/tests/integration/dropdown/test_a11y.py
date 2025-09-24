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
        dash_duo.wait_for_element("#dropdown .dash-dropdown-options", timeout=0.25)

    dash_duo.find_element("#label").click()
    dash_duo.wait_for_element("#dropdown .dash-dropdown-options")

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
        dash_duo.wait_for_element("#dropdown .dash-dropdown-options", timeout=0.25)

    dash_duo.find_element("#label").click()
    dash_duo.wait_for_element("#dropdown .dash-dropdown-options")

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
    dash_duo.wait_for_element("#dropdown .dash-dropdown-options")

    send_keys(
        Keys.ESCAPE
    )  # Expecting focus to remain on the dropdown after escaping out
    with pytest.raises(TimeoutException):
        dash_duo.wait_for_element("#dropdown .dash-dropdown-options", timeout=0.25)

    send_keys(Keys.ARROW_DOWN)  # Expecting the dropdown to open up
    dash_duo.wait_for_element("#dropdown .dash-dropdown-search")

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
