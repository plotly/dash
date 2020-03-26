import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State, MATCH, ALL, ALLSMALLER
from dash.testing.wait import until_not

debugging = dict(
    debug=True,
    use_reloader=False,
    use_debugger=True,
    dev_tools_hot_reload=False,
)


def check_error(dash_duo, index, message, snippets):
    # This is not fully general - despite the selectors below, it only applies
    # to front-end errors with no back-end errors in the list.
    # Also the index is as on the page, which is opposite the execution order.

    found_message = dash_duo.find_elements(".dash-fe-error__title")[index].text
    assert found_message == message

    if not snippets:
        return

    dash_duo.find_elements(".test-devtools-error-toggle")[index].click()

    found_text = dash_duo.wait_for_element(".dash-backend-error").text
    for snip in snippets:
        assert snip in found_text

    # hide the error detail again - so only one detail is be visible at a time
    dash_duo.find_elements(".test-devtools-error-toggle")[index].click()
    dash_duo.wait_for_no_elements(".dash-backend-error")


def test_dvcv001_blank(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div()

    @app.callback([], [])
    def x():
        return 42

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "2")

    check_error(dash_duo, 0, "A callback is missing Inputs", [
        "there are no `Input` elements."
    ])
    check_error(dash_duo, 1, "A callback is missing Outputs", [
        "Please provide an output for this callback:"
    ])


def test_dvcv002_blank_id_prop(dash_duo):
    # TODO: remove suppress_callback_exceptions after we move that part to FE
    app = dash.Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div([html.Div(id="a")])

    @app.callback([Output("a", "children"), Output("", "")], [Input("", "")])
    def x(a):
        return a

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "6")

    # the first 2 are just artifacts... the other 4 we care about
    check_error(dash_duo, 0, "Circular Dependencies", [])
    check_error(dash_duo, 1, "Same `Input` and `Output`", [])

    check_error(dash_duo, 2, "Callback item missing ID", [
        'Input[0].id = ""',
        "Every item linked to a callback needs an ID",
    ])
    check_error(dash_duo, 3, "Callback property error", [
        'Input[0].property = ""',
        "expected `property` to be a non-empty string.",
    ])
    check_error(dash_duo, 4, "Callback item missing ID", [
        'Output[1].id = ""',
        "Every item linked to a callback needs an ID",
    ])
    check_error(dash_duo, 5, "Callback property error", [
        'Output[1].property = ""',
        "expected `property` to be a non-empty string.",
    ])


def test_dvcv003_duplicate_outputs_same_callback(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Div(id="a"), html.Div(id="b")])

    @app.callback(
        [Output("a", "children"), Output("a", "children")],
        [Input("b", "children")]
    )
    def x(b):
        return b, b

    @app.callback(
        [Output({"a": 1}, "children"), Output({"a": ALL}, "children")],
        [Input("b", "children")]
    )
    def y(b):
        return b, b

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "2")

    check_error(dash_duo, 0, "Overlapping wildcard callback outputs", [
        'Output 1 ({"a":ALL}.children)',
        'overlaps another output ({"a":1}.children)',
        "used in this callback",
    ])
    check_error(dash_duo, 1, "Duplicate callback Outputs", [
        "Output 1 (a.children) is already used by this callback."
    ])


def test_dvcv004_duplicate_outputs_across_callbacks(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Div(id="a"), html.Div(id="b"), html.Div(id="c")])

    @app.callback(
        [Output("a", "children"), Output("a", "style")],
        [Input("b", "children")]
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
        [Output("b", "children"), Output("b", "style")],
        [Input("c", "children")]
    )
    def y2(c):
        return c

    @app.callback(
        [Output({"a": 1}, "children"), Output({"b": ALL, "c": 1}, "children")],
        [Input("b", "children")]
    )
    def z(b):
        return b, b

    @app.callback(
        [Output({"a": ALL}, "children"), Output({"b": 1, "c": ALL}, "children")],
        [Input("b", "children")]
    )
    def z2(b):
        return b, b

    @app.callback(
        Output({"a": MATCH}, "children"),
        [Input({"a": MATCH, "b": 1}, "children")]
    )
    def z3(ab):
        return ab

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "5")

    check_error(dash_duo, 0, "Overlapping wildcard callback outputs", [
        'Output 0 ({"a":MATCH}.children)',
        'overlaps another output ({"a":1}.children)',
        "used in a different callback.",
    ])

    check_error(dash_duo, 1, "Overlapping wildcard callback outputs", [
        'Output 1 ({"b":1,"c":ALL}.children)',
        'overlaps another output ({"b":ALL,"c":1}.children)',
        "used in a different callback.",
    ])

    check_error(dash_duo, 2, "Overlapping wildcard callback outputs", [
        'Output 0 ({"a":ALL}.children)',
        'overlaps another output ({"a":1}.children)',
        "used in a different callback.",
    ])

    check_error(dash_duo, 3, "Duplicate callback outputs", [
        "Output 0 (b.children) is already in use."
    ])

    check_error(dash_duo, 4, "Duplicate callback outputs", [
        "Output 0 (a.children) is already in use."
    ])


def test_dvcv005_input_output_overlap(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div([html.Div(id="a"), html.Div(id="b"), html.Div(id="c")])

    @app.callback(Output("a", "children"), [Input("a", "children")])
    def x(a):
        return a

    @app.callback(
        [Output("b", "children"), Output("c", "children")],
        [Input("c", "children")]
    )
    def y(c):
        return c, c

    @app.callback(Output({"a": ALL}, "children"), [Input({"a": 1}, "children")])
    def x2(a):
        return [a]

    @app.callback(
        [Output({"b": MATCH}, "children"), Output({"b": MATCH, "c": 1}, "children")],
        [Input({"b": MATCH, "c": 1}, "children")]
    )
    def y2(c):
        return c, c

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "6")

    check_error(dash_duo, 0, "Dependency Cycle Found: a.children -> a.children", [])
    check_error(dash_duo, 1, "Circular Dependencies", [])

    check_error(dash_duo, 2, "Same `Input` and `Output`", [
        'Input 0 ({"b":MATCH,"c":1}.children)',
        "can match the same component(s) as",
        'Output 1 ({"b":MATCH,"c":1}.children)',
    ])

    check_error(dash_duo, 3, "Same `Input` and `Output`", [
        'Input 0 ({"a":1}.children)',
        "can match the same component(s) as",
        'Output 0 ({"a":ALL}.children)',
    ])

    check_error(dash_duo, 4, "Same `Input` and `Output`", [
        "Input 0 (c.children)",
        "matches Output 1 (c.children)",
    ])

    check_error(dash_duo, 5, "Same `Input` and `Output`", [
        "Input 0 (a.children)",
        "matches Output 0 (a.children)",
    ])


def test_dvcv006_inconsistent_wildcards(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div()

    @app.callback(
        [Output({"b": MATCH}, "children"), Output({"b": ALL, "c": 1}, "children")],
        [Input({"b": MATCH, "c": 2}, "children")]
    )
    def x(c):
        return c, [c]

    @app.callback(
        [Output({"a": MATCH}, "children")],
        [Input({"b": MATCH}, "children"), Input({"c": ALLSMALLER}, "children")],
        [State({"d": MATCH, "dd": MATCH}, "children"), State({"e": ALL}, "children")]
    )
    def y(b, c, d, e):
        return b + c + d + e

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "4")

    check_error(dash_duo, 0, "`Input` / `State` wildcards not in `Output`s", [
        'State 0 ({"d":MATCH,"dd":MATCH}.children)',
        "has MATCH or ALLSMALLER on key(s) d, dd",
        'where Output 0 ({"a":MATCH}.children)',
    ])

    check_error(dash_duo, 1, "`Input` / `State` wildcards not in `Output`s", [
        'Input 1 ({"c":ALLSMALLER}.children)',
        "has MATCH or ALLSMALLER on key(s) c",
        'where Output 0 ({"a":MATCH}.children)',
    ])

    check_error(dash_duo, 2, "`Input` / `State` wildcards not in `Output`s", [
        'Input 0 ({"b":MATCH}.children)',
        "has MATCH or ALLSMALLER on key(s) b",
        'where Output 0 ({"a":MATCH}.children)',
    ])

    check_error(dash_duo, 3, "Mismatched `MATCH` wildcards across `Output`s", [
        'Output 1 ({"b":ALL,"c":1}.children)',
        "does not have MATCH wildcards on the same keys as",
        'Output 0 ({"b":MATCH}.children).',
    ])


def test_dvcv007_disallowed_ids(dash_duo):
    app = dash.Dash(__name__)
    app.layout = html.Div()

    @app.callback(
        Output({"": 1, "a": [4], "c": ALLSMALLER}, "children"),
        [Input({"b": {"c": 1}}, "children")]
    )
    def y(b):
        return b

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "4")

    check_error(dash_duo, 0, "Callback wildcard ID error", [
        'Input[0].id["b"] = {"c":1}',
        "Wildcard callback ID values must be either wildcards",
        "or constants of one of these types:",
        "string, number, boolean",
    ])

    check_error(dash_duo, 1, "Callback wildcard ID error", [
        'Output[0].id["c"] = ALLSMALLER',
        "Allowed wildcards for Outputs are:",
        "ALL, MATCH",
    ])

    check_error(dash_duo, 2, "Callback wildcard ID error", [
        'Output[0].id["a"] = [4]',
        "Wildcard callback ID values must be either wildcards",
        "or constants of one of these types:",
        "string, number, boolean",
    ])

    check_error(dash_duo, 3, "Callback wildcard ID error", [
        'Output[0].id has key ""',
        "Keys must be non-empty strings."
    ])


def bad_id_app(**kwargs):
    app = dash.Dash(__name__, **kwargs)
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
        [State("what", "children")]
    )
    def g2(a):
        return [a, a]

    # the right way
    @app.callback(Output("inner-div", "style"), [Input("inner-input", "value")])
    def h(a):
        return a

    return app


def test_dvcv008_wrong_callback_id(dash_duo):
    dash_duo.start_server(bad_id_app(), **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "4")

    check_error(dash_duo, 0, "ID not found in layout", [
        "Attempting to connect a callback Input item to component:",
        '"yeah-no"',
        "but no components with that id exist in the layout.",
        "If you are assigning callbacks to components that are",
        "generated by other callbacks (and therefore not in the",
        "initial layout), you can suppress this exception by setting",
        "`suppress_callback_exceptions=True`.",
        "This ID was used in the callback(s) for Output(s):",
        "outer-input.value"
    ])

    check_error(dash_duo, 1, "ID not found in layout", [
        "Attempting to connect a callback Output item to component:",
        '"nope"',
        "but no components with that id exist in the layout.",
        "This ID was used in the callback(s) for Output(s):",
        "inner-div.children, nope.children"
    ])

    check_error(dash_duo, 2, "ID not found in layout", [
        "Attempting to connect a callback State item to component:",
        '"what"',
        "but no components with that id exist in the layout.",
        "This ID was used in the callback(s) for Output(s):",
        "inner-div.children, nope.children"
    ])

    check_error(dash_duo, 3, "ID not found in layout", [
        "Attempting to connect a callback Output item to component:",
        '"nuh-uh"',
        "but no components with that id exist in the layout.",
        "This ID was used in the callback(s) for Output(s):",
        "nuh-uh.children"
    ])


def test_dvcv009_suppress_callback_exceptions(dash_duo):
    dash_duo.start_server(bad_id_app(suppress_callback_exceptions=True), **debugging)

    dash_duo.find_element('.dash-debug-menu')
    dash_duo.wait_for_no_elements('.test-devtools-error-count')


def test_dvcv010_bad_props(dash_duo):
    app = dash.Dash(__name__)
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
        [State("inner-div", "value")]
    )
    def xyz(a, b, c):
        a if b else c

    @app.callback(
        Output({"a": MATCH}, "no"),
        [Input({"a": MATCH}, "never")],
        # "boo" will not error because we don't check State MATCH/ALLSMALLER
        [State({"a": MATCH}, "boo"), State({"a": ALL}, "nope")]
    )
    def f(a, b, c):
        return a if b else c

    dash_duo.start_server(app, **debugging)

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "6")

    check_error(dash_duo, 0, "Invalid prop for this component", [
        'Property "never" was used with component ID:',
        '{"a":1}',
        "in one of the Input items of a callback.",
        "This ID is assigned to a dash_core_components.Input component",
        "in the layout, which does not support this property.",
        "This ID was used in the callback(s) for Output(s):",
        '{"a":MATCH}.no'
    ])

    check_error(dash_duo, 1, "Invalid prop for this component", [
        'Property "nope" was used with component ID:',
        '{"a":1}',
        "in one of the State items of a callback.",
        "This ID is assigned to a dash_core_components.Input component",
        '{"a":MATCH}.no'
    ])

    check_error(dash_duo, 2, "Invalid prop for this component", [
        'Property "no" was used with component ID:',
        '{"a":1}',
        "in one of the Output items of a callback.",
        "This ID is assigned to a dash_core_components.Input component",
        '{"a":MATCH}.no'
    ])

    check_error(dash_duo, 3, "Invalid prop for this component", [
        'Property "pdq" was used with component ID:',
        '"inner-input"',
        "in one of the Input items of a callback.",
        "This ID is assigned to a dash_core_components.Input component",
        "inner-div.xyz"
    ])

    check_error(dash_duo, 4, "Invalid prop for this component", [
        'Property "value" was used with component ID:',
        '"inner-div"',
        "in one of the State items of a callback.",
        "This ID is assigned to a dash_html_components.Div component",
        "inner-div.xyz"
    ])

    check_error(dash_duo, 5, "Invalid prop for this component", [
        'Property "xyz" was used with component ID:',
        '"inner-div"',
        "in one of the Output items of a callback.",
        "This ID is assigned to a dash_html_components.Div component",
        "inner-div.xyz"
    ])
