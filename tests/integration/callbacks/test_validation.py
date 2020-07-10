import pytest

import dash_html_components as html

from dash import Dash

from dash.dependencies import Input, Output, State
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

    with pytest.raises(IncorrectTypeException):

        @app.callback([[Output("out1", "children")]], [Input("in1", "children")])
        def f(i):
            return i

        pytest.fail("extra output nesting")

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
    def f2(i):
        return i

    # all OK with lists
    @app.callback(
        [Output("out3", "children")],
        [Input("in3", "children")],
        [State("state3", "children")],
    )
    def f3(i):
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

    with pytest.raises(InvalidCallbackReturnValue):
        # outputs_list (normally callback_context.outputs_list) is provided
        # by the dispatcher from the request.
        single("aaa", outputs_list={"id": "b", "property": "children"})
        pytest.fail("not serializable")

    @app.callback(
        [Output("c", "children"), Output("d", "children")], [Input("a", "children")]
    )
    def multi(a):
        return [1, set([2])]

    with pytest.raises(InvalidCallbackReturnValue):
        outputs_list = [
            {"id": "c", "property": "children"},
            {"id": "d", "property": "children"},
        ]
        multi("aaa", outputs_list=outputs_list)
        pytest.fail("nested non-serializable")

    @app.callback(
        [Output("e", "children"), Output("f", "children")], [Input("a", "children")]
    )
    def multi2(a):
        return ["abc"]

    with pytest.raises(InvalidCallbackReturnValue):
        outputs_list = [
            {"id": "e", "property": "children"},
            {"id": "f", "property": "children"},
        ]
        multi2("aaa", outputs_list=outputs_list)
        pytest.fail("wrong-length list")


def test_cbva003_list_single_output(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [html.Div("Hi", id="in"), html.Div(id="out1"), html.Div(id="out2"),]
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
