from dash import Dash, Input, Output
from dash.exceptions import PreventUpdate

from dash_generator_test_component_nested import MyNestedComponent
from dash_generator_test_component_standard import MyStandardComponent
from dash_generator_test_component_typescript import (
    TypeScriptComponent,
    TypeScriptClassComponent,
)
from dash_test_components import StyledComponent
from dash.html import Button, Div

from selenium.webdriver.support.ui import WebDriverWait


def test_gene001_simple_callback(dash_duo):
    app = Dash(__name__)

    app.layout = Div(
        [
            MyStandardComponent(id="standard", value="Standard"),
            MyNestedComponent(id="nested", value="Nested"),
            TypeScriptComponent(id="typescript", required_string="TypeScript"),
            TypeScriptClassComponent(
                id="typescript-class", required_string="TypeScriptClass"
            ),
        ]
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"
    assert dash_duo.wait_for_element("#nested").text == "Nested"
    assert dash_duo.wait_for_element("#typescript").text == "TypeScript"
    assert dash_duo.wait_for_element("#typescript-class").text == "TypeScriptClass"

    dash_duo.percy_snapshot(name="gene001-simple-callback")


def test_gene002_arbitrary_resources(dash_duo):
    app = Dash(__name__)

    app.layout = Div([Button(id="btn"), Div(id="container")])

    @app.callback(Output("container", "children"), [Input("btn", "n_clicks")])
    def update_container(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        return StyledComponent(
            id="styled", value="Styled", style={"font-family": "godfather"}
        )

    dash_duo.start_server(app)

    assert (
        dash_duo.driver.execute_script("return document.fonts.check('1em godfather')")
        is False
    )

    dash_duo.wait_for_element("#btn").click()
    assert dash_duo.wait_for_element("#styled").text == "Styled"

    WebDriverWait(dash_duo.driver, 10).until(
        lambda _: dash_duo.driver.execute_script(
            "return document.fonts.check('1em godfather')"
        )
        is True,
    )

    dash_duo.percy_snapshot(name="gene002-arbitrary-resource")
