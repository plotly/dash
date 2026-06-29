"""Component list resource."""

from __future__ import annotations

import json

from pydantic import AnyUrl

from dash.mcp.types import (
    ReadResourceResult,
    Resource,
    TextResourceContents,
)

from dash import get_app
from dash._layout_utils import traverse

from .base import MCPResourceProvider


class ComponentsResource(MCPResourceProvider):
    uri = "dash://components"

    @classmethod
    def get_resource(cls) -> Resource | None:
        return Resource(
            uri=AnyUrl(cls.uri),
            name="dash_components",
            description=(
                "All components with IDs in the app layout. "
                "Use get_dash_component with any of these IDs "
                "to inspect their properties and values. "
                "See dash://layout for the tree structure showing "
                "how these components are nested in the page."
            ),
            mimeType="application/json",
        )

    @classmethod
    def read_resource(cls, uri: str = "") -> ReadResourceResult:
        app = get_app()
        layout = app.get_layout()
        components = sorted(
            [
                {
                    "id": str(getattr(comp, "id")),
                    "type": getattr(comp, "_type", type(comp).__name__),
                }
                for comp, _ in traverse(layout)
                if getattr(comp, "id", None) is not None
            ],
            key=lambda c: c["id"],
        )

        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=AnyUrl(cls.uri),
                    mimeType="application/json",
                    text=json.dumps(components),
                )
            ]
        )
