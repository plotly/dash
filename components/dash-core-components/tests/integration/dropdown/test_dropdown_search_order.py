from dash import Dash, html, dcc, Input, Output
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


def test_ddso001_search_preserves_custom_order(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="dropdown",
                options=["11 Text", "12", "23", "112", "111", "110", "22"],
                searchable=True,
                search_order="original",
            ),
            html.Div(id="output"),
        ]
    )

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Search for '11'
    search_input = dash_duo.find_element(".dash-dropdown-search")
    search_input.send_keys("11")
    sleep(0.2)

    # Presents matching options in original order
    options = dash_duo.find_elements(".dash-dropdown-option")
    assert len(options) == 4
    assert [opt.text for opt in options] == ["11 Text", "112", "111", "110"]

    assert dash_duo.get_logs() == []


def test_ddso002_multi_search_preserves_custom_order(dash_duo):
    def send_keys(key):
        ActionChains(dash_duo.driver).send_keys(key).perform()

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="dropdown",
                options=["11 Text", "12", "112", "111", "110"],
                multi=True,
                searchable=True,
                search_order="original",
            ),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), Input("dropdown", "value"))
    def update_output(value):
        return f"Selected: {value}"

    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    # Select '12' (second option)
    send_keys(Keys.ARROW_DOWN)
    sleep(0.2)
    send_keys(Keys.ARROW_DOWN)
    sleep(0.2)
    send_keys(Keys.SPACE)
    dash_duo.wait_for_text_to_equal("#output", "Selected: ['12']")
    sleep(0.2)

    # Select '111' (fourth option)
    send_keys(Keys.ARROW_DOWN)
    sleep(0.2)
    send_keys(Keys.ARROW_DOWN)
    sleep(0.2)
    send_keys(Keys.SPACE)
    dash_duo.wait_for_text_to_equal("#output", "Selected: ['12', '111']")
    sleep(0.2)

    # Search for '1'
    send_keys(Keys.HOME)
    sleep(0.2)
    send_keys("1")
    sleep(0.2)

    # Presents selected options first and rest in original order
    options = dash_duo.find_elements(".dash-dropdown-option")
    assert len(options) == 5
    assert [opt.text for opt in options] == ["12", "111", "11 Text", "112", "110"]

    assert dash_duo.get_logs() == []


def test_ddso003_search_preserves_custom_order_full_list(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="dropdown",
                options=["A", "Zebra", "Apply", "Apple"],
                searchable=True,
                search_order="original",
            ),
            html.Div(id="output"),
        ]
    )
    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()

    search_input = dash_duo.find_element(".dash-dropdown-search")

    # Search for 'A', returns all options
    search_input.send_keys("A")
    sleep(0.2)

    # Presents all options in original order
    options = dash_duo.find_elements(".dash-dropdown-option")
    assert len(options) == 4
    assert [opt.text for opt in options] == ["A", "Zebra", "Apply", "Apple"]

    assert dash_duo.get_logs() == []


def test_ddso004_search_no_match(dash_duo):
    app = Dash(__name__)

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="dropdown",
                options=["11 Text", "12", "110", "111", "112"],
                searchable=True,
                search_order="original",
            ),
            html.Div(id="output"),
        ]
    )
    dash_duo.start_server(app)

    dropdown = dash_duo.find_element("#dropdown")
    dropdown.click()

    search_input = dash_duo.find_element(".dash-dropdown-search")

    # Search for 'A', returns no options
    search_input.send_keys("A")
    sleep(0.2)

    options = dash_duo.find_elements(".dash-dropdown-option")

    assert len(options) == 1
    assert [opt.text for opt in options] == ["No options found"]
    assert dash_duo.get_logs() == []
