"""Tests for the dash://clientside-callbacks resource."""

import json

from dash import Dash, Input, Output, clientside_callback, html

from tests.unit.mcp.conftest import _mcp, _tools_list


class TestClientsideCallbacksResource:
    @staticmethod
    def _make_app():
        app = Dash(__name__)
        app.layout = html.Div(
            [
                html.Button(id="btn", children="Click"),
                html.Div(id="out"),
                html.Div(id="server-out"),
            ]
        )

        clientside_callback(
            "function(n) { return n; }",
            Output("out", "children"),
            Input("btn", "n_clicks"),
        )

        @app.callback(Output("server-out", "children"), Input("btn", "n_clicks"))
        def server_cb(n):
            return str(n)

        with app.server.test_request_context():
            app._setup_server()

        return app

    def test_clientside_excluded_from_tools(self):
        app = self._make_app()
        tools = _tools_list(app)
        # 1 server callback + get_dash_component = 2 tools total
        # The clientside callback is NOT included
        assert len(tools) == 2

    def test_resource_listed(self):
        app = self._make_app()
        result = _mcp(app, "resources/list")
        uris = [r["uri"] for r in result["result"]["resources"]]
        assert "dash://clientside-callbacks" in uris

    def test_resource_read(self):
        app = self._make_app()
        result = _mcp(app, "resources/read", {"uri": "dash://clientside-callbacks"})
        data = json.loads(result["result"]["contents"][0]["text"])
        assert "description" in data
        callbacks = data["callbacks"]
        assert len(callbacks) == 1
        assert callbacks[0]["inputs"][0]["component_id"] == "btn"
        assert callbacks[0]["inputs"][0]["property"] == "n_clicks"
        assert callbacks[0]["outputs"][0]["component_id"] == "out"
