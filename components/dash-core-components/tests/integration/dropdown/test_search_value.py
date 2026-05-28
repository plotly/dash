from time import sleep

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from dash import Dash, Input, Output, dcc, html


def test_ddsv001_search_value(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [dcc.Dropdown(id="dropdown", search_value="something"), html.Div(id="output")]
    )

    @app.callback(
        Output("output", "children"), inputs=[Input("dropdown", "search_value")]
    )
    def update_output(search_value):
        return f'search_value="{search_value}"'

    dash_duo.start_server(app)

    # Get the inner input used for search value.
    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()
    input_ = dash_duo.find_element(".dash-dropdown-search")

    dash_duo.wait_for_text_to_equal("#output", 'search_value="something"')

    dash_duo.find_element(
        ".dash-dropdown-search-container .dash-dropdown-clear"
    ).click()
    input_.send_keys("x")
    dash_duo.wait_for_text_to_equal("#output", 'search_value="x"')

    assert dash_duo.get_logs() == []


def test_ddsv002_search_filter_and_scroll(dash_duo):
    """Search filters a virtualized dropdown, backspace restores all options,
    then scroll to the bottom and select the last item."""
    app = Dash(__name__)
    options = [
        {"label": f"Option {i + 1}", "value": f"opt_{i + 1}"} for i in range(100)
    ]
    app.layout = html.Div(
        [
            dcc.Dropdown(id="dropdown", options=options, value="opt_1"),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("dropdown", "value"))
    def update_output(value):
        return f"value={value}"

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#output", "value=opt_1")

    # Open the dropdown by clicking it
    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Click the search field to focus it
    search = dash_duo.find_element(".dash-dropdown-search")
    search.click()

    # Use ActionChains to type into the currently focused element,
    # which will fail if focus is stolen from the search field.
    def send_key(key):
        ActionChains(dash_duo.driver).send_keys(key).perform()

    # Type "100" one character at a time to filter down to "Option 100"
    send_key("1")
    sleep(0.2)
    send_key("0")
    sleep(0.2)
    send_key("0")
    sleep(0.2)

    # Should have exactly one option visible: "Option 100"
    visible_options = dash_duo.find_elements(".dash-dropdown-option")
    assert len(visible_options) == 1
    assert "Option 100" in visible_options[0].text

    # Backspace three times to clear the search and restore all options
    send_key(Keys.BACKSPACE)
    sleep(0.2)
    send_key(Keys.BACKSPACE)
    sleep(0.2)
    send_key(Keys.BACKSPACE)
    sleep(0.2)

    # Scroll to the bottom of the options list
    options_container = dash_duo.find_element(".dash-dropdown-options")
    dash_duo.driver.execute_script(
        "arguments[0].querySelector('.dash-options-list-virtualized').scrollTop = "
        "arguments[0].querySelector('.dash-options-list-virtualized').scrollHeight",
        options_container,
    )
    sleep(0.3)

    # Find and click the last option (Option 100)
    all_options = dash_duo.find_elements(".dash-dropdown-option")
    last_option = all_options[-1]
    assert "Option 100" in last_option.text
    last_option.click()

    dash_duo.wait_for_text_to_equal("#output", "value=opt_100")


def test_ddsv003_dropdown_virtualized_component_label_filtering(dash_duo):
    app = Dash(__name__)

    options = [
        {
            "label": html.Div(["Item ", html.Span(f"#{i}")]),
            "value": f"item_{i}",
            "search": f"item_{i}",
        }
        for i in range(1, 2000)
    ]

    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="dd",
                options=options,
                value="item_1",
                searchable=True,
                clearable=True,
            )
        ]
    )

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dd")
    dropdown.click()

    search = dash_duo.find_element(".dash-dropdown-search")

    # trigger filtering path that used to crash virtualized list
    search.send_keys("199")
    sleep(.5)

    assert dash_duo.get_logs() == []
