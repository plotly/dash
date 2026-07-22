from dash import Dash
from dash.dcc import Dropdown
from dash.html import Div
from dash.dash_table import DataTable
from flaky import flaky
from selenium.webdriver.common.action_chains import ActionChains


@flaky(max_runs=3)
def test_ddst001_cursor_should_be_pointer(dash_duo):
    app = Dash(__name__)
    app.layout = Div(
        [
            Dropdown(
                id="dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                value="NYC",
            ),
            DataTable(
                id="table",
                columns=[
                    {"name": x, "id": x, "selectable": True} for x in ["a", "b", "c"]
                ],
                editable=True,
                row_deletable=True,
                fixed_rows=dict(headers=True),
                fixed_columns=dict(headers=True),
                data=[
                    {"a": "a" + str(x), "b": "b" + str(x), "c": "c" + str(x)}
                    for x in range(0, 20)
                ],
            ),
        ]
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#dropdown").click()
    dash_duo.wait_for_element(".dash-dropdown-options")

    items = dash_duo.find_elements(".dash-dropdown-options .dash-dropdown-option")

    assert items[0].value_of_css_property("cursor") == "pointer"

    # If the search element is visible, then we should be able to click on it.
    search_element = dash_duo.find_element(".dash-dropdown-search")
    actions = ActionChains(dash_duo.driver)
    actions.move_to_element_with_offset(search_element, 8, 8).click().perform()

    # The dropdown should remain open after clicking into the search bar
    dash_duo.wait_for_element(".dash-dropdown-options")
