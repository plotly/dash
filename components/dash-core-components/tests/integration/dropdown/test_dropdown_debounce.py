from dash import Dash, Input, Output, dcc, html
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


def test_ddde001_dropdown_debounce(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value=["MTL", "SF"],
                multi=True,
                closeOnSelect=False,
                debounce=True,
            ),
            html.Div(
                id="dropdown-value-out", style={"height": "10px", "width": "10px"}
            ),
        ]
    )

    @app.callback(
        Output("dropdown-value-out", "children"),
        Input("dropdown", "value"),
    )
    def update_value(val):
        return ", ".join(val)

    dash_duo.start_server(app)

    assert dash_duo.find_element("#dropdown-value-out").text == "MTL, SF"

    dash_duo.find_element("#dropdown").click()

    # deselect first item
    selected = dash_duo.find_elements(".dash-dropdown-options input[checked]")
    selected[0].click()

    # UI should update immediately (local state updated)
    assert dash_duo.find_element("#dropdown-value").text == "San Francisco"

    # Callback output should not change while dropdown is still open
    assert dash_duo.find_element("#dropdown-value-out").text == "MTL, SF"

    # Close the dropdown (ESC simulates user dismiss)
    actions = ActionChains(dash_duo.driver)
    actions.send_keys(Keys.ESCAPE).perform()
    time.sleep(0.1)

    # After closing, the callback output should be updated
    assert dash_duo.find_element("#dropdown-value-out").text == "SF"

    assert dash_duo.get_logs() == []
