"""MCP protocol types: JSON-RPC, capabilities, tools, resources, tasks.

These replace the ``mcp`` package dependency. Only the types actually
used by Dash are defined here; the shapes match the MCP spec exactly
so wire-format compatibility is preserved.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field

LATEST_PROTOCOL_VERSION: str = "2025-11-25"

# --- JSON-RPC -----------------------------------------------------------------


class ErrorData(BaseModel):
    code: int
    message: str
    data: Any | None = None
    model_config = ConfigDict(extra="allow")


class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str | int
    result: dict[str, Any]
    model_config = ConfigDict(extra="allow")


class JSONRPCError(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str | int
    error: ErrorData
    model_config = ConfigDict(extra="allow")


# --- Capabilities -------------------------------------------------------------


class ToolsCapability(BaseModel):
    listChanged: bool | None = None
    model_config = ConfigDict(extra="allow")


class ResourcesCapability(BaseModel):
    subscribe: bool | None = None
    listChanged: bool | None = None
    model_config = ConfigDict(extra="allow")


class ServerCapabilities(BaseModel):
    resources: ResourcesCapability | None = None
    tools: ToolsCapability | None = None
    model_config = ConfigDict(extra="allow")


# --- Base types ---------------------------------------------------------------


class _Result(BaseModel):
    meta: dict[str, Any] | None = Field(alias="_meta", default=None)
    model_config = ConfigDict(extra="allow")


class _PaginatedResult(_Result):
    nextCursor: str | None = None


class Implementation(BaseModel):
    name: str
    version: str
    model_config = ConfigDict(extra="allow")


# --- Initialization -----------------------------------------------------------


class InitializeResult(_Result):
    protocolVersion: str | int
    capabilities: ServerCapabilities
    serverInfo: Implementation
    instructions: str | None = None


# --- Resources ----------------------------------------------------------------


class Resource(BaseModel):
    uri: AnyUrl
    name: str
    description: str | None = None
    mimeType: str | None = None
    model_config = ConfigDict(extra="allow")


class ResourceTemplate(BaseModel):
    uriTemplate: str
    name: str
    description: str | None = None
    mimeType: str | None = None
    model_config = ConfigDict(extra="allow")


class _ResourceContents(BaseModel):
    uri: AnyUrl
    mimeType: str | None = None
    model_config = ConfigDict(extra="allow")


class TextResourceContents(_ResourceContents):
    text: str


class ReadResourceResult(_Result):
    contents: list[TextResourceContents]


class ListResourcesResult(_PaginatedResult):
    resources: list[Resource]


class ListResourceTemplatesResult(_PaginatedResult):
    resourceTemplates: list[ResourceTemplate]


# --- Tools --------------------------------------------------------------------


class Tool(BaseModel):
    name: str
    description: str | None = None
    inputSchema: dict[str, Any]
    outputSchema: dict[str, Any] | None = None
    model_config = ConfigDict(extra="allow")


class ListToolsResult(_PaginatedResult):
    tools: list[Tool]


# --- Content ------------------------------------------------------------------


class TextContent(BaseModel):
    type: Literal["text"]
    text: str
    model_config = ConfigDict(extra="allow")


class ImageContent(BaseModel):
    type: Literal["image"]
    data: str
    mimeType: str
    model_config = ConfigDict(extra="allow")


class CallToolResult(_Result):
    content: list[Any]
    structuredContent: dict[str, Any] | None = None
    isError: bool = False


# --- Tasks --------------------------------------------------------------------

TaskStatus = Literal["working", "input_required", "completed", "failed", "cancelled"]


class Task(BaseModel):
    taskId: str
    status: TaskStatus
    statusMessage: str | None = None
    createdAt: datetime
    lastUpdatedAt: datetime
    ttl: int | None
    pollInterval: int | None = None
    model_config = ConfigDict(extra="allow")


class CreateTaskResult(_Result):
    task: Task


class GetTaskResult(_Result, Task):
    pass


class CancelTaskResult(_Result, Task):
    pass
