"""Tests for the dash://clientside-callbacks resource."""

import json

from dash import Dash, Input, Output, clientside_callback, html

from dash.mcp.primitives.resources import list_resources, read_resource


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

    def test_resource_listed(self):
        app = self._make_app()
        with app.server.test_request_context():
            result = list_resources()
        uris = [str(r.uri) for r in result.resources]
        assert "dash://clientside-callbacks" in uris

    def test_resource_read(self):
        app = self._make_app()
        with app.server.test_request_context():
            result = read_resource("dash://clientside-callbacks")
        data = json.loads(result.contents[0].text)
        assert "description" in data
        callbacks = data["callbacks"]
        assert len(callbacks) == 1
        assert callbacks[0]["inputs"][0]["component_id"] == "btn"
        assert callbacks[0]["inputs"][0]["property"] == "n_clicks"
        assert callbacks[0]["outputs"][0]["component_id"] == "out"
