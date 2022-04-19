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
                    Button("click footer", id="to-footer"),
                    Div(id="from-header"),
                ],
            ),
            ComponentAsProp(
                id="shaped",
                shapeEl={
                    "header": Button("header", id="button-header"),
                    "footer": Div("initial", id="footer"),
                },
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

    @app.callback(
        Output("from-header", "children"), [Input("button-header", "n_clicks")]
    )
    def from_header(n_clicks):
        return f"From header: {n_clicks}"

    @app.callback(Output("footer", "children"), [Input("to-footer", "n_clicks")])
    def send_to_footer(n_clicks):
        return f"To footer: {n_clicks}"

    dash_duo.start_server(app)

    assert dash_duo.get_logs() == []

    dash_duo.wait_for_text_to_equal("#as-props", "as-props")

    elements = dash_duo.find_elements("#elements div")

    assert len(elements) == 3

    clicker = dash_duo.wait_for_element("#clicker")
    clicker.click()
    dash_duo.wait_for_text_to_equal("#output-from-prop", "From prop: 1")

    nested = dash_duo.wait_for_element("#send-nested")
    nested.click()
    dash_duo.wait_for_text_to_equal("#nested-output", "Nested: 1")

    to_list = dash_duo.find_element("#to-list")
    to_list.click()
    dash_duo.wait_for_text_to_equal("#list-output", "To list: 1")

    from_list = dash_duo.find_element("#list-two")
    from_list.click()
    dash_duo.wait_for_text_to_equal("#output-from-list", "From list: 1")

    from_header = dash_duo.find_element("#button-header")
    from_header.click()
    dash_duo.wait_for_text_to_equal("#from-header", "From header: 1")

    to_footer = dash_duo.find_element("#to-footer")
    to_footer.click()
    dash_duo.wait_for_text_to_equal("#footer", "To footer: 1")

    assert dash_duo.get_logs() == []
