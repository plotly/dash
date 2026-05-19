"""Per-page layout resource template for multi-page apps."""

from __future__ import annotations

from mcp.types import (
    ReadResourceResult,
    ResourceTemplate,
    TextResourceContents,
)
from pydantic import AnyUrl

from dash import html
from dash._pages import PAGE_REGISTRY
from dash._utils import to_json

from .base import MCPResourceProvider

_URI_TEMPLATE = "dash://page-layout/{path}"


class PageLayoutResource(MCPResourceProvider):
    uri = "dash://page-layout/"

    @classmethod
    def get_template(cls) -> ResourceTemplate | None:
        if not PAGE_REGISTRY:
            return None
        return ResourceTemplate(
            uriTemplate=_URI_TEMPLATE,
            name="dash_page_layout",
            description="Component tree for a specific page in the app.",
            mimeType="application/json",
        )

    @classmethod
    def read_resource(cls, uri: str) -> ReadResourceResult:
        path = uri[len(cls.uri) :]
        if not path.startswith("/"):
            path = "/" + path

        page_layout = None
        for _module, page in PAGE_REGISTRY.items():
            if page.get("path") == path:
                page_layout = page.get("layout")
                break

        if page_layout is None:
            raise ValueError(f"Page not found: {path}")

        if callable(page_layout):
            page_layout = page_layout()

        if isinstance(page_layout, (list, tuple)):
            page_layout = html.Div(list(page_layout))

        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=AnyUrl(uri),
                    mimeType="application/json",
                    text=to_json(page_layout),
                )
            ]
        )
