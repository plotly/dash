"""Typed dicts for component data in MCP."""

from __future__ import annotations

from typing import Any

from typing_extensions import NotRequired, TypedDict


class ComponentPropertyInfo(TypedDict):
    initial_value: Any
    modified_by_tool: list[str]
    input_to_tool: list[str]


class ComponentQueryResult(TypedDict):
    component_id: str
    component_type: str
    label: NotRequired[list[str] | None]
    properties: dict[str, ComponentPropertyInfo]
