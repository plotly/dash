"""Tests for the dash://pages resource."""

import json
from unittest.mock import patch

from dash import Dash, html

from dash.mcp.primitives.resources import list_resources, read_resource

EXPECTED_PAGES = [
    {
        "path": "/",
        "name": "Home",
        "title": "Home Page",
        "description": "The landing page",
        "module": "pages.home",
    },
    {
        "path": "/analytics",
        "name": "Analytics",
        "title": "Analytics Dashboard",
        "description": "View analytics",
        "module": "pages.analytics",
    },
]


class TestPagesResource:
    @staticmethod
    def _make_app():
        app = Dash(__name__)
        app.layout = html.Div(id="main")
        return app

    def test_listed_for_multi_page_app(self):
        app = self._make_app()
        fake_registry = {
            "pages.home": {
                "path": "/",
                "name": "Home",
                "title": "Home",
                "description": "",
            }
        }
        with app.server.test_request_context():
            with patch(
                "dash.mcp.primitives.resources.resource_pages.PAGE_REGISTRY",
                fake_registry,
            ):
                result = list_resources()
        uris = [str(r.uri) for r in result.resources]
        assert "dash://pages" in uris

    def test_returns_page_info(self):
        app = self._make_app()
        fake_registry = {
            "pages.home": EXPECTED_PAGES[0],
            "pages.analytics": EXPECTED_PAGES[1],
        }
        with app.server.test_request_context():
            with patch(
                "dash.mcp.primitives.resources.resource_pages.PAGE_REGISTRY",
                fake_registry,
            ):
                result = read_resource("dash://pages")
        content = json.loads(result.contents[0].text)
        assert content == EXPECTED_PAGES

    def test_callable_title_falls_back_to_name(self):
        app = self._make_app()
        fake_registry = {
            "pages.dynamic": {
                "path": "/item/<item_id>",
                "name": "Item Detail",
                "title": lambda **kwargs: f"Item {kwargs.get('item_id', '')}",
                "description": lambda **kwargs: f"Details for {kwargs.get('item_id', '')}",
            },
        }
        with app.server.test_request_context():
            with patch(
                "dash.mcp.primitives.resources.resource_pages.PAGE_REGISTRY",
                fake_registry,
            ):
                result = read_resource("dash://pages")
        page = json.loads(result.contents[0].text)[0]
        assert page["title"] == "Item Detail"
        assert page["description"] == ""
