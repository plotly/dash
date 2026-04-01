"""Tests for callback dispatch execution via MCP tools."""

from dash import Dash, Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from dash.mcp._server import _process_mcp_message

from tests.unit.mcp.conftest import _setup_mcp


def _msg(method, params=None, request_id=1):
    d = {"jsonrpc": "2.0", "method": method, "id": request_id}
    d["params"] = params if params is not None else {}
    return d


def _mcp(app, method, params=None, request_id=1):
    with app.server.test_request_context():
        _setup_mcp(app)
        return _process_mcp_message(_msg(method, params, request_id))


def _tools_list(app):
    return _mcp(app, "tools/list")["result"]["tools"]


def _call_tool_structured(app, tool_name, arguments=None):
    result = _mcp(app, "tools/call", {"name": tool_name, "arguments": arguments or {}})
    return result["result"]["structuredContent"]


def _call_tool_output(
    app, tool_name, arguments=None, component_id=None, prop="children"
):
    structured = _call_tool_structured(app, tool_name, arguments)
    response = structured["response"]
    if component_id is None:
        component_id = next(iter(response))
    return response[component_id][prop]


class TestRunCallback:
    def test_multi_output(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="dd", options=["a", "b"], value="a"),
                dcc.Dropdown(id="dd2"),
                html.Div(id="out"),
            ]
        )

        @app.callback(
            Output("dd2", "options"),
            Output("out", "children"),
            Input("dd", "value"),
        )
        def update(val):
            return [{"label": val, "value": val}], f"selected: {val}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "update" in t["name"])
        structured = _call_tool_structured(app, tool_name, {"val": "b"})
        assert structured["response"]["dd2"]["options"] == [
            {"label": "b", "value": "b"}
        ]
        assert structured["response"]["out"]["children"] == "selected: b"

    def test_omitted_kwargs_default_to_none(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="dd", options=["a"]),
                dcc.Input(id="inp"),
                html.Div(id="out"),
            ]
        )

        @app.callback(
            Output("out", "children"),
            Input("dd", "value"),
            State("inp", "value"),
        )
        def update(selected, text):
            return f"{selected}-{text}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "update" in t["name"])
        assert _call_tool_output(app, tool_name, {"selected": "a"}, "out") == "a-None"

    def test_no_output_callback(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Button(id="btn"),
                html.Div(id="display"),
            ]
        )

        @app.callback(Input("btn", "n_clicks"))
        def server_cb(n):
            from dash import set_props

            set_props("display", {"children": f"Clicked {n} times"})

        tools = _tools_list(app)
        tool_names = [t["name"] for t in tools]
        assert "server_cb" in tool_names

    def test_prevent_update(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="inp", value="hello"),
                html.Div(id="out"),
            ]
        )

        @app.callback(Output("out", "children"), Input("inp", "value"))
        def update(val):
            if val == "block":
                raise PreventUpdate
            return f"got: {val}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "update" in t["name"])
        assert _call_tool_output(app, tool_name, {"val": "test"}, "out") == "got: test"

    def test_with_state(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="trigger"),
                html.Div(id="store"),
                html.Div(id="result"),
            ]
        )

        @app.callback(
            Output("result", "children"),
            Input("trigger", "children"),
            State("store", "children"),
        )
        def with_state(trigger, store):
            return f"{trigger}-{store}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "with_state" in t["name"])
        assert (
            _call_tool_output(
                app,
                tool_name,
                {
                    "trigger": "click",
                    "store": "data",
                },
                "result",
            )
            == "click-data"
        )

    def test_dict_inputs(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="x-input", value="hello"),
                dcc.Input(id="y-input", value="world"),
                html.Div(id="dict-out"),
            ]
        )

        @app.callback(
            Output("dict-out", "children"),
            inputs={
                "x_val": Input("x-input", "value"),
                "y_val": Input("y-input", "value"),
            },
        )
        def combine(**kwargs):
            return f"{kwargs['x_val']}-{kwargs['y_val']}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "combine" in t["name"])
        assert (
            _call_tool_output(
                app,
                tool_name,
                {
                    "x_val": "foo",
                    "y_val": "bar",
                },
                "dict-out",
            )
            == "foo-bar"
        )

    def test_positional_inputs(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="a-input", value="A"),
                html.Div(id="pos-out"),
            ]
        )

        @app.callback(Output("pos-out", "children"), Input("a-input", "value"))
        def echo(val):
            return f"got:{val}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "echo" in t["name"])
        assert (
            _call_tool_output(app, tool_name, {"val": "test"}, "pos-out") == "got:test"
        )

    def test_dict_inputs_with_state(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="inp", value="hi"),
                html.Div(id="st", children="state-val"),
                html.Div(id="ds-out"),
            ]
        )

        @app.callback(
            Output("ds-out", "children"),
            inputs={"trigger": Input("inp", "value")},
            state={"kept": State("st", "children")},
        )
        def with_dict_state(**kwargs):
            return f"{kwargs['trigger']}+{kwargs['kept']}"

        tools = _tools_list(app)
        tool_name = next(t["name"] for t in tools if "with_dict_state" in t["name"])
        assert (
            _call_tool_output(
                app,
                tool_name,
                {
                    "trigger": "hey",
                    "kept": "saved",
                },
                "ds-out",
            )
            == "hey+saved"
        )
