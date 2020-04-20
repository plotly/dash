import dash
import dash_generator_test_component_nested
import dash_generator_test_component_standard
import dash_html_components


def test_gene001_simple_callback(dash_duo):
    app = dash.Dash(__name__)

    app.layout = dash_html_components.Div(
        [
            dash_generator_test_component_nested.MyStandardComponent(
                id="standard", value="Standard"
            ),
            dash_generator_test_component_standard.MyNestedComponent(
                id="nested", value="Nested"
            ),
        ]
    )

    dash_duo.start_server(app)

    assert dash_duo.wait_for_element("#standard").text == "Standard"
    assert dash_duo.wait_for_element("#nested").text == "Nested"
