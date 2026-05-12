"""Handler functions for MCP tasks/* methods."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Literal

from mcp.types import CancelTaskResult, CreateTaskResult, GetTaskResult, Task

from dash import get_app
from dash.mcp.primitives.tools.results import format_callback_response
from dash.mcp.types import MCPError


def parse_task_id(task_id: str) -> tuple[str, str, str, datetime]:
    """Parse a taskId into (tool_name, job_id, cache_key, created_at)."""
    tool_name, job_id, rest = task_id.split(":", 2)
    cache_key, created_epoch = rest.rsplit(":", 1)
    created_at = datetime.fromtimestamp(int(created_epoch), tz=timezone.utc)
    return tool_name, job_id, cache_key, created_at


def _get_callback_manager(tool_name: str):
    """Resolve the background callback manager for a specific MCP tool."""
    adapter = get_app().mcp_callback_map.find_by_tool_name(tool_name)
    if adapter is None:
        return None
    # pylint: disable-next=protected-access
    return adapter._cb_info.get("manager")


def create_task(dispatch_response: dict[str, Any], callback) -> CreateTaskResult:
    """Create a Task from a background callback's initial dispatch response."""
    cache_key = dispatch_response["cacheKey"]
    job_id = str(dispatch_response["job"])
    now = datetime.now(timezone.utc)
    # taskId encodes creation time so subsequent polls return a stable
    # createdAt without server-side storage (works across gunicorn workers).
    task_id = f"{callback.tool_name}:{job_id}:{cache_key}:{int(now.timestamp())}"
    # pylint: disable-next=protected-access
    interval = callback._cb_info.get("background", {}).get("interval", 1000)
    return CreateTaskResult(
        task=Task(
            taskId=task_id,
            status="working",
            createdAt=now,
            lastUpdatedAt=now,
            ttl=None,
            pollInterval=interval,
        ),
    )


def get_task(task_id: str) -> GetTaskResult:
    """Handle tasks/get — derive status from the callback manager."""
    tool_name, job_id, cache_key, created_at = parse_task_id(task_id)

    manager = _get_callback_manager(tool_name)
    if manager is None:
        return GetTaskResult(
            taskId=task_id,
            status="failed",
            statusMessage="No background callback manager configured.",
            createdAt=created_at,
            lastUpdatedAt=datetime.now(timezone.utc),
            ttl=None,
        )

    running = manager.job_running(job_id)
    progress = manager.get_progress(cache_key)

    status: Literal["working", "completed", "failed"]
    if running:
        status = "working"
    elif manager.result_ready(cache_key):
        status = "completed"
    else:
        status = "failed"

    adapter = get_app().mcp_callback_map.find_by_tool_name(tool_name)
    interval = None
    if adapter is not None:
        # pylint: disable-next=protected-access
        interval = adapter._cb_info.get("background", {}).get("interval", 1000)

    return GetTaskResult(
        taskId=task_id,
        status=status,
        statusMessage=str(progress) if progress else None,
        createdAt=created_at,
        lastUpdatedAt=datetime.now(timezone.utc),
        ttl=manager.expire * 1000 if manager.expire else None,
        pollInterval=interval,
    )


def get_task_result(task_id: str) -> Any:
    """Handle tasks/result — retrieve and format the callback result.

    Mirrors the Dash renderer: calls get_result() which clears from cache.
    """
    tool_name, job_id, cache_key, _created_at = parse_task_id(task_id)

    manager = _get_callback_manager(tool_name)
    if manager is None:
        raise MCPError("No background callback manager configured.")

    # Mirror the renderer: dispatch with cacheKey/job query params.
    # The framework handles result retrieval, wrapping, and cleanup.
    adapter = get_app().mcp_callback_map.find_by_tool_name(tool_name)
    body = adapter.as_callback_body({})
    app = get_app()

    with app.server.test_request_context(
        f"/_dash-update-component?cacheKey={cache_key}&job={job_id}",
        method="POST",
        data=json.dumps(body, default=str),
        content_type="application/json",
    ):
        response = app.dispatch()

    response_data = json.loads(response.get_data(as_text=True))

    if "response" not in response_data:
        raise MCPError(
            "Task result not ready. Poll tasks/get until status is 'completed'."
        )

    return format_callback_response(response_data, adapter)


def cancel_task(task_id: str) -> Any:
    """Handle tasks/cancel — terminate the background job.

    Same underlying mechanism as the renderer's cancelJob query param.
    """
    tool_name, job_id, _cache_key, created_at = parse_task_id(task_id)

    manager = _get_callback_manager(tool_name)
    if manager is None:
        raise MCPError("No background callback manager configured.")

    manager.terminate_job(job_id)

    return CancelTaskResult(
        taskId=task_id,
        status="cancelled",
        createdAt=created_at,
        lastUpdatedAt=datetime.now(timezone.utc),
        ttl=manager.expire * 1000 if manager.expire else None,
    )
