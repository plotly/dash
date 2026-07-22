"""Tests for the dash://layout resource."""

import json
from unittest.mock import patch

from dash import Dash, dcc, html

from dash.mcp.primitives.resources import list_resources, read_resource

EXPECTED_LAYOUT = {
    "type": "Div",
    "namespace": "dash_html_components",
    "props": {
        "children": [
            {
                "type": "Dropdown",
                "namespace": "dash_core_components",
                "props": {
                    "id": "test-dd",
                    "options": ["a", "b"],
                    "value": "a",
                },
            },
            {
                "type": "Div",
                "namespace": "dash_html_components",
                "props": {
                    "children": None,
                    "id": "output",
                },
            },
        ]
    },
}


class TestLayoutResource:
    def test_listed_in_resources(self):
        app = Dash(__name__)
        app.layout = html.Div(id="main")
        with app.server.test_request_context():
            result = list_resources()
        uris = [str(r.uri) for r in result.resources]
        assert "dash://layout" in uris

    def test_read_returns_layout(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="test-dd", options=["a", "b"], value="a"),
                html.Div(id="output"),
            ]
        )
        with app.server.test_request_context():
            with patch.object(app, "get_layout", wraps=app.get_layout) as mock:
                result = read_resource("dash://layout")
                mock.assert_called_once()
        layout = json.loads(result.contents[0].text)
        assert layout == EXPECTED_LAYOUT
