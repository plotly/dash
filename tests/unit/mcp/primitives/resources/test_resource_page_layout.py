"""Tests for the dash://page-layout/{path} resource template."""

import json
from unittest.mock import patch

from dash import Dash, dcc, html

from dash.mcp.primitives.resources import read_resource

EXPECTED_PAGE_LAYOUT = {
    "type": "Div",
    "namespace": "dash_html_components",
    "props": {
        "children": [
            {
                "type": "Dropdown",
                "namespace": "dash_core_components",
                "props": {
                    "id": "page-dd",
                    "options": ["a", "b"],
                    "value": "a",
                },
            }
        ]
    },
}


class TestPageLayoutResource:
    def test_read_page_layout(self):
        app = Dash(__name__)
        app.layout = html.Div(id="main")

        page_layout = html.Div(
            [
                dcc.Dropdown(id="page-dd", options=["a", "b"], value="a"),
            ]
        )
        fake_registry = {
            "pages.test": {
                "path": "/test",
                "name": "Test",
                "title": "Test Page",
                "description": "",
                "layout": page_layout,
            },
        }
        with app.server.test_request_context():
            with patch(
                "dash.mcp.primitives.resources.resource_page_layout.PAGE_REGISTRY",
                fake_registry,
            ):
                result = read_resource("dash://page-layout/test")
        layout = json.loads(result.contents[0].text)
        assert layout == EXPECTED_PAGE_LAYOUT
