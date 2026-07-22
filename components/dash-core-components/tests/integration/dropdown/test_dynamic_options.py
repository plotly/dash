import time

from selenium.webdriver.common.keys import Keys

from dash import Dash, Input, Output, dcc, html
from dash.exceptions import PreventUpdate


def test_dddo001_dynamic_options(dash_dcc):
    dropdown_options = [
        {"label": "New York City", "value": "NYC"},
        {"label": "Montreal", "value": "MTL"},
        {"label": "San Francisco", "value": "SF"},
    ]

    app = Dash(__name__)
    app.layout = dcc.Dropdown(id="my-dynamic-dropdown", options=[])

    @app.callback(
        Output("my-dynamic-dropdown", "options"),
        [Input("my-dynamic-dropdown", "search_value")],
    )
    def update_options(search_value):
        if not search_value:
            raise PreventUpdate
        return [o for o in dropdown_options if search_value in o["label"]]

    dash_dcc.start_server(app)

    dropdown = dash_dcc.find_element("#my-dynamic-dropdown")
    dropdown.click()

    # Get the inner input used for search value.
    input_ = dash_dcc.find_element(".dash-dropdown-content input")

    # Focus on the input to open the options menu
    input_.send_keys("x")

    # No options to be found with `x` in them, should show the empty message.
    dash_dcc.wait_for_text_to_equal(".dash-dropdown-options", "No options found")

    input_.clear()
    input_.send_keys("o")

    time.sleep(0.25)
    options = dash_dcc.find_elements(".dash-dropdown-options .dash-dropdown-option")

    # Should show all options.
    assert len(options) == 3

    # Searching for `on`
    input_.send_keys("n")

    time.sleep(0.25)
    options = dash_dcc.find_elements(".dash-dropdown-options .dash-dropdown-option")

    assert len(options) == 1
    assert options[0].text == "Montreal"

    assert dash_dcc.get_logs() == []


def test_dddo002_array_comma_value(dash_dcc):
    app = Dash(__name__)

    dropdown = dcc.Dropdown(
        options=["New York, NY", "Montreal, QC", "San Francisco, CA"],
        value=["San Francisco, CA"],
        multi=True,
    )
    app.layout = html.Div(dropdown)

    dash_dcc.start_server(app)

    dash_dcc.wait_for_text_to_equal(".dash-dropdown-value", "San Francisco, CA")

    assert dash_dcc.get_logs() == []


def test_dddo003_value_no_options(dash_dcc):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Dropdown(value="foobar", id="dropdown"),
        ]
    )

    dash_dcc.start_server(app)
    assert dash_dcc.get_logs() == []
    dash_dcc.wait_for_element("#dropdown")


def test_dddo004_dynamic_value_search(dash_dcc):
    # Bug clear the search input while typing
    # https://github.com/plotly/dash/issues/2099

    options = [
        {"label": "aa1", "value": "aa1"},
        {"label": "aa2", "value": "aa2"},
        {"label": "aa3", "value": "aa3"},
        {"label": "best value", "value": "bb1"},
        {"label": "better value", "value": "bb2"},
        {"label": "bye", "value": "bb3"},
    ]

    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                ["Single dynamic Dropdown", dcc.Dropdown(id="dropdown")],
                style={"width": 200, "marginLeft": 20, "marginTop": 20},
            ),
        ]
    )

    @app.callback(Output("dropdown", "options"), Input("dropdown", "search_value"))
    def update_options(search_value):
        if not search_value:
            raise PreventUpdate
        return [o for o in options if search_value in o["label"]]

    dash_dcc.start_server(app)

    dropdown = dash_dcc.find_element("#dropdown")
    dropdown.click()
    input_ = dash_dcc.find_element(".dash-dropdown-search")

    input_.send_keys("aa1")
    input_.send_keys(Keys.ESCAPE)

    dropdown.click()
    input_ = dash_dcc.find_element(".dash-dropdown-search")
    input_.send_keys("b")

    time.sleep(1)
    assert input_.get_attribute("value") == "b"
