"""Tests for the dash://layout resource."""

import json
from unittest.mock import patch

from dash import Dash, dcc, html

from tests.unit.mcp.conftest import _mcp

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
        result = _mcp(app, "resources/list")
        uris = [r["uri"] for r in result["result"]["resources"]]
        assert "dash://layout" in uris

    def test_read_returns_layout_matching_dash_layout_endpoint(self):
        app = Dash(__name__)
        app.layout = html.Div(
            [
                dcc.Dropdown(id="test-dd", options=["a", "b"], value="a"),
                html.Div(id="output"),
            ]
        )

        with patch.object(app, "get_layout", wraps=app.get_layout) as mock_get_layout:
            result = _mcp(app, "resources/read", {"uri": "dash://layout"})
            mock_get_layout.assert_called_once()

        layout = json.loads(result["result"]["contents"][0]["text"])
        assert layout == EXPECTED_LAYOUT
