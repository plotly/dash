"""MCP tools backed by ``@mcp_enabled``-decorated functions."""

from __future__ import annotations

import inspect
import json
import typing
from typing import Any, Callable

from dash.mcp.types import CallToolResult, TextContent, Tool

from dash import get_app
from dash.mcp._decorator import MCPToolRegistration
from dash.mcp.primitives.tools.tools_callbacks import CallbackTools
from dash.mcp.primitives.tools.input_schemas import get_input_schema
from dash.mcp.primitives.tools.input_schemas.schema_callback_type_annotations import (
    annotation_to_json_schema,
)
from dash.mcp.types import MCPInput, is_nullable

from .base import MCPToolProvider


def _build_inputs(fn: Callable[..., Any]) -> list[MCPInput]:
    """Build an ``MCPInput`` from each of the function's arguments."""
    try:
        hints = typing.get_type_hints(fn)
    except Exception:  # pylint: disable=broad-exception-caught
        hints = getattr(fn, "__annotations__", {})

    sig = inspect.signature(fn)
    inputs: list[MCPInput] = []

    for name, param in sig.parameters.items():
        annotation = hints.get(name)

        has_default = param.default is not inspect.Parameter.empty
        required = not has_default and (
            annotation is None or not is_nullable(annotation)
        )

        inputs.append(
            MCPInput(
                name=name,
                id_and_prop="",
                component_id="",
                property="",
                annotation=annotation,
                component_type=None,
                component=None,
                required=required,
                initial_value=param.default if has_default else None,
                upstream_output=None,
            )
        )
    return inputs


def _build_output_schema(fn: Callable[..., Any]) -> dict[str, Any]:
    """Build a JSON Schema ``outputSchema`` from the return annotation.

    The schema wraps the return type in ``{"result": <type>}`` to match
    the object that ``call_tool`` returns as ``structuredContent``.
    """
    try:
        hints = typing.get_type_hints(fn)
    except Exception:  # pylint: disable=broad-exception-caught
        hints = getattr(fn, "__annotations__", {})

    ret = hints.get("return")
    if ret is None:
        return {}

    inner = annotation_to_json_schema(ret)
    if inner is None:
        return {}

    return {
        "type": "object",
        "properties": {"result": inner},
        "required": ["result"],
    }


def _build_tool(tool_name: str, reg: MCPToolRegistration) -> Tool:
    fn = reg["fn"]
    inputs = _build_inputs(fn)
    properties = {p["name"]: get_input_schema(p) for p in inputs}
    required = [p["name"] for p in inputs if p["required"]]

    input_schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        input_schema["required"] = required

    expose_docstring = reg["expose_docstring"]
    if expose_docstring is None:
        expose_docstring = CallbackTools.expose_docstrings_by_default

    description = "MCP tool"
    if expose_docstring:
        docstring = getattr(fn, "__doc__", None)
        if docstring:
            description = docstring.strip()

    return Tool(
        name=tool_name,
        description=description,
        inputSchema=input_schema,
        outputSchema=_build_output_schema(fn),
    )


class DecoratedFunctionTools(MCPToolProvider):
    """Exposes ``@mcp_enabled``-decorated functions as MCP tools."""

    @classmethod
    def _registry(cls) -> dict[str, MCPToolRegistration]:
        return get_app().mcp_decorated_functions

    @classmethod
    def get_tool_names(cls) -> set[str]:
        return set(cls._registry().keys())

    @classmethod
    def list_tools(cls) -> list[Tool]:
        return [_build_tool(name, reg) for name, reg in cls._registry().items()]

    @classmethod
    def call_tool(
        cls, tool_name: str, arguments: dict[str, Any], task: dict | None = None
    ) -> CallToolResult:
        reg = cls._registry().get(tool_name)
        if reg is None:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Tool not found: {tool_name}")],
                isError=True,
            )
        fn = reg["fn"]
        try:
            result = fn(**arguments)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return CallToolResult(
                content=[TextContent(type="text", text=f"{type(exc).__name__}: {exc}")],
                isError=True,
            )

        serialized = json.dumps(result, default=str)
        return CallToolResult(
            content=[TextContent(type="text", text=serialized)],
            structuredContent={"result": result},
        )
