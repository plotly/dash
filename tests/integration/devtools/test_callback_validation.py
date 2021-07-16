import flask
import pytest

from dash import Dash, Input, Output, State, MATCH, ALL, ALLSMALLER, html, dcc
from dash.testing import wait

debugging = dict(
    debug=True, use_reloader=False, use_debugger=True, dev_tools_hot_reload=False
)


def check_errors(dash_duo, specs):
    # Order-agnostic check of all the errors shown.
    # This is not fully general - despite the selectors below, it only applies
    # to front-end errors with no back-end errors in the list.
    cnt = len(specs)
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, str(cnt))

    found = []
    for i in range(cnt):
        msg = dash_duo.find_elements(".dash-fe-error__title")[i].text
        dash_duo.find_elements(".test-devtools-error-toggle")[i].click()
        dash_duo.wait_for_element(".dash-backend-error,.dash-fe-error__info")
        has_BE = dash_duo.driver.execute_script(
            "return document.querySelectorAll('.dash-backend-error').length"
        )
        txt_selector = ".dash-backend-error" if has_BE else ".dash-fe-error__info"
        txt = dash_duo.wait_for_element(txt_selector).text
        dash_duo.find_elements(".test-devtools-error-toggle")[i].click()
        dash_duo.wait_for_no_elements(".dash-backend-error")
        found.append((msg, txt))

    orig_found = found[:]

    for i, (message, snippets) in enumerate(specs):
        for j, (msg, txt) in enumerate(found):
            if msg == message and all(snip in txt for snip in snippets):
                print(j)
                found.pop(j)
                break
        else:
            raise AssertionError(
                (
                    "error {} ({}) not found with text:\n"
                    "  {}\nThe found messages were:\n---\n{}"
                ).format(
                    i,
                    message,
                    "\n  ".join(snippets),
                    "\n---\n".join(
                        "{}\n{}".format(msg, txt) for msg, txt in orig_found
                    ),
                )
            )

    # ensure the errors didn't leave items in the pendingCallbacks queue
    assert dash_duo.driver.execute_script("return document.title") == "Dash"


def test_dvcv001_blank(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div()

    @app.callback([], [])
    def x():
        return 42

    dash_duo.start_server(app, **debugging)
    check_errors(
        dash_duo,
        [
            ["A callback is missing Inputs", ["there are no `Input` elements."]],
            [
                "A callback is missing Outputs",
                ["Please provide an output for this callback:"],
            ],
        ],
    )


def test_dvcv002_blank_id_prop(dash_duo):
    # TODO: remove suppress_callback_exceptions after we move that part to FE
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div([html.Div(id="a")])

    @app.callback([Output("a", "children"), Output("", "")], [Input("", "")])
    def x(a):
        return a

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Callback item missing ID",
            ['Input[0].id = ""', "Every item linked to a callback needs an ID"],
        ],
        [
            "Callback property error",
            [
                'Input[0].property = ""',
                "expected `property` to be a non-empty string.",
            ],
        ],
        [
            "Callback item missing ID",
            ['Output[1].id = ""', "Every item linked to a callback needs an ID"],
        ],
        [
            "Callback property error",
            [
                'Output[1].property = ""',
                "expected `property` to be a non-empty string.",
            ],
        ],
    ]
    check_errors(dash_duo, specs)


def test_dvcv003_duplicate_outputs_same_callback(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="a"), html.Div(id="b")])

    @app.callback(
        [Output("a", "children"), Output("a", "children")], [Input("b", "children")]
    )
    def x(b):
        return b, b

    @app.callback(
        [Output({"a": 1}, "children"), Output({"a": ALL}, "children")],
        [Input("b", "children")],
    )
    def y(b):
        return b, b

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Overlapping wildcard callback outputs",
            [
                'Output 1 ({"a":ALL}.children)',
                'overlaps another output ({"a":1}.children)',
                "used in this callback",
            ],
        ],
        [
            "Duplicate callback Outputs",
            ["Output 1 (a.children) is already used by this callback."],
        ],
    ]
    check_errors(dash_duo, specs)


def test_dvcv004_duplicate_outputs_across_callbacks(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="a"), html.Div(id="b"), html.Div(id="c")])

    @app.callback(
        [Output("a", "children"), Output("a", "style")], [Input("b", "children")]
    )
    def x(b):
        return b, b

    @app.callback(Output("b", "children"), [Input("b", "style")])
    def y(b):
        return b

    @app.callback(Output("a", "children"), [Input("b", "children")])
    def x2(b):
        return b

    @app.callback(
        [Output("b", "children"), Output("b", "style")], [Input("c", "children")]
    )
    def y2(c):
        return c

    @app.callback(
        [Output({"a": 1}, "children"), Output({"b": ALL, "c": 1}, "children")],
        [Input("b", "children")],
    )
    def z(b):
        return b, b

    @app.callback(
        [Output({"a": ALL}, "children"), Output({"b": 1, "c": ALL}, "children")],
        [Input("b", "children")],
    )
    def z2(b):
        return b, b

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Overlapping wildcard callback outputs",
            [
                # depending on the order callbacks get reported to the
                # front end, either of these could have been registered first.
                # so we use this oder-independent form that just checks for
                # both prop_id's and the string "overlaps another output"
                '({"b":1,"c":ALL}.children)',
                "overlaps another output",
                '({"b":ALL,"c":1}.children)',
                "used in a different callback.",
            ],
        ],
        [
            "Overlapping wildcard callback outputs",
            [
                '({"a":ALL}.children)',
                "overlaps another output",
                '({"a":1}.children)',
                "used in a different callback.",
            ],
        ],
        ["Duplicate callback outputs", ["Output 0 (b.children) is already in use."]],
        ["Duplicate callback outputs", ["Output 0 (a.children) is already in use."]],
    ]
    check_errors(dash_duo, specs)


def test_dvcv005_input_output_overlap(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([html.Div(id="a"), html.Div(id="b"), html.Div(id="c")])

    @app.callback(Output("a", "children"), [Input("a", "children")])
    def x(a):
        return a

    @app.callback(
        [Output("b", "children"), Output("c", "children")], [Input("c", "children")]
    )
    def y(c):
        return c, c

    @app.callback(Output({"a": ALL}, "children"), [Input({"a": 1}, "children")])
    def x2(a):
        return [a]

    @app.callback(
        [Output({"b": MATCH}, "children"), Output({"b": MATCH, "c": 1}, "children")],
        [Input({"b": MATCH, "c": 1}, "children")],
    )
    def y2(c):
        return c, c

    dash_duo.start_server(app, **debugging)

    # input/output overlap is now legal, shouldn't throw any errors
    wait.until(lambda: ~dash_duo.redux_state_is_loading, 2)
    assert dash_duo.get_logs() == []


def test_dvcv006_inconsistent_wildcards(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div()

    @app.callback(
        [Output({"b": MATCH}, "children"), Output({"b": ALL, "c": 1}, "children")],
        [Input({"b": MATCH, "c": 2}, "children")],
    )
    def x(c):
        return c, [c]

    @app.callback(
        [Output({"a": MATCH}, "children")],
        [Input({"b": MATCH}, "children"), Input({"c": ALLSMALLER}, "children")],
        [State({"d": MATCH, "dd": MATCH}, "children"), State({"e": ALL}, "children")],
    )
    def y(b, c, d, e):
        return b + c + d + e

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "`Input` / `State` wildcards not in `Output`s",
            [
                'State 0 ({"d":MATCH,"dd":MATCH}.children)',
                "has MATCH or ALLSMALLER on key(s) d, dd",
                'where Output 0 ({"a":MATCH}.children)',
            ],
        ],
        [
            "`Input` / `State` wildcards not in `Output`s",
            [
                'Input 1 ({"c":ALLSMALLER}.children)',
                "has MATCH or ALLSMALLER on key(s) c",
                'where Output 0 ({"a":MATCH}.children)',
            ],
        ],
        [
            "`Input` / `State` wildcards not in `Output`s",
            [
                'Input 0 ({"b":MATCH}.children)',
                "has MATCH or ALLSMALLER on key(s) b",
                'where Output 0 ({"a":MATCH}.children)',
            ],
        ],
        [
            "Mismatched `MATCH` wildcards across `Output`s",
            [
                'Output 1 ({"b":ALL,"c":1}.children)',
                "does not have MATCH wildcards on the same keys as",
                'Output 0 ({"b":MATCH}.children).',
            ],
        ],
    ]
    check_errors(dash_duo, specs)


def test_dvcv007_disallowed_ids(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div()

    @app.callback(
        Output({"": 1, "a": [4], "c": ALLSMALLER}, "children"),
        [Input({"b": {"c": 1}}, "children")],
    )
    def y(b):
        return b

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Callback wildcard ID error",
            [
                'Input[0].id["b"] = {"c":1}',
                "Wildcard callback ID values must be either wildcards",
                "or constants of one of these types:",
                "string, number, boolean",
            ],
        ],
        [
            "Callback wildcard ID error",
            [
                'Output[0].id["c"] = ALLSMALLER',
                "Allowed wildcards for Outputs are:",
                "ALL, MATCH",
            ],
        ],
        [
            "Callback wildcard ID error",
            [
                'Output[0].id["a"] = [4]',
                "Wildcard callback ID values must be either wildcards",
                "or constants of one of these types:",
                "string, number, boolean",
            ],
        ],
        [
            "Callback wildcard ID error",
            ['Output[0].id has key ""', "Keys must be non-empty strings."],
        ],
    ]
    check_errors(dash_duo, specs)


def bad_id_app(**kwargs):
    app = Dash(__name__, **kwargs)
    app.layout = html.Div(
        [
            html.Div(
                [html.Div(id="inner-div"), dcc.Input(id="inner-input")], id="outer-div"
            ),
            dcc.Input(id="outer-input"),
        ],
        id="main",
    )

    @app.callback(Output("nuh-uh", "children"), [Input("inner-input", "value")])
    def f(a):
        return a

    @app.callback(Output("outer-input", "value"), [Input("yeah-no", "value")])
    def g(a):
        return a

    @app.callback(
        [Output("inner-div", "children"), Output("nope", "children")],
        [Input("inner-input", "value")],
        [State("what", "children")],
    )
    def g2(a):
        return [a, a]

    # the right way
    @app.callback(Output("inner-div", "style"), [Input("inner-input", "value")])
    def h(a):
        return a

    return app


# This one is raised by bad_id_app whether suppressing callback exceptions or not
# yeah-no no longer raises an error on dispatch due to the no-input regression fix
# for issue #1200
dispatch_specs = [
    [
        "A nonexistent object was used in an `Output` of a Dash callback. "
        "The id of this object is `nope` and the property is `children`. "
        "The string ids in the current layout are: "
        "[main, outer-div, inner-div, inner-input, outer-input]",
        [],
    ],
]


def test_dvcv008_wrong_callback_id(dash_duo):
    dash_duo.start_server(bad_id_app(), **debugging)

    specs = [
        [
            "ID not found in layout",
            [
                "Attempting to connect a callback Input item to component:",
                '"yeah-no"',
                "but no components with that id exist in the layout.",
                "If you are assigning callbacks to components that are",
                "generated by other callbacks (and therefore not in the",
                "initial layout), you can suppress this exception by setting",
                "`suppress_callback_exceptions=True`.",
                "This ID was used in the callback(s) for Output(s):",
                "outer-input.value",
            ],
        ],
        [
            "ID not found in layout",
            [
                "Attempting to connect a callback Output item to component:",
                '"nope"',
                "but no components with that id exist in the layout.",
                "This ID was used in the callback(s) for Output(s):",
                "inner-div.children, nope.children",
            ],
        ],
        [
            "ID not found in layout",
            [
                "Attempting to connect a callback State item to component:",
                '"what"',
                "but no components with that id exist in the layout.",
                "This ID was used in the callback(s) for Output(s):",
                "inner-div.children, nope.children",
            ],
        ],
        [
            "ID not found in layout",
            [
                "Attempting to connect a callback Output item to component:",
                '"nuh-uh"',
                "but no components with that id exist in the layout.",
                "This ID was used in the callback(s) for Output(s):",
                "nuh-uh.children",
            ],
        ],
    ]
    check_errors(dash_duo, dispatch_specs + specs)


def test_dvcv009_suppress_callback_exceptions(dash_duo):
    dash_duo.start_server(bad_id_app(suppress_callback_exceptions=True), **debugging)

    check_errors(dash_duo, dispatch_specs)


def test_dvcv010_bad_props(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(
                [html.Div(id="inner-div"), dcc.Input(id="inner-input")], id="outer-div"
            ),
            dcc.Input(id={"a": 1}),
        ],
        id="main",
    )

    @app.callback(
        Output("inner-div", "xyz"),
        # "data-xyz" is OK, does not give an error
        [Input("inner-input", "pdq"), Input("inner-div", "data-xyz")],
        [State("inner-div", "value")],
    )
    def xyz(a, b, c):
        a if b else c

    @app.callback(
        Output({"a": MATCH}, "no"),
        [Input({"a": MATCH}, "never")],
        # "boo" will not error because we don't check State MATCH/ALLSMALLER
        [State({"a": MATCH}, "boo"), State({"a": ALL}, "nope")],
    )
    def f(a, b, c):
        return a if b else c

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Invalid prop for this component",
            [
                'Property "never" was used with component ID:',
                '{"a":1}',
                "in one of the Input items of a callback.",
                "This ID is assigned to a dash_core_components.Input component",
                "in the layout, which does not support this property.",
                "This ID was used in the callback(s) for Output(s):",
                '{"a":MATCH}.no',
            ],
        ],
        [
            "Invalid prop for this component",
            [
                'Property "nope" was used with component ID:',
                '{"a":1}',
                "in one of the State items of a callback.",
                "This ID is assigned to a dash_core_components.Input component",
                '{"a":MATCH}.no',
            ],
        ],
        [
            "Invalid prop for this component",
            [
                'Property "no" was used with component ID:',
                '{"a":1}',
                "in one of the Output items of a callback.",
                "This ID is assigned to a dash_core_components.Input component",
                '{"a":MATCH}.no',
            ],
        ],
        [
            "Invalid prop for this component",
            [
                'Property "pdq" was used with component ID:',
                '"inner-input"',
                "in one of the Input items of a callback.",
                "This ID is assigned to a dash_core_components.Input component",
                "inner-div.xyz",
            ],
        ],
        [
            "Invalid prop for this component",
            [
                'Property "value" was used with component ID:',
                '"inner-div"',
                "in one of the State items of a callback.",
                "This ID is assigned to a dash_html_components.Div component",
                "inner-div.xyz",
            ],
        ],
        [
            "Invalid prop for this component",
            [
                'Property "xyz" was used with component ID:',
                '"inner-div"',
                "in one of the Output items of a callback.",
                "This ID is assigned to a dash_html_components.Div component",
                "inner-div.xyz",
            ],
        ],
    ]
    check_errors(dash_duo, specs)


def test_dvcv011_duplicate_outputs_simple(dash_duo):
    app = Dash(__name__)

    @app.callback(Output("a", "children"), [Input("c", "children")])
    def c(children):
        return children

    @app.callback(Output("a", "children"), [Input("b", "children")])
    def c2(children):
        return children

    @app.callback([Output("a", "style")], [Input("c", "style")])
    def s(children):
        return (children,)

    @app.callback([Output("a", "style")], [Input("b", "style")])
    def s2(children):
        return (children,)

    app.layout = html.Div(
        [
            html.Div([], id="a"),
            html.Div(["Bye"], id="b", style={"color": "red"}),
            html.Div(["Hello"], id="c", style={"color": "green"}),
        ]
    )

    dash_duo.start_server(app, **debugging)

    specs = [
        ["Duplicate callback outputs", ["Output 0 (a.children) is already in use."]],
        ["Duplicate callback outputs", ["Output 0 (a.style) is already in use."]],
    ]
    check_errors(dash_duo, specs)


def test_dvcv012_circular_2_step(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [html.Div([], id="a"), html.Div(["Bye"], id="b"), html.Div(["Hello"], id="c")]
    )

    @app.callback(Output("a", "children"), [Input("b", "children")])
    def callback(children):
        return children

    @app.callback(Output("b", "children"), [Input("a", "children")])
    def c2(children):
        return children

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Circular Dependencies",
            [
                "Dependency Cycle Found:",
                "a.children -> b.children",
                "b.children -> a.children",
            ],
        ]
    ]
    check_errors(dash_duo, specs)


def test_dvcv013_circular_3_step(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [html.Div([], id="a"), html.Div(["Bye"], id="b"), html.Div(["Hello"], id="c")]
    )

    @app.callback(Output("b", "children"), [Input("a", "children")])
    def callback(children):
        return children

    @app.callback(Output("c", "children"), [Input("b", "children")])
    def c2(children):
        return children

    @app.callback([Output("a", "children")], [Input("c", "children")])
    def c3(children):
        return (children,)

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Circular Dependencies",
            [
                "Dependency Cycle Found:",
                "a.children -> b.children",
                "b.children -> c.children",
                "c.children -> a.children",
            ],
        ]
    ]
    check_errors(dash_duo, specs)


def multipage_app(validation=False):
    app = Dash(__name__, suppress_callback_exceptions=(validation == "suppress"))

    skeleton = html.Div(
        [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
    )

    layout_index = html.Div(
        [
            dcc.Link('Navigate to "/page-1"', id="index_p1", href="/page-1"),
            dcc.Link('Navigate to "/page-2"', id="index_p2", href="/page-2"),
        ]
    )

    layout_page_1 = html.Div(
        [
            html.H2("Page 1"),
            dcc.Input(id="input-1-state", type="text", value="Montreal"),
            dcc.Input(id="input-2-state", type="text", value="Canada"),
            html.Button(id="submit-button", n_clicks=0, children="Submit"),
            html.Div(id="output-state"),
            html.Br(),
            dcc.Link('Navigate to "/"', id="p1_index", href="/"),
            dcc.Link('Navigate to "/page-2"', id="p1_p2", href="/page-2"),
        ]
    )

    layout_page_2 = html.Div(
        [
            html.H2("Page 2"),
            dcc.Input(id="page-2-input", value="LA"),
            html.Div(id="page-2-display-value"),
            html.Br(),
            dcc.Link('Navigate to "/"', id="p2_index", href="/"),
            dcc.Link('Navigate to "/page-1"', id="p2_p1", href="/page-1"),
        ]
    )

    validation_layout = html.Div([skeleton, layout_index, layout_page_1, layout_page_2])

    def validation_function():
        return skeleton if flask.has_request_context() else validation_layout

    app.layout = validation_function if validation == "function" else skeleton
    if validation == "attribute":
        app.validation_layout = validation_layout

    # Index callbacks
    @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    def display_page(pathname):
        if pathname == "/page-1":
            return layout_page_1
        elif pathname == "/page-2":
            return layout_page_2
        else:
            return layout_index

    # Page 1 callbacks
    @app.callback(
        Output("output-state", "children"),
        [Input("submit-button", "n_clicks")],
        [State("input-1-state", "value"), State("input-2-state", "value")],
    )
    def update_output(n_clicks, input1, input2):
        return (
            "The Button has been pressed {} times,"
            'Input 1 is "{}",'
            'and Input 2 is "{}"'
        ).format(n_clicks, input1, input2)

    # Page 2 callbacks
    @app.callback(
        Output("page-2-display-value", "children"), [Input("page-2-input", "value")]
    )
    def display_value(value):
        print("display_value")
        return 'You have selected "{}"'.format(value)

    return app


def test_dvcv014_multipage_errors(dash_duo):
    app = multipage_app()
    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "ID not found in layout",
            ['"page-2-input"', "page-2-display-value.children"],
        ],
        ["ID not found in layout", ['"submit-button"', "output-state.children"]],
        [
            "ID not found in layout",
            ['"page-2-display-value"', "page-2-display-value.children"],
        ],
        ["ID not found in layout", ['"output-state"', "output-state.children"]],
    ]
    check_errors(dash_duo, specs)


@pytest.mark.parametrize("validation", ("function", "attribute", "suppress"))
def test_dvcv015_multipage_validation_layout(validation, dash_duo):
    app = multipage_app(validation)
    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal("#index_p1", 'Navigate to "/page-1"')
    dash_duo.find_element("#index_p1").click()

    dash_duo.find_element("#submit-button").click()
    dash_duo.wait_for_text_to_equal(
        "#output-state",
        "The Button has been pressed 1 times,"
        'Input 1 is "Montreal",and Input 2 is "Canada"',
    )

    dash_duo.find_element("#p1_p2").click()
    dash_duo.wait_for_text_to_equal("#page-2-display-value", 'You have selected "LA"')

    assert not dash_duo.get_logs()


def test_dvcv016_circular_with_input_output(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [html.Div([], id="a"), html.Div(["Bye"], id="b"), html.Div(["Hello"], id="c")]
    )

    @app.callback(
        [Output("a", "children"), Output("b", "children")],
        [Input("a", "children"), Input("b", "children"), Input("c", "children")],
    )
    def c1(a, b, c):
        return a, b

    @app.callback(Output("c", "children"), [Input("a", "children")])
    def c2(children):
        return children

    dash_duo.start_server(app, **debugging)

    specs = [
        [
            "Circular Dependencies",
            [
                "Dependency Cycle Found:",
                "a.children__output -> c.children",
                "c.children -> a.children__output",
            ],
        ]
    ]
    check_errors(dash_duo, specs)
