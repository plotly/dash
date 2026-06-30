"""Clientside callbacks resource."""

from __future__ import annotations

import json
from typing import Any

from pydantic import AnyUrl

from dash.mcp.types import (
    ReadResourceResult,
    Resource,
    TextResourceContents,
)

from dash import get_app
from dash._utils import clean_property_name, split_callback_id

from .base import MCPResourceProvider


class ClientsideCallbacksResource(MCPResourceProvider):
    uri = "dash://clientside-callbacks"

    @classmethod
    def get_resource(cls) -> Resource | None:
        if not _get_clientside_callbacks():
            return None
        return Resource(
            uri=AnyUrl(cls.uri),
            name="dash_clientside_callbacks",
            description=(
                "Actions the user can take manually in the browser "
                "to affect clientside state. Inputs describe the "
                "components that can be changed to trigger an effect. "
                "Outputs describe the components that will change "
                "in response."
            ),
            mimeType="application/json",
        )

    @classmethod
    def read_resource(cls, uri: str = "") -> ReadResourceResult:
        data = {
            "description": (
                "These are actions that the user can take manually in the "
                "browser to affect the clientside state. Inputs describe "
                "the components that can be changed to trigger an effect. "
                "Outputs describe the components that will change in "
                "response to the effect."
            ),
            "callbacks": _get_clientside_callbacks(),
        }
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=AnyUrl(cls.uri),
                    mimeType="application/json",
                    text=json.dumps(data, default=str),
                )
            ]
        )


def _get_clientside_callbacks() -> list[dict[str, Any]]:
    """Get input/output mappings for clientside callbacks."""
    app = get_app()
    callbacks = []
    callback_map = getattr(app, "callback_map", {})

    for output_id, callback_info in callback_map.items():
        if "callback" in callback_info:
            continue
        normalize_deps = lambda deps: [
            {
                "component_id": str(d.get("id", "unknown")),
                "property": d.get("property", "unknown"),
            }
            for d in deps
        ]
        parsed = split_callback_id(output_id)
        if isinstance(parsed, dict):
            parsed = [parsed]
        outputs = [
            {"component_id": p["id"], "property": clean_property_name(p["property"])}
            for p in parsed
        ]
        callbacks.append(
            {
                "outputs": outputs,
                "inputs": normalize_deps(callback_info.get("inputs", [])),
                "state": normalize_deps(callback_info.get("state", [])),
            }
        )

    return callbacks
