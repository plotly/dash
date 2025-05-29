import pytest

from dash import Dash, Input, Output
from dash.exceptions import PreventUpdate

from dash_generator_test_component_nested import MyNestedComponent
from dash_generator_test_component_standard import MyStandardComponent
from dash_generator_test_component_typescript import (
    TypeScriptComponent,
    TypeScriptClassComponent,
    StandardComponent,
    RequiredChildrenComponent,
)
from dash_test_components import StyledComponent
from dash.html import Button, Div

from selenium.webdriver.support.ui import WebDriverWait


def test_gene001_simple_callback(dash_duo):
    app = Dash(__name__)

    app.layout = Div(
        [
            # Note: `value` is not part of the explicit function signature
            # for MyStandardComponent, due to --max-props 2 in its build command
            # but this verifies that it still works.
            MyStandardComponent(id="standard", value="Standard"),
            MyNestedComponent(id="nested", value="Nested"),
            TypeScriptComponent(id="typescript", required_string="TypeScript"),
            TypeScriptClassComponent(
                id="typescript-class", required_string="TypeScriptClass"
            ),
            StandardComponent(id="ts-standard", children="jsx"),
        ],
        id="outer",
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"
    assert dash_duo.wait_for_element("#nested").text == "Nested"
    assert dash_duo.wait_for_element("#typescript").text == "TypeScript"
    assert dash_duo.wait_for_element("#typescript-class").text == "TypeScriptClass"
    assert dash_duo.wait_for_element("#ts-standard").text == "jsx"
    expected_html = (
        '<div id="standard">Standard</div>'
        '<div id="nested">Nested</div>'
        '<div id="typescript">TypeScript</div>'
        '<div class="typescript-class-component" id="typescript-class">TypeScriptClass</div>'
        '<div id="ts-standard">jsx</div>'
    )
    assert dash_duo.find_element("#outer").get_property("innerHTML") == expected_html


def test_gene002_arbitrary_resources(dash_duo):
    app = Dash(__name__)

    app.layout = Div([Button("Click", id="btn"), Div(id="container")])

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
    dash_duo.wait_for_text_to_equal("#styled", "Styled")

    WebDriverWait(dash_duo.driver, 10).until(
        lambda _: dash_duo.driver.execute_script(
            "return document.fonts.check('1em godfather')"
        )
        is True,
    )


def test_gene003_max_props():
    limited_props_doc = "large number of props for this component"
    # dash_generator_test_component_standard has max_props set to 2, so
    # MyStandardComponent gets the restricted signature and note about it
    # in its docstring.
    # dash_generator_test_component_nested and MyNestedComponent do not.
    assert limited_props_doc in MyStandardComponent.__doc__
    assert limited_props_doc not in MyNestedComponent.__doc__

    # Verify that it still works to check for invalid props in both cases
    with pytest.raises(TypeError):
        MyStandardComponent(valuex="nope")

    with pytest.raises(TypeError):
        MyNestedComponent(valuey="nor this")


def test_gene004_required_children_prop():
    with pytest.raises(TypeError):
        RequiredChildrenComponent()

    RequiredChildrenComponent(children="worked")
