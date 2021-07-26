from dash import Dash, Input, Output, dcc, html

from selenium.webdriver.common.keys import Keys


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

    dropdown = dash_duo.find_element("#my-unclearable-dropdown input")
    dropdown.send_keys(Keys.BACKSPACE)
    dash_duo.find_element("#dropdown-value").click()

    assert len(dash_duo.find_element("#dropdown-value").text) > 0

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

    dropdown = dash_duo.find_element("#my-unclearable-dropdown input")
    dropdown.send_keys(Keys.BACKSPACE)
    dropdown.send_keys(Keys.BACKSPACE)
    dash_duo.find_element("#dropdown-value").click()

    assert len(dash_duo.find_element("#dropdown-value").text) > 0

    assert dash_duo.get_logs() == []
