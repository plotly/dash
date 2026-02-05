import pytest
from dash import Dash, Input, Output, dcc, html
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


def test_ddcf001_clearable_false_single(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="my-unclearable-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value="MTL",
                clearable=False,
            ),
            html.Div(id="dropdown-value", style={"height": "10px", "width": "10px"}),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        [Input("my-unclearable-dropdown", "value")],
    )
    def update_value(val):
        return val

    dash_duo.start_server(app)

    with pytest.raises(TimeoutException):
        WebDriverWait(dash_duo.driver, 1).until(
            lambda _: dash_duo.find_element(
                "#my-unclearable-dropdown .dash-dropdown-clear"
            )
        )

    output_text = dash_duo.find_element("#dropdown-value").text

    dash_duo.find_element("#my-unclearable-dropdown ").click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Clicking the selected item should not de-select it.
    # Click on the option container instead of the input directly
    selected_item = dash_duo.find_element(
        f'.dash-dropdown-option:has(input[value="{output_text}"])'
    )
    selected_item.click()
    assert dash_duo.find_element("#dropdown-value").text == output_text
    assert dash_duo.get_logs() == []


def test_ddcf001b_delete_backspace_keys_clearable_false(dash_duo):
    from selenium.webdriver.common.keys import Keys

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="my-unclearable-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value="MTL",
                clearable=False,
            ),
            html.Div(id="dropdown-value"),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        Input("my-unclearable-dropdown", "value"),
    )
    def update_value(val):
        return str(val)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#dropdown-value", "MTL")

    dropdown = dash_duo.find_element("#my-unclearable-dropdown")

    # Try to clear with Delete key - should not work since clearable=False
    dropdown.send_keys(Keys.DELETE)
    dash_duo.wait_for_text_to_equal("#dropdown-value", "MTL")

    # Try to clear with Backspace key - should not work since clearable=False
    dropdown.send_keys(Keys.BACKSPACE)
    dash_duo.wait_for_text_to_equal("#dropdown-value", "MTL")

    assert dash_duo.get_logs() == []


def test_ddcf001c_delete_backspace_keys_clearable_true(dash_duo):
    from selenium.webdriver.common.keys import Keys

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="my-clearable-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value="MTL",
                clearable=True,
            ),
            html.Div(id="dropdown-value"),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        Input("my-clearable-dropdown", "value"),
    )
    def update_value(val):
        return str(val)

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#dropdown-value", "MTL")

    dropdown = dash_duo.find_element("#my-clearable-dropdown")

    # Clear with Delete key - should work since clearable=True
    dropdown.send_keys(Keys.DELETE)
    dash_duo.wait_for_text_to_equal("#dropdown-value", "None")

    # Set a value again
    dropdown.click()
    dash_duo.wait_for_element(".dash-dropdown-options")
    option = dash_duo.find_element('.dash-dropdown-option:has(input[value="SF"])')
    option.click()
    dash_duo.wait_for_text_to_equal("#dropdown-value", "SF")

    # Clear with Backspace key - should work since clearable=True
    dropdown.send_keys(Keys.BACKSPACE)
    dash_duo.wait_for_text_to_equal("#dropdown-value", "None")

    assert dash_duo.get_logs() == []


def test_ddcf002_clearable_false_multi(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="my-unclearable-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value=["MTL", "SF"],
                multi=True,
                closeOnSelect=False,
                clearable=False,
            ),
            html.Div(id="dropdown-value", style={"height": "10px", "width": "10px"}),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        [Input("my-unclearable-dropdown", "value")],
    )
    def update_value(val):
        return ", ".join(val)

    dash_duo.start_server(app)

    with pytest.raises(TimeoutException):
        WebDriverWait(dash_duo.driver, 1).until(
            lambda _: dash_duo.find_element(
                "#my-unclearable-dropdown .dash-dropdown-clear"
            )
        )

    assert dash_duo.find_element("#dropdown-value").text == "MTL, SF"

    dash_duo.find_element("#my-unclearable-dropdown ").click()

    # Attempt to deselect all items. Everything should deselect until we get to
    # the last item which cannot be cleared.
    selected = dash_duo.find_elements(".dash-dropdown-options input[checked]")
    [el.click() for el in selected]

    assert dash_duo.find_element("#dropdown-value").text == "SF"

    assert dash_duo.get_logs() == []
