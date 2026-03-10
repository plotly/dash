"""Tests for CallbackAdapterCollection."""

from dash import Dash, Input, Output, dcc, html

from tests.unit.mcp.conftest import (
    _call_tool,
    _call_tool_output,
    _setup_mcp,
    _tools_list,
)


class TestToolNameCollisions:
    @staticmethod
    def _make_duplicate_cb_app(n=3):
        ids = [f"dd{i + 1}" for i in range(n)]
        app = Dash(__name__)
        app.layout = html.Div(
            [
                item
                for i in ids
                for item in [
                    dcc.Dropdown(
                        id=i, options=[chr(97 + j) for j in range(1)], value="a"
                    ),
                    html.Div(id=f"{i}-output"),
                ]
            ]
        )
        for idx, dd_id in enumerate(ids):

            @app.callback(Output(f"{dd_id}-output", "children"), Input(dd_id, "value"))
            def cb(value, _id=dd_id):  # noqa: F811
                return f"{_id}: {value}"

        return app

    @staticmethod
    def _cb_tools(tools):
        return [
            t
            for t in tools
            if t["name"] not in ("get_dash_component", "dash_list_pages")
        ]

    def test_duplicate_func_names_get_unique_tools(self):
        app = self._make_duplicate_cb_app(3)
        cb_tools = self._cb_tools(_tools_list(app))
        tool_names = [t["name"] for t in cb_tools]
        assert len(tool_names) == 3
        assert len(set(tool_names)) == 3, f"Tool names are not unique: {tool_names}"
        for name in tool_names:
            assert "dd" in name, f"Expected output ID in tool name: {name}"

    def test_duplicate_func_names_each_callable(self):
        app = self._make_duplicate_cb_app(2)
        cb_tools = self._cb_tools(_tools_list(app))
        results = []
        for tool in cb_tools:
            param_names = list(tool["inputSchema"]["properties"].keys())
            assert len(param_names) == 1
            children = _call_tool_output(app, tool["name"], {param_names[0]: "test"})
            results.append(children)
        assert len(set(results)) == 2, f"Expected distinct results, got: {results}"

    def test_unique_func_names_use_func_name(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="in1"),
                html.Div(id="out1"),
                html.Div(id="in2"),
                html.Div(id="out2"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("in1", "children"))
        def alpha_handler(value):
            return value

        @app.callback(Output("out2", "children"), Input("in2", "children"))
        def beta_handler(value):
            return value

        tool_names = [t["name"] for t in _tools_list(app)]
        assert "alpha_handler" in tool_names
        assert "beta_handler" in tool_names

    def test_duplicate_func_names_use_output_id(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="out1"),
                html.Div(id="out2"),
                html.Div(id="out3"),
                html.Div(id="in1"),
                html.Div(id="in2"),
                html.Div(id="in3"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("in1", "children"))
        def unique_func(v):
            return v

        @app.callback(Output("out2", "children"), Input("in2", "children"))
        def cb(v):
            return v

        @app.callback(Output("out3", "children"), Input("in3", "children"))
        def cb(v):  # noqa: F811
            return v

        _setup_mcp(app)
        tool_names = [a.tool_name for a in app.mcp_callback_map]
        assert "unique_func" in tool_names
        non_unique = [n for n in tool_names if n != "unique_func"]
        assert len(non_unique) == 2
        assert non_unique[0] != non_unique[1]

    def test_missing_component_suggests_relevant_tools(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="container"),
                html.Div(id="trigger"),
            ]
        )

        @app.callback(Output("container", "children"), Input("trigger", "children"))
        def render(value):
            from dash import html

            return html.Div(id="dynamic")

        result = _call_tool(app, "get_dash_component", {"component_id": "nonexistent"})
        text = result["result"]["content"][0]["text"]
        assert "not found" in text


class TestAllCallbacksVisibleByDefault:
    def test_all_callbacks_visible_by_default(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Div(id="in1"),
                html.Div(id="out1"),
                html.Div(id="in2"),
                html.Div(id="out2"),
            ]
        )

        @app.callback(Output("out1", "children"), Input("in1", "children"))
        def cb_one(value):
            return value

        @app.callback(Output("out2", "children"), Input("in2", "children"))
        def cb_two(value):
            return value

        tool_names = [t["name"] for t in _tools_list(app)]
        assert "cb_one" in tool_names
        assert "cb_two" in tool_names


class TestAdapterCollection:
    def test_adapter_has_expected_properties(self):
        app = Dash(__name__)
        app.layout = html.Div([dcc.Input(id="inp"), html.Div(id="out")])

        @app.callback(Output("out", "children"), Input("inp", "value"))
        def update(val):
            return val

        _setup_mcp(app)
        adapter = app.mcp_callback_map[0]
        assert adapter.tool_name == "update"
        assert adapter.output_id == "out.children"
