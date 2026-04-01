"""Output schema derived from CallbackDispatchResponse."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from dash.types import CallbackDispatchResponse

_schema = TypeAdapter(CallbackDispatchResponse).json_schema()


def callback_response_schema() -> dict[str, Any]:
    """Return the JSON Schema for a callback dispatch response."""
    return _schema
