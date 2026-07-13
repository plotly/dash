# -*- coding: UTF-8 -*-
from dash import Dash, Input, Output, State, html, dcc
from dash.dependencies import ALL


def test_clsg001_grouped_dict_inputs_outputs(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="first", value="one"),
            dcc.Input(id="second", value="two"),
            html.Div(id="out-a"),
            html.Div(id="out-b"),
        ]
    )

    app.clientside_callback(
        """
        function({a, b}) {
            return {x: `a=${a}`, y: `b=${b}`};
        }
        """,
        output=dict(x=Output("out-a", "children"), y=Output("out-b", "children")),
        inputs=dict(a=Input("first", "value"), b=Input("second", "value")),
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out-a", "a=one")
    dash_duo.wait_for_text_to_equal("#out-b", "b=two")

    dash_duo.find_element("#first").send_keys("!")
    dash_duo.wait_for_text_to_equal("#out-a", "a=one!")
    dash_duo.wait_for_text_to_equal("#out-b", "b=two")

    assert dash_duo.get_logs() == []


def test_clsg002_grouped_nested_list_positional_args(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="x", value="1"),
            dcc.Input(id="y", value="2"),
            dcc.Input(id="z", value="3"),
            html.Div(id="out"),
        ]
    )

    app.clientside_callback(
        """
        function(pair, third) {
            return `${pair[0]}-${pair[1]}-${third}`;
        }
        """,
        output=Output("out", "children"),
        inputs=[[Input("x", "value"), Input("y", "value")], Input("z", "value")],
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "1-2-3")

    dash_duo.find_element("#y").send_keys("0")
    dash_duo.wait_for_text_to_equal("#out", "1-20-3")

    assert dash_duo.get_logs() == []


def test_clsg003_grouped_mixed_input_state(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="in-a", value="a0"),
            dcc.Input(id="state-s", value="s0"),
            dcc.Input(id="in-b", value="b0"),
            html.Div(id="out"),
        ]
    )

    # Dict mixing Input and State: index remapping must put each value under
    # the right name regardless of Input/State declaration order.
    app.clientside_callback(
        """
        function({a, s, b}) {
            return `a=${a} s=${s} b=${b}`;
        }
        """,
        output=Output("out", "children"),
        inputs=dict(
            a=Input("in-a", "value"),
            s=State("state-s", "value"),
            b=Input("in-b", "value"),
        ),
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "a=a0 s=s0 b=b0")

    # Changing state alone must not fire; changing an input picks up new state
    dash_duo.find_element("#state-s").send_keys("!")
    dash_duo.find_element("#in-b").send_keys("!")
    dash_duo.wait_for_text_to_equal("#out", "a=a0 s=s0! b=b0!")

    assert dash_duo.get_logs() == []


def test_clsg004_grouped_no_update(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("update both", id="both"),
            html.Button("skip second", id="skip-b"),
            html.Button("skip all", id="skip-all"),
            html.Div(id="out-a", children="init-a"),
            html.Div(id="out-b", children="init-b"),
        ]
    )

    app.clientside_callback(
        """
        function({both, skipb, skipall}) {
            const no_update = window.dash_clientside.no_update;
            const trig = window.dash_clientside.callback_context.triggered_id;
            if (trig === "skip-all") {
                return no_update;
            }
            if (trig === "skip-b") {
                return {x: `skipb-${skipb}`, y: no_update};
            }
            return {x: `both-${both}`, y: `both-${both}`};
        }
        """,
        output=dict(x=Output("out-a", "children"), y=Output("out-b", "children")),
        inputs=dict(
            both=Input("both", "n_clicks"),
            skipb=Input("skip-b", "n_clicks"),
            skipall=Input("skip-all", "n_clicks"),
        ),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#both").click()
    dash_duo.wait_for_text_to_equal("#out-a", "both-1")
    dash_duo.wait_for_text_to_equal("#out-b", "both-1")

    # per-leaf no_update: out-b keeps its previous value
    dash_duo.find_element("#skip-b").click()
    dash_duo.wait_for_text_to_equal("#out-a", "skipb-1")
    dash_duo.wait_for_text_to_equal("#out-b", "both-1")

    # whole-return no_update: neither output changes; prove the callback ran
    # by clicking "both" afterwards and seeing the next update come through
    dash_duo.find_element("#skip-all").click()
    dash_duo.find_element("#both").click()
    dash_duo.wait_for_text_to_equal("#out-a", "both-2")
    dash_duo.wait_for_text_to_equal("#out-b", "both-2")

    assert dash_duo.get_logs() == []


def test_clsg005_grouped_wildcard_all_leaf(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id={"type": "many", "idx": 0}, value="p"),
            dcc.Input(id={"type": "many", "idx": 1}, value="q"),
            dcc.Input(id="single", value="r"),
            html.Div(id="out"),
        ]
    )

    app.clientside_callback(
        """
        function({many, single}) {
            return `${many.join("+")}|${single}`;
        }
        """,
        output=Output("out", "children"),
        inputs=dict(
            many=Input({"type": "many", "idx": ALL}, "value"),
            single=Input("single", "value"),
        ),
    )

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#out", "p+q|r")

    dash_duo.find_element("#single").send_keys("!")
    dash_duo.wait_for_text_to_equal("#out", "p+q|r!")

    assert dash_duo.get_logs() == []


def test_clsg006_grouped_args_grouping_context(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button("go", id="go"),
            dcc.Input(id="other", value="v0"),
            html.Div(id="out"),
        ]
    )

    app.clientside_callback(
        """
        function({n, v}) {
            const ctx = window.dash_clientside.callback_context;
            const g = ctx.args_grouping;
            return JSON.stringify({
                using_args: ctx.using_args_grouping,
                using_outputs: ctx.using_outputs_grouping,
                n_triggered: g.n.triggered,
                v_triggered: g.v.triggered,
                v_str_id: g.v.str_id,
                v_value: g.v.value
            });
        }
        """,
        output=Output("out", "children"),
        inputs=dict(n=Input("go", "n_clicks"), v=State("other", "value")),
        prevent_initial_call=True,
    )

    dash_duo.start_server(app)

    dash_duo.find_element("#go").click()
    dash_duo.wait_for_text_to_equal(
        "#out",
        '{"using_args":true,"using_outputs":false,"n_triggered":true,'
        '"v_triggered":false,"v_str_id":"other","v_value":"v0"}',
    )

    assert dash_duo.get_logs() == []


def test_clsg007_grouped_wrong_return_shape(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(id="val", value="start"),
            html.Div(id="out-a", children="init-a"),
            html.Div(id="out-b", children="init-b"),
        ]
    )

    app.clientside_callback(
        """
        function({v}) {
            return {x: v};  // missing the `y` key
        }
        """,
        output=dict(x=Output("out-a", "children"), y=Output("out-b", "children")),
        inputs=dict(v=Input("val", "value")),
    )

    dash_duo.start_server(app)

    # The shape mismatch surfaces as a clientside error and no outputs update
    dash_duo.wait_for_text_to_equal("#out-a", "init-a")
    dash_duo.wait_for_text_to_equal("#out-b", "init-b")

    logs = dash_duo.get_logs()
    assert logs
    assert any("output grouping" in log["message"] for log in logs)
