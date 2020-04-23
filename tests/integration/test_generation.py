from dash import Dash
from dash_generator_test_component_nested import MyNestedComponent
from dash_generator_test_component_standard import MyStandardComponent
from dash_html_components import Div

from selenium.webdriver.support.ui import WebDriverWait


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

    dash_duo.percy_snapshot(name="gene001-simple-callback")


def test_gene002_arbitrary_resources(dash_duo):
    app = Dash(__name__)

    app.layout = Div(
        [
            MyStandardComponent(
                id="standard", value="Standard", style={"font-family": "godfather"}
            )
        ]
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"

    WebDriverWait(dash_duo.driver, 10).until(
        lambda _: dash_duo.driver.execute_script(
            "return document.fonts.check('1em godfather')"
        )
        is True,
    )

    dash_duo.percy_snapshot(name="gene002-arbitrary-resource")
