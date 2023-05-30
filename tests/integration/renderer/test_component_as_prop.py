import uuid

from dash import Dash, Input, Output, callback_context, State, MATCH

from dash_test_components import ComponentAsProp

from dash.dcc import Checklist, Dropdown
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
            ComponentAsProp(
                dynamic={
                    "inside-dynamic": Div("dynamic", "inside-dynamic"),
                    "output-dynamic": Div(id="output-dynamic"),
                    "clicker": Button("click-dynamic", id="click-dynamic"),
                    "clicker-dict": Button("click-dict", id="click-dict"),
                    "clicker-list": Button("click-list", id="click-list"),
                    "clicker-nested": Button("click-nested", id="click-nested"),
                },
                dynamic_dict={
                    "node": {
                        "dict-dyn": Div("dict-dyn", id="inside-dict"),
                        "dict-2": Div("dict-2", id="inside-dict-2"),
                    }
                },
                dynamic_list=[
                    {
                        "list": Div("dynamic-list", id="inside-list"),
                        "list-2": Div("list-2", id="inside-list-2"),
                    },
                    {"list-3": Div("list-3", id="inside-list-3")},
                ],
                dynamic_nested_list=[
                    {"obj": {"nested": Div("nested", id="nested-dyn")}},
                    {
                        "obj": {
                            "nested": Div("nested-2", id="nested-2"),
                            "nested-again": Div("nested-again", id="nested-again"),
                        },
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

    @app.callback(
        Output("output-dynamic", "children"),
        Input("click-dynamic", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        return f"Clicked {n_clicks}"

    @app.callback(
        Output("inside-dict", "children"),
        Input("click-dict", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        return f"Clicked {n_clicks}"

    @app.callback(
        Output("inside-list", "children"),
        Input("click-list", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        return f"Clicked {n_clicks}"

    @app.callback(
        Output("nested-dyn", "children"),
        Input("click-nested", "n_clicks"),
        prevent_initial_call=True,
    )
    def on_click(n_clicks):
        return f"Clicked {n_clicks}"

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

    dash_duo.wait_for_text_to_equal("#inside-dynamic", "dynamic")
    dash_duo.wait_for_text_to_equal("#dict-dyn", "dict-dyn")
    dash_duo.wait_for_text_to_equal("#inside-dict-2", "dict-2")
    dash_duo.wait_for_text_to_equal("#nested-2", "nested-2")
    dash_duo.wait_for_text_to_equal("#nested-again", "nested-again")

    dash_duo.wait_for_text_to_equal("#inside-list", "dynamic-list")
    dash_duo.wait_for_text_to_equal("#inside-list-2", "list-2")
    dash_duo.wait_for_text_to_equal("#inside-list-3", "list-3")

    dash_duo.find_element("#click-dynamic").click()
    dash_duo.wait_for_text_to_equal("#output-dynamic", "Clicked 1")

    dash_duo.find_element("#click-dict").click()
    dash_duo.wait_for_text_to_equal("#inside-dict", "Clicked 1")

    dash_duo.find_element("#click-list").click()
    dash_duo.wait_for_text_to_equal("#inside-list", "Clicked 1")

    dash_duo.find_element("#click-nested").click()
    dash_duo.wait_for_text_to_equal("#nested-dyn", "Clicked 1")

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
        dash_duo.wait_for_text_to_equal(f"#options label:nth-child({i}) span", "")
        dash_duo.wait_for_element(f"#options label:nth-child({i}) button").click()
        dash_duo.wait_for_text_to_equal(f"#options label:nth-child({i}) span", "1")


def test_rdcap003_side_effect_regression(dash_duo):
    # Test for #2411, regression introduced by original rdcap002 fix
    # callback on the same components that is output with same id but not property triggered
    # on cap components of array type like Checklist.options[] and  Dropdown.options[].
    app = Dash(__name__)

    app.layout = Div([Button("3<->2", id="a"), Checklist(id="b"), Div(0, id="counter")])

    app.clientside_callback(
        "function(_, prev) {return parseInt(prev) + 1}",
        Output("counter", "children"),
        Input("b", "value"),
        State("counter", "children"),
        prevent_initial_call=True,
    )

    @app.callback(Output("b", "options"), Input("a", "n_clicks"))
    def opts(n):
        n_out = 3 - (n or 0) % 2
        return [str(i) for i in range(n_out)]

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#counter", "0")
    dash_duo.find_element("#a").click()
    assert len(dash_duo.find_elements("#b label > input")) == 2
    dash_duo.wait_for_text_to_equal("#counter", "0")
    dash_duo.find_element("#a").click()
    assert len(dash_duo.find_elements("#b label > input")) == 3
    dash_duo.wait_for_text_to_equal("#counter", "0")

    dash_duo.find_elements("#b label > input")[0].click()
    dash_duo.wait_for_text_to_equal("#counter", "1")


def test_rdcap004_side_effect_same_component(dash_duo):
    options = [
        {"label": "aa1", "value": "aa1"},
        {"label": "aa2", "value": "aa2"},
        {"label": "aa3", "value": "aa3"},
        {"label": "best value", "value": "bb1"},
        {"label": "better value", "value": "bb2"},
        {"label": "bye", "value": "bb3"},
    ]

    app = Dash(__name__)

    app.layout = Div(
        [
            Div(
                ["Single dynamic Dropdown", Dropdown(id="my-dynamic-dropdown")],
                style={"width": 200, "marginLeft": 20, "marginTop": 20},
            ),
            Button(
                "Reset",
                id="button",
                n_clicks=0,
            ),
            Div(0, id="counter"),
        ]
    )
    app.clientside_callback(
        "function(_, prev) {return parseInt(prev) + 1}",
        Output("counter", "children"),
        Input("my-dynamic-dropdown", "value"),
        State("counter", "children"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("my-dynamic-dropdown", "options"),
        Input("my-dynamic-dropdown", "search_value"),
    )
    def update_options(search_value):
        if search_value is None:
            return options
        return [o for o in options if search_value in o["label"]]

    @app.callback(
        Output("my-dynamic-dropdown", "value"),
        Input("button", "n_clicks"),
    )
    def on_button(n_clicks):
        return None

    dash_duo.start_server(app)

    # Initial callback
    dash_duo.wait_for_text_to_equal("#counter", "1")

    search = dash_duo.wait_for_element("#my-dynamic-dropdown input")

    search.send_keys("a")

    dash_duo.wait_for_text_to_equal("#counter", "1")
