from dash_generator_test_component_nested import MyComponent as MyNestedComponent
from dash_generator_test_component_standard import MyComponent as MyStandardComponent

import dash
import dash_html_components as html


def test_gene001_simple_callback(dash_duo):
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            MyStandardComponent(id="standard", value="Standard"),
            MyNestedComponent(id="nested", value="Nested"),
        ]
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"
    assert dash_duo.wait_for_element("#nested").text == "Nested"
