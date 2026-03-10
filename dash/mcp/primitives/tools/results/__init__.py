"""Tool result formatting for MCP tools/call responses.

Each result formatter shares the same signature:
``(component_type, prop, value, component) -> list[TextContent | ImageContent]``

Formatters inspect individual output values and produce additional
content items (images, markdown tables, etc.). The structuredContent
is always the full dispatch response.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import CallToolResult, TextContent

from dash.types import CallbackDispatchResponse

from .result_dataframe import dataframe_result
from .result_plotly_figure import plotly_figure_result

_STRUCTURED_RESULTS = [
    plotly_figure_result,
    dataframe_result,
]


def format_callback_response(
    response: CallbackDispatchResponse,
    component_types: dict[str, str] | None = None,
    component_instances: dict[str, Any] | None = None,
) -> CallToolResult:
    """Format a dispatch response as a CallToolResult.

    The response is always returned as structuredContent. Result
    formatters are called per output property and may add additional
    content items (images, markdown, etc.).
    """
    # Per MCP spec: "a tool that returns structured content SHOULD also
    # return the serialized JSON in a TextContent block."
    # https://modelcontextprotocol.io/specification/2025-11-25/server/tools#structured-content
    content: list[Any] = [
        TextContent(type="text", text=json.dumps(response, default=str)),
    ]

    for comp_id, props in (response.get("response") or {}).items():
        comp_type = (component_types or {}).get(comp_id)
        component = (component_instances or {}).get(comp_id)
        for prop, value in props.items():
            for result_fn in _STRUCTURED_RESULTS:
                content.extend(result_fn(comp_type, prop, value, component))

    return CallToolResult(
        content=content,
        structuredContent=response,
    )
