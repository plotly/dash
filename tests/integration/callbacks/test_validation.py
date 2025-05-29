import pytest

from dash import Dash, Input, Output, State, html
from dash.exceptions import InvalidCallbackReturnValue, IncorrectTypeException


def test_cbva001_callback_dep_types():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div("child", id="in1"),
            html.Div("state", id="state1"),
            html.Div(id="out1"),
            html.Div("child", id="in2"),
            html.Div("state", id="state2"),
            html.Div(id="out2"),
            html.Div("child", id="in3"),
            html.Div("state", id="state3"),
            html.Div(id="out3"),
        ]
    )

    with pytest.raises(IncorrectTypeException) as err:

        @app.callback(Input("in1", "children"), Output("out1", "children"))
        def f2(i):
            return i

        pytest.fail("out-of-order args")

    assert "Outputs first,\nthen all Inputs, then all States." in err.value.args[0]
    assert "<Input `in1.children`>" in err.value.args[0]
    assert "<Output `out1.children`>" in err.value.args[0]

    # all OK with tuples
    @app.callback(
        (Output("out1", "children"),),
        (Input("in1", "children"),),
        (State("state1", "children"),),
    )
    def f1(i):
        return i

    # all OK with all args in single list
    @app.callback(
        Output("out2", "children"),
        Input("in2", "children"),
        State("state2", "children"),
    )
    def f3(i):
        return i

    # all OK with lists
    @app.callback(
        [Output("out3", "children")],
        [Input("in3", "children")],
        [State("state3", "children")],
    )
    def f4(i):
        return i


def test_cbva002_callback_return_validation():
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div(id="a"),
            html.Div(id="b"),
            html.Div(id="c"),
            html.Div(id="d"),
            html.Div(id="e"),
            html.Div(id="f"),
        ]
    )

    @app.callback(Output("b", "children"), [Input("a", "children")])
    def single(a):
        return set([1])

    single_wrapped = app.callback_map["b.children"]["callback"]

    with pytest.raises(InvalidCallbackReturnValue):
        # outputs_list (normally callback_context.outputs_list) is provided
        # by the dispatcher from the request.
        single_wrapped("aaa", outputs_list={"id": "b", "property": "children"})
        pytest.fail("not serializable")

    @app.callback(
        [Output("c", "children"), Output("d", "children")], [Input("a", "children")]
    )
    def multi(a):
        return [1, set([2])]

    multi_wrapped = app.callback_map["..c.children...d.children.."]["callback"]

    with pytest.raises(InvalidCallbackReturnValue):
        outputs_list = [
            {"id": "c", "property": "children"},
            {"id": "d", "property": "children"},
        ]
        multi_wrapped("aaa", outputs_list=outputs_list)
        pytest.fail("nested non-serializable")

    @app.callback(
        [Output("e", "children"), Output("f", "children")], [Input("a", "children")]
    )
    def multi2(a):
        return ["abc"]

    multi2_wrapped = app.callback_map["..e.children...f.children.."]["callback"]

    with pytest.raises(InvalidCallbackReturnValue):
        outputs_list = [
            {"id": "e", "property": "children"},
            {"id": "f", "property": "children"},
        ]
        multi2_wrapped("aaa", outputs_list=outputs_list)
        pytest.fail("wrong-length list")


def test_cbva003_list_single_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Div("Hi", id="in"), html.Div(id="out1"), html.Div(id="out2")]
    )

    @app.callback(Output("out1", "children"), Input("in", "children"))
    def o1(i):
        return "1: " + i

    @app.callback([Output("out2", "children")], [Input("in", "children")])
    def o2(i):
        return ("2: " + i,)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out1", "1: Hi")
    dash_duo.wait_for_text_to_equal("#out2", "2: Hi")


@pytest.mark.parametrize("named_out", [True, False])
@pytest.mark.parametrize("named_in,named_state", [(True, True), (False, False)])
def test_cbva004_named_args(named_out, named_in, named_state, dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div("Hi", id="in"),
            html.Div("gh", id="state"),
            html.Div(id="out1"),
            html.Div(id="out2"),
        ]
    )

    def make_args(*a):
        args = []
        kwargs = {}
        names = ["output", "inputs", "state"]
        flags = [named_out, named_in, named_state]
        for ai, name, flag in zip(a, names, flags):
            if flag:
                kwargs[name] = ai
            else:
                args.append(ai)
        return args, kwargs

    args, kwargs = make_args(
        Output("out1", "children"), Input("in", "children"), State("state", "children")
    )

    @app.callback(*args, **kwargs)
    def o1(i, s):
        return "1: " + i + s

    args, kwargs = make_args(
        [Output("out2", "children")],
        [Input("in", "children")],
        [State("state", "children")],
    )

    @app.callback(*args, **kwargs)
    def o2(i, s):
        return ("2: " + i + s,)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out1", "1: High")
    dash_duo.wait_for_text_to_equal("#out2", "2: High")


def test_cbva005_tuple_args(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Div("Yo", id="in1"),
            html.Div("lo", id="in2"),
            html.Div(id="out1"),
            html.Div(id="out2"),
        ]
    )

    @app.callback(
        Output("out1", "children"), (Input("in1", "children"), Input("in2", "children"))
    )
    def f(i1, i2):
        return "1: " + i1 + i2

    @app.callback(
        (Output("out2", "children"),),
        Input("in1", "children"),
        (State("in2", "children"),),
    )
    def g(i1, i2):
        return ("2: " + i1 + i2,)

    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#out1", "1: Yolo")
    dash_duo.wait_for_text_to_equal("#out2", "2: Yolo")
