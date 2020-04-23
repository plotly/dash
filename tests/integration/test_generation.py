from dash import Dash
from dash_generator_test_component_nested import MyNestedComponent
from dash_generator_test_component_standard import MyStandardComponent
from dash_html_components import Div


def test_gene001_simple_callback(dash_duo):
    app = Dash(__name__)

    app.layout = Div(
        [
            MyStandardComponent(id="standard", value="Standard"),
            MyNestedComponent(id="nested", value="Nested"),
        ]
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"
    assert dash_duo.wait_for_element("#nested").text == "Nested"


def test_gene002_arbitrary_resources(dash_duo):
    app = Dash(__name__)

    app.layout = Div(
        [
            MyStandardComponent(
                id="standard", value="Standard", style={"font-family": "godfather"}
            ),
            MyNestedComponent(id="nested", value="Nested"),
        ]
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"
    assert dash_duo.wait_for_element("#nested").text == "Nested"
