"""Pages resource for multi-page apps."""

from __future__ import annotations

import json

from mcp.types import (
    ReadResourceResult,
    Resource,
    ResourceTemplate,
    TextResourceContents,
)

URI = "dash://pages"


def _has_pages() -> bool:
    try:
        from dash._pages import PAGE_REGISTRY

        return bool(PAGE_REGISTRY)
    except ImportError:
        return False


def get_resource() -> Resource | None:
    if not _has_pages():
        return None
    return Resource(
        uri=URI,
        name="dash_app_pages",
        description=(
            "List of all pages in this multi-page Dash app "
            "with paths, names, titles, and descriptions."
        ),
        mimeType="application/json",
    )


def get_template() -> ResourceTemplate | None:
    return None


def read_resource(uri: str = "") -> ReadResourceResult:
    try:
        from dash._pages import PAGE_REGISTRY
    except ImportError:
        return ReadResourceResult(
            contents=[
                TextResourceContents(uri=URI, mimeType="application/json", text="[]")
            ]
        )

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
                uri=URI,
                mimeType="application/json",
                text=json.dumps(pages, default=str),
            )
        ]
    )
