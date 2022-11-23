import uuid

from dash import Dash, Input, Output, callback_context, State, MATCH

from dash_test_components import ComponentAsProp

from dash.dcc import Checklist
from dash.html import Button, Div, Span


def opt(u):
    return {
        "label": [
            Button(
                "click me", id={"type": "button", "index": u}, className="label-button"
            ),
            Span(id={"type": "text", "index": u}, className="label-result"),
        ],
        "value": u,
    }


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
                element=[
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
                    Div(id="from-list-of-dict"),
                    Button("click to list", id="update-list-of-dict"),
                ],
            ),
            ComponentAsProp(
                id="shaped",
                shapeEl={
                    "header": Button("header", id="button-header"),
                    "footer": Div("initial", id="footer"),
                },
            ),
            ComponentAsProp(
                id="list-of-dict",
                list_of_shapes=[
                    {"label": Button(f"click-{i}", id=f"list-click-{i}"), "value": i}
                    for i in range(1, 4)
                ],
            ),
            ComponentAsProp(
                "list-of-dict-update",
                list_of_shapes=[
                    {
                        "label": Div("update me", id="update-in-list-of-dict"),
                        "value": 1,
                    },
                ],
            ),
            ComponentAsProp(
                id="list-of-list-of-nodes",
                list_of_shapes=[
                    {
                        "label": [
                            Div("first-label", id="first-label"),
                            Div("second-label", id="second-label"),
                        ],
                        "value": 2,
                    }
                ],
            ),
            ComponentAsProp(
                id="list-in-shape",
                shapeEl={
                    "header": [
                        Div("one", id="first-in-shape"),
                        Div("two", id="second-in-shape"),
                    ]
                },
            ),
            ComponentAsProp(
                id="multi-component",
                multi_components=[
                    {
                        "id": "multi",
                        "first": Span("first"),
                        "second": Span("second"),
                    },
                    {
                        "id": "multi2",
                        "first": Span("foo"),
                        "second": Span("bar"),
                    },
                ],
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

    @app.callback(
        Output("update-in-list-of-dict", "children"),
        [Input("update-list-of-dict", "n_clicks")],
    )
    def send_to_list_of_dict(n_clicks):
        return f"Updated: {n_clicks}"

    @app.callback(
        Output("from-list-of-dict", "children"),
        [Input(f"list-click-{i}", "n_clicks") for i in range(1, 4)],
        prevent_initial_call=True,
    )
    def updated_from_list(*_):
        return callback_context.triggered[0]["prop_id"]

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

    for btn_id in (f"list-click-{i}" for i in range(1, 4)):
        dash_duo.find_element(f"#{btn_id}").click()
        dash_duo.wait_for_text_to_equal("#from-list-of-dict", f"{btn_id}.n_clicks")

    dash_duo.find_element("#update-list-of-dict").click()
    dash_duo.wait_for_text_to_equal("#update-in-list-of-dict", "Updated: 1")

    dash_duo.wait_for_text_to_equal("#first-label", "first-label")
    dash_duo.wait_for_text_to_equal("#second-label", "second-label")

    dash_duo.wait_for_text_to_equal("#first-in-shape", "one")
    dash_duo.wait_for_text_to_equal("#second-in-shape", "two")

    dash_duo.wait_for_text_to_equal("#multi", "first - second")
    dash_duo.wait_for_text_to_equal("#multi2", "foo - bar")

    assert dash_duo.get_logs() == []


def test_rdcap002_component_as_props_dynamic_id(dash_duo):
    # Test for issue 2296
    app = Dash(__name__)
    n = 3
    app.layout = Div(
        [
            Button("add options", id="add-option", style={"marginBottom": "25px"}),
            Checklist([opt(str(uuid.uuid4())) for i in range(n)], id="options"),
        ]
    )

    @app.callback(
        Output("options", "options"),
        Input("add-option", "n_clicks"),
        State("options", "options"),
        prevent_initial_call=True,
    )
    def add_option(_, options):
        return [*options, opt(str(uuid.uuid4()))]

    @app.callback(
        Output({"type": "text", "index": MATCH}, "children"),
        Input({"type": "button", "index": MATCH}, "n_clicks"),
    )
    def demo(n_clicks):
        return n_clicks

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#add-option").click()
    for i in range(1, n + 2):
        dash_duo.wait_for_element(f"#options label:nth-child({i}) button").click()
        dash_duo.wait_for_text_to_equal(f"#options label:nth-child({i}) span", "1")
