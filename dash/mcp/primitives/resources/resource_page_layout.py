"""Per-page layout resource template for multi-page apps."""

from __future__ import annotations

from mcp.types import (
    ReadResourceResult,
    Resource,
    ResourceTemplate,
    TextResourceContents,
)

from dash._utils import to_json

URI = "dash://page-layout/"
_URI_TEMPLATE = "dash://page-layout/{path}"


def get_resource() -> Resource | None:
    return None


def get_template() -> ResourceTemplate | None:
    if not _has_pages():
        return None
    return ResourceTemplate(
        uriTemplate=_URI_TEMPLATE,
        name="dash_page_layout",
        description="Component tree for a specific page in the app.",
        mimeType="application/json",
    )


def read_resource(uri: str) -> ReadResourceResult:
    path = uri[len(URI) :]
    if not path.startswith("/"):
        path = "/" + path

    try:
        from dash._pages import PAGE_REGISTRY
    except ImportError:
        raise ValueError("Dash Pages is not available.")

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
        from dash import html

        page_layout = html.Div(list(page_layout))

    return ReadResourceResult(
        contents=[
            TextResourceContents(
                uri=uri,
                mimeType="application/json",
                text=to_json(page_layout),
            )
        ]
    )


def _has_pages() -> bool:
    try:
        from dash._pages import PAGE_REGISTRY

        return bool(PAGE_REGISTRY)
    except ImportError:
        return False
