"""Built-in tool: get_dash_component."""

from __future__ import annotations

import json
from typing import Any

from dash.mcp.types import CallToolResult, TextContent, Tool
from pydantic import Field, TypeAdapter
from typing_extensions import Annotated, NotRequired, TypedDict

from dash import get_app
from dash._layout_utils import find_component
from dash.mcp.types import ComponentPropertyInfo, ComponentQueryResult

from .base import MCPToolProvider


class _ComponentQueryInput(TypedDict):
    component_id: Annotated[str, Field(description="The component ID to query")]
    property: NotRequired[
        Annotated[
            str,
            Field(
                description="The property name to read (e.g. 'options', 'value'). Omit to list all defined properties."
            ),
        ]
    ]


_INPUT_SCHEMA = TypeAdapter(_ComponentQueryInput).json_schema()
_OUTPUT_SCHEMA = TypeAdapter(ComponentQueryResult).json_schema()

NAME = "get_dash_component"


class GetDashComponentTool(MCPToolProvider):
    """Inspects a component's properties and its tool relationships."""

    @classmethod
    def get_tool_names(cls) -> set[str]:
        return {NAME}

    @classmethod
    def list_tools(cls) -> list[Tool]:
        return [
            Tool(
                name=NAME,
                description=(
                    "Get a component's properties, values, and tool relationships. "
                    "If property is omitted, returns all defined properties. "
                    "If property is specified, returns only that property. "
                    "See the dash://components resource for available component IDs."
                ),
                inputSchema=_INPUT_SCHEMA,
                outputSchema=_OUTPUT_SCHEMA,
            )
        ]

    @classmethod
    def call_tool(
        cls,
        tool_name: str,
        arguments: dict[str, Any],
        task: dict | None = None,
    ) -> CallToolResult:
        comp_id = arguments.get("component_id", "")
        if not comp_id:
            return CallToolResult(
                content=[TextContent(type="text", text="component_id is required")],
                isError=True,
            )

        prop_filter = arguments.get("property", "")
        component = find_component(comp_id)
        callback_map = get_app().mcp_callback_map

        if component is None:
            rendering_tools = [
                cb.tool_name
                for cb in callback_map
                if any(out["component_id"] == comp_id for out in cb.outputs)
            ]
            msg = f"Component '{comp_id}' not found in static layout."
            if rendering_tools:
                msg += (
                    f" However, the following tools would modify it: {rendering_tools}."
                )
            msg += " Use the dash://components resource to see statically available component IDs."
            return CallToolResult(
                content=[TextContent(type="text", text=msg)],
                isError=True,
            )

        properties: dict[str, ComponentPropertyInfo] = {}
        for prop_name in getattr(component, "_prop_names", []):
            if prop_filter and prop_name != prop_filter:
                continue

            id_and_prop = f"{comp_id}.{prop_name}"
            value = callback_map.get_initial_value(id_and_prop)
            if value is None:
                value = getattr(component, prop_name, None)
            if value is None:
                continue

            modified_by = [
                cb.tool_name for cb in callback_map.outputs_by_prop.get(id_and_prop, [])
            ]
            input_to = [
                cb.tool_name for cb in callback_map.inputs_by_prop.get(id_and_prop, [])
            ]

            properties[prop_name] = ComponentPropertyInfo(
                initial_value=value,
                modified_by_tool=modified_by,
                input_to_tool=input_to,
            )

        labels = callback_map.component_label_map.get(comp_id, [])

        structured: ComponentQueryResult = ComponentQueryResult(
            component_id=comp_id,
            component_type=type(component).__name__,
            label=labels if labels else None,
            properties=properties,
        )

        return CallToolResult(
            content=[
                TextContent(type="text", text=json.dumps(structured, default=str))
            ],
            structuredContent=dict(structured),
        )
