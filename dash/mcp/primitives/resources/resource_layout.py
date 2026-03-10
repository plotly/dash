"""Layout tree resource for the whole app."""

from __future__ import annotations

from mcp.types import (
    ReadResourceResult,
    Resource,
    ResourceTemplate,
    TextResourceContents,
)

from dash import get_app
from dash._utils import to_json

URI = "dash://layout"


def get_resource() -> Resource | None:
    return Resource(
        uri=URI,
        name="dash_app_layout",
        description=(
            "Full component tree of the Dash app. "
            "See dash://components for a compact list of component IDs."
        ),
        mimeType="application/json",
    )


def get_template() -> ResourceTemplate | None:
    return None


def read_resource(uri: str = "") -> ReadResourceResult:
    app = get_app()
    return ReadResourceResult(
        contents=[
            TextResourceContents(
                uri=URI,
                mimeType="application/json",
                text=to_json(app.get_layout()),
            )
        ]
    )
