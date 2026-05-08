"""Tool result formatting for MCP tools/call responses.

Each formatter is a ``ResultFormatter`` subclass that can enrich
a tool result with additional content. All formatters are accumulated.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.types import CallToolResult, TextContent

from dash.types import CallbackExecutionResponse
from dash.mcp.primitives.tools.callback_adapter import CallbackAdapter

from .base import ResultFormatter
from .result_dataframe import DataFrameResult
from .result_plotly_figure import PlotlyFigureResult

_RESULT_FORMATTERS: list[type[ResultFormatter]] = [
    PlotlyFigureResult,
    DataFrameResult,
]


def format_callback_response(
    response: CallbackExecutionResponse,
    callback: CallbackAdapter,
) -> CallToolResult:
    """Format a callback response as a CallToolResult.

    The response is always returned as structuredContent. Result
    formatters are called per output property and may add additional
    content items (images, markdown, etc.).
    """
    content: list[Any] = [
        TextContent(type="text", text=json.dumps(response, default=str)),
    ]

    resp = response.get("response") or {}
    for callback_output in callback.outputs:
        value = resp.get(callback_output["component_id"], {}).get(
            callback_output["property"]
        )
        for formatter in _RESULT_FORMATTERS:
            content.extend(formatter.format(callback_output, value))

    return CallToolResult(
        content=content,
        structuredContent=response,
    )
