"""Callback introspection utilities for MCP tools."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from dash import get_app

if TYPE_CHECKING:
    from .callback_adapter import CallbackAdapter


def run_callback(callback: CallbackAdapter, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Execute a callback via Dash's dispatch pipeline."""
    from dash.mcp.types import CallbackExecutionError

    body = callback.as_callback_body(kwargs)

    app = get_app()
    with app.server.test_request_context(
        "/_dash-update-component",
        method="POST",
        data=json.dumps(body, default=str),
        content_type="application/json",
    ):
        response = app.dispatch()

    response_text = response.get_data(as_text=True)
    if response.status_code != 200:
        raise CallbackExecutionError(
            f"Callback {callback.output_id} failed "
            f"(HTTP {response.status_code}): {response_text[:500]}"
        )

    return json.loads(response_text)
