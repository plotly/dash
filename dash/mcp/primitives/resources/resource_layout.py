"""Layout tree resource for the whole app."""

from __future__ import annotations

from mcp.types import (
    ReadResourceResult,
    Resource,
    TextResourceContents,
)
from pydantic import AnyUrl

from dash import get_app
from dash._utils import to_json

from .base import MCPResourceProvider


class LayoutResource(MCPResourceProvider):
    uri = "dash://layout"

    @classmethod
    def get_resource(cls) -> Resource | None:
        return Resource(
            uri=AnyUrl(cls.uri),
            name="dash_app_layout",
            description=(
                "Full component tree of the Dash app. "
                "See dash://components for a compact list of component IDs."
            ),
            mimeType="application/json",
        )

    @classmethod
    def read_resource(cls, uri: str = "") -> ReadResourceResult:
        app = get_app()
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=AnyUrl(cls.uri),
                    mimeType="application/json",
                    text=to_json(app.get_layout()),
                )
            ]
        )
