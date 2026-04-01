"""Generic component property descriptions.

Generate a description for each component prop that has a value (either set
directly in the layout or by an upstream callback).
"""

from __future__ import annotations

from typing import Any

from dash import get_app
from dash.mcp.types import MCPInput

_MAX_VALUE_LENGTH = 200

_MCP_EXCLUDED_PROPS = {"id", "className", "style"}

_PROP_TEMPLATES: dict[tuple[str | None, str], str] = {
    ("Store", "storage_type"): (
        "storage_type: {value}. Describes how to store the value client-side"
        "'memory' resets on page refresh. "
        "'session' persists for the duration of this session. "
        "'local' persists on disk until explicitly cleared."
    ),
}


def component_props_description(param: MCPInput) -> list[str]:
    component = param.get("component")
    if component is None:
        return []

    component_id = param["component_id"]
    cbmap = get_app().mcp_callback_map
    prop_lines: list[str] = []

    for prop_name in getattr(component, "_prop_names", []):
        if prop_name in _MCP_EXCLUDED_PROPS:
            continue

        upstream = cbmap.find_by_output(f"{component_id}.{prop_name}")
        if upstream is not None and not upstream.prevents_initial_call:
            value = upstream.initial_output_value(f"{component_id}.{prop_name}")
        else:
            value = getattr(component, prop_name, None)
        tool_name = upstream.tool_name if upstream is not None else None

        if value is None and tool_name is None:
            continue

        component_type = param.get("component_type")
        template = _PROP_TEMPLATES.get((component_type, prop_name))
        formatted_value = (
            _truncate_large_values(value, component_id, prop_name)
            if value is not None
            else None
        )

        if template and formatted_value is not None:
            line = template.format(value=formatted_value)
        elif formatted_value is not None:
            line = f"{prop_name}: {formatted_value}"
        else:
            line = prop_name

        if tool_name:
            line += f" (can be updated by tool: `{tool_name}`)"

        prop_lines.append(line)

    if not prop_lines:
        return []
    return [f"Component properties for {component_id}:"] + prop_lines


def _truncate_large_values(value: Any, component_id: str, prop_name: str) -> str:
    text = repr(value)
    if len(text) > _MAX_VALUE_LENGTH:
        hint = f"Use get_dash_component('{component_id}', '{prop_name}') for the full value"
        return f"{text[:_MAX_VALUE_LENGTH]}... ({hint})"
    return text
