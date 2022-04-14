from dash import Dash, Input, Output

from dash_test_components import ComponentAsProp
from dash.html import Button, Div


def test_rdcap001_component_as_prop(dash_duo):
    app = Dash(__name__)

    app.layout = Div(
        [
            ComponentAsProp(
                element=Div(
                    "as-props",
                    id="as-props",
                )
            ),
            ComponentAsProp(
                id="clicker-container", element=Button("click-me", id="clicker")
            ),
            ComponentAsProp(
                id="nested-output-container",
                element=Div(id="nested-output"),
            ),
            Div(
                [
                    Button("click-nested", id="send-nested"),
                    Div(id="output-from-prop"),
                ]
            ),
            ComponentAsProp(
                id="elements",
                elements=[
                    Div("one", id="list-one"),
                    Div("two", id="list-two"),
                    Div(id="list-output"),
                ],
            ),
            Div(
                [
                    Button("click-list", id="to-list"),
                    Div(id="output-from-list"),
                ]
            ),
        ]
    )

    @app.callback(
        Output("output-from-prop", "children"), [Input("clicker", "n_clicks")]
    )
    def from_as_prop(n_clicks):
        return f"From prop: {n_clicks}"

    @app.callback(
        Output("nested-output", "children"), [Input("send-nested", "n_clicks")]
    )
    def send_nested(n_clicks):
        return f"Nested: {n_clicks}"

    @app.callback(
        Output("output-from-list", "children"), [Input("list-two", "n_clicks")]
    )
    def send_list_output(n_clicks):
        return f"From list: {n_clicks}"

    @app.callback(Output("list-output", "children"), [Input("to-list", "n_clicks")])
    def send_to_list(n_clicks):
        return f"To list: {n_clicks}"

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#as-props", "as-props")

    clicker = dash_duo.wait_for_element("#clicker")
    clicker.click()
    dash_duo.wait_for_text_to_equal("#output-from-prop", "From prop: 1")

    nested = dash_duo.wait_for_element("#send-nested")
    nested.click()
    dash_duo.wait_for_text_to_equal("#nested-output", "Nested: 1")

    elements = dash_duo.find_elements("#elements div")

    assert len(elements) == 3

    to_list = dash_duo.find_element("#to-list")
    to_list.click()
    dash_duo.wait_for_text_to_equal("#list-output", "To list: 1")

    from_list = dash_duo.find_element("#list-two")
    from_list.click()
    dash_duo.wait_for_text_to_equal("#output-from-list", "From list: 1")
