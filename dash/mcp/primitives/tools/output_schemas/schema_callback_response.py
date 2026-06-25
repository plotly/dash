"""Output schema derived from CallbackExecutionResponse."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from dash.types import CallbackExecutionResponse

_schema = TypeAdapter(CallbackExecutionResponse).json_schema()


def callback_response_schema() -> dict[str, Any]:
    """Return the JSON Schema for a callback dispatch response."""
    return _schema
