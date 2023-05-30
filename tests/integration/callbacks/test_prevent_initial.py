import json
import pytest
from flaky import flaky

from dash import Dash, Input, Output, MATCH, html
from dash.exceptions import PreventUpdate

# parametrize all the tests, but no need to do all 8 combinations, 5 is enough!
flavors = [
    {"clientside": False, "content": False, "global": False},
    {"clientside": True, "content": False, "global": False},
    {"clientside": False, "content": True, "global": False},
    {"clientside": True, "content": True, "global": True},
    {"clientside": False, "content": False, "global": True},
]


def make_app(flavor):
    kwargs = {}
    if flavor["global"]:
        kwargs["prevent_initial_callbacks"] = True
    return Dash(__name__, **kwargs)


def content_callback(app, flavor, layout):
    kwargs = {}
    if flavor["global"]:
        kwargs["prevent_initial_call"] = False

    if flavor["content"]:
        app.layout = html.Div(id="content")

        @app.callback(
            Output("content", "children"), [Input("content", "style")], **kwargs
        )
        def set_content(_):
            return layout

    else:
        app.layout = layout


def const_callback(app, flavor, val, outputs, inputs, prevent_initial_call=False):
    kwargs = {}
    if prevent_initial_call != flavor["global"]:
        kwargs["prevent_initial_call"] = prevent_initial_call

    if flavor["clientside"]:
        vstr = json.dumps(val)
        app.clientside_callback(
            "function() { return " + vstr + "; }", outputs, inputs, **kwargs
        )
    else:

        @app.callback(outputs, inputs, **kwargs)
        def f(*args):
            return val


def concat_callback(app, flavor, outputs, inputs, prevent_initial_call=False):
    kwargs = {}
    if prevent_initial_call != flavor["global"]:
        kwargs["prevent_initial_call"] = prevent_initial_call

    multi_out = isinstance(outputs, (list, tuple))

    if flavor["clientside"]:
        app.clientside_callback(
            """
            function() {
                var out = '';
                for(var i = 0; i < arguments.length; i++) {
                    out += String(arguments[i]);
                }
                return X;
            }
            """.replace(
                "X",
                ("[" + ",".join(["out"] * len(outputs)) + "]") if multi_out else "out",
            ),
            outputs,
            inputs,
            **kwargs
        )
    else:

        @app.callback(outputs, inputs, **kwargs)
        def f(*args):
            out = "".join(str(arg) for arg in args)
            return [out] * len(outputs) if multi_out else out


@pytest.mark.parametrize("flavor", flavors)
def test_cbpi001_prevent_initial_call(flavor, dash_duo):
    app = make_app(flavor)

    layout = html.Div(
        [
            html.Button("click", id="btn"),
            html.Div("A", id="a"),
            html.Div("B", id="b"),
            html.Div("C", id="c"),
            html.Div("D", id="d"),
            html.Div("E", id="e"),
            html.Div("F", id="f"),
        ]
    )
    content_callback(app, flavor, layout)

    # Prevented, so A will only change after the button is clicked
    const_callback(
        app,
        flavor,
        "Click",
        Output("a", "children"),
        [Input("btn", "n_clicks")],
        prevent_initial_call=True,
    )

    # B depends on A - this *will* run, because prevent_initial_call is
    # not equivalent to PreventUpdate within the callback, it's treated as if
    # that callback was never in the initialization chain.
    concat_callback(app, flavor, Output("b", "children"), [Input("a", "children")])

    # C matches B except that it also has prevent_initial_call itself, not just
    # its input A - so it will not run initially
    concat_callback(
        app,
        flavor,
        Output("c", "children"),
        [Input("a", "children")],
        prevent_initial_call=True,
    )

    @app.callback(Output("d", "children"), [Input("d", "style")])
    def d(_):
        raise PreventUpdate

    # E depends on A and D - one prevent_initial_call and one PreventUpdate
    # the prevent_initial_call means it *will* run
    concat_callback(
        app,
        flavor,
        Output("e", "children"),
        [Input("a", "children"), Input("d", "children")],
    )

    # F has prevent_initial_call but DOES fire during init, because one of its
    # inputs (B) was changed by a callback
    concat_callback(
        app,
        flavor,
        Output("f", "children"),
        [Input("a", "children"), Input("b", "children"), Input("d", "children")],
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    # check from the end, to ensure the callbacks are all done
    dash_duo.wait_for_text_to_equal("#f", "AAD")
    dash_duo.wait_for_text_to_equal("#e", "AD"),
    dash_duo.wait_for_text_to_equal("#d", "D")
    dash_duo.wait_for_text_to_equal("#c", "C")
    dash_duo.wait_for_text_to_equal("#b", "A")
    dash_duo.wait_for_text_to_equal("#a", "A")

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#f", "ClickClickD")
    dash_duo.wait_for_text_to_equal("#e", "ClickD"),
    dash_duo.wait_for_text_to_equal("#d", "D")
    dash_duo.wait_for_text_to_equal("#c", "Click")
    dash_duo.wait_for_text_to_equal("#b", "Click")
    dash_duo.wait_for_text_to_equal("#a", "Click")


@flaky(max_runs=3)
@pytest.mark.parametrize("flavor", flavors)
def test_cbpi002_pattern_matching(flavor, dash_duo):
    # a clone of cbpi001 just throwing it through the pattern-matching machinery
    app = make_app(flavor)

    layout = html.Div(
        [
            html.Button("click", id={"i": 0, "j": "btn"}, className="btn"),
            html.Div("A", id={"i": 0, "j": "a"}, className="a"),
            html.Div("B", id={"i": 0, "j": "b"}, className="b"),
            html.Div("C", id={"i": 0, "j": "c"}, className="c"),
            html.Div("D", id={"i": 0, "j": "d"}, className="d"),
            html.Div("E", id={"i": 0, "j": "e"}, className="e"),
            html.Div("F", id={"i": 0, "j": "f"}, className="f"),
        ]
    )
    content_callback(app, flavor, layout)

    const_callback(
        app,
        flavor,
        "Click",
        Output({"i": MATCH, "j": "a"}, "children"),
        [Input({"i": MATCH, "j": "btn"}, "n_clicks")],
        prevent_initial_call=True,
    )

    concat_callback(
        app,
        flavor,
        Output({"i": MATCH, "j": "b"}, "children"),
        [Input({"i": MATCH, "j": "a"}, "children")],
    )

    concat_callback(
        app,
        flavor,
        Output({"i": MATCH, "j": "c"}, "children"),
        [Input({"i": MATCH, "j": "a"}, "children")],
        prevent_initial_call=True,
    )

    @app.callback(
        Output({"i": MATCH, "j": "d"}, "children"),
        [Input({"i": MATCH, "j": "d"}, "style")],
    )
    def d(_):
        raise PreventUpdate

    concat_callback(
        app,
        flavor,
        Output({"i": MATCH, "j": "e"}, "children"),
        [
            Input({"i": MATCH, "j": "a"}, "children"),
            Input({"i": MATCH, "j": "d"}, "children"),
        ],
    )

    concat_callback(
        app,
        flavor,
        Output({"i": MATCH, "j": "f"}, "children"),
        [
            Input({"i": MATCH, "j": "a"}, "children"),
            Input({"i": MATCH, "j": "b"}, "children"),
            Input({"i": MATCH, "j": "d"}, "children"),
        ],
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    # check from the end, to ensure the callbacks are all done
    dash_duo.wait_for_text_to_equal(".f", "AAD")
    dash_duo.wait_for_text_to_equal(".e", "AD"),
    dash_duo.wait_for_text_to_equal(".d", "D")
    dash_duo.wait_for_text_to_equal(".c", "C")
    dash_duo.wait_for_text_to_equal(".b", "A")
    dash_duo.wait_for_text_to_equal(".a", "A")

    dash_duo.find_element(".btn").click()

    dash_duo.wait_for_text_to_equal(".f", "ClickClickD")
    dash_duo.wait_for_text_to_equal(".e", "ClickD"),
    dash_duo.wait_for_text_to_equal(".d", "D")
    dash_duo.wait_for_text_to_equal(".c", "Click")
    dash_duo.wait_for_text_to_equal(".b", "Click")
    dash_duo.wait_for_text_to_equal(".a", "Click")


@pytest.mark.parametrize("flavor", flavors)
def test_cbpi003_multi_outputs(flavor, dash_duo):
    app = make_app(flavor)

    layout = html.Div(
        [
            html.Button("click", id="btn"),
            html.Div("A", id="a"),
            html.Div("B", id="b"),
            html.Div("C", id="c"),
            html.Div("D", id="d"),
            html.Div("E", id="e"),
            html.Div("F", id="f"),
            html.Div("G", id="g"),
        ]
    )

    content_callback(app, flavor, layout)

    const_callback(
        app,
        flavor,
        ["Blue", "Cheese"],
        [Output("a", "children"), Output("b", "children")],
        [Input("btn", "n_clicks")],
        prevent_initial_call=True,
    )

    concat_callback(
        app,
        flavor,
        [Output("c", "children"), Output("d", "children")],
        [Input("a", "children"), Input("b", "children")],
        prevent_initial_call=True,
    )

    concat_callback(
        app,
        flavor,
        [Output("e", "children"), Output("f", "children")],
        [Input("a", "children")],
        prevent_initial_call=True,
    )

    # this is the only one that should run initially
    concat_callback(app, flavor, Output("g", "children"), [Input("f", "children")])

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#g", "F")
    dash_duo.wait_for_text_to_equal("#f", "F")
    dash_duo.wait_for_text_to_equal("#e", "E")
    dash_duo.wait_for_text_to_equal("#d", "D")
    dash_duo.wait_for_text_to_equal("#c", "C")
    dash_duo.wait_for_text_to_equal("#b", "B")
    dash_duo.wait_for_text_to_equal("#a", "A")

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#g", "Blue")
    dash_duo.wait_for_text_to_equal("#f", "Blue")
    dash_duo.wait_for_text_to_equal("#e", "Blue")
    dash_duo.wait_for_text_to_equal("#d", "BlueCheese")
    dash_duo.wait_for_text_to_equal("#c", "BlueCheese")
    dash_duo.wait_for_text_to_equal("#b", "Cheese")
    dash_duo.wait_for_text_to_equal("#a", "Blue")


def test_cbpi004_positional_arg(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div([html.Button("click", id="btn"), html.Div(id="out")])

    @app.callback(Output("out", "children"), Input("btn", "n_clicks"), True)
    def f(n):
        return n

    dash_duo.start_server(app)
    dash_duo._wait_for_callbacks()

    dash_duo.wait_for_text_to_equal("#out", "")

    dash_duo.find_element("#btn").click()

    dash_duo.wait_for_text_to_equal("#out", "1")
