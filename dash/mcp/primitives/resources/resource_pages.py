"""Pages resource for multi-page apps."""

from __future__ import annotations

import json

from dash.mcp.types import (
    ReadResourceResult,
    Resource,
    TextResourceContents,
)

from dash._pages import PAGE_REGISTRY

from .base import MCPResourceProvider


class PagesResource(MCPResourceProvider):
    uri = "dash://pages"

    @classmethod
    def get_resource(cls) -> Resource | None:
        if not PAGE_REGISTRY:
            return None
        return Resource(
            uri=cls.uri,
            name="dash_app_pages",
            description=(
                "List of all pages in this multi-page Dash app "
                "with paths, names, titles, and descriptions."
            ),
            mimeType="application/json",
        )

    @classmethod
    def read_resource(cls, uri: str = "") -> ReadResourceResult:
        pages = []
        for module, page in PAGE_REGISTRY.items():
            title = page.get("title", "")
            description = page.get("description", "")
            pages.append(
                {
                    "module": module,
                    "path": page.get("path", ""),
                    "name": page.get("name", ""),
                    "title": title if not callable(title) else page.get("name", ""),
                    "description": description if not callable(description) else "",
                }
            )

        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=cls.uri,
                    mimeType="application/json",
                    text=json.dumps(pages, default=str),
                )
            ]
        )
