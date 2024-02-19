from dash import Dash, html, Input, Output
import dash_test_components as dt
import dash_generator_test_component_standard as dgs


def test_rblib001_dynamic_loading(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("Insert", id="insert-btn"),
            html.Div(id="output"),
            dgs.MyStandardComponent(id="dgs"),
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input("insert-btn", "n_clicks")],
        prevent_initial_call=True,
    )
    def update_output(_):
        import dash_generator_test_component_nested as dn

        return [
            dt.StyledComponent(value="Styled", id="styled"),
            dn.MyNestedComponent(value="nested", id="nested"),
        ]

    dash_duo.start_server(app)

    def assert_unloaded(namespace):
        assert dash_duo.driver.execute_script(
            f"return window['{namespace}'] === undefined"
        )

    def assert_loaded(namespace):
        assert dash_duo.driver.execute_script(
            f"return window['{namespace}'] !== undefined"
        )

    assert_unloaded(dt.package_name)
    assert_unloaded(dgs.package_name)
    assert_unloaded("dash_generator_test_component_nested")
    dash_duo.wait_for_element("#dgs")
    assert_unloaded(dt.package_name)
    assert_loaded(dgs.package_name)

    dash_duo.wait_for_element("#insert-btn").click()

    dash_duo.wait_for_element("#styled")
    assert_loaded(dt.package_name)
    assert_loaded("dash_generator_test_component_nested")
