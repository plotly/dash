"""Tests for the dash://pages resource."""

import json
from unittest.mock import patch

from tests.unit.mcp.conftest import _make_app, _mcp

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
    def test_listed_for_multi_page_app(self):
        app = _make_app()
        fake_registry = {
            "pages.home": {
                "path": "/",
                "name": "Home",
                "title": "Home",
                "description": "",
            }
        }
        with patch("dash._pages.PAGE_REGISTRY", fake_registry):
            result = _mcp(app, "resources/list")
        uris = [r["uri"] for r in result["result"]["resources"]]
        assert "dash://pages" in uris

    def test_returns_page_info(self):
        app = _make_app()
        fake_registry = {
            "pages.home": EXPECTED_PAGES[0],
            "pages.analytics": EXPECTED_PAGES[1],
        }
        with patch("dash._pages.PAGE_REGISTRY", fake_registry):
            result = _mcp(app, "resources/read", {"uri": "dash://pages"})
        content = json.loads(result["result"]["contents"][0]["text"])
        assert content == EXPECTED_PAGES

    def test_callable_title_falls_back_to_name(self):
        app = _make_app()
        fake_registry = {
            "pages.dynamic": {
                "path": "/item/<item_id>",
                "name": "Item Detail",
                "title": lambda **kwargs: f"Item {kwargs.get('item_id', '')}",
                "description": lambda **kwargs: f"Details for {kwargs.get('item_id', '')}",
            },
        }
        with patch("dash._pages.PAGE_REGISTRY", fake_registry):
            result = _mcp(app, "resources/read", {"uri": "dash://pages"})
        page = json.loads(result["result"]["contents"][0]["text"])[0]
        assert page["title"] == "Item Detail"
        assert page["description"] == ""
