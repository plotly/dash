"""Typed dicts for MCP callback adapter data."""

from __future__ import annotations

from typing import Any

from typing_extensions import TypedDict


class MCPOutput(TypedDict):
    """A single callback output, with component type and initial value resolved."""

    id_and_prop: str
    component_id: str
    property: str
    component_type: str | None
    initial_value: Any
    tool_name: str


class MCPInput(TypedDict):
    """A single callback parameter (input or state), fully resolved."""

    name: str
    id_and_prop: str
    component_id: str
    property: str
    annotation: Any | None
    component_type: str | None
    component: Any | None
    required: bool
    initial_value: Any
    upstream_output: MCPOutput | None
