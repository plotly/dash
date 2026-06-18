"""Callback introspection utilities for MCP tools."""

from __future__ import annotations

import json
from contextvars import copy_context
from typing import TYPE_CHECKING, Any

from dash import get_app
from dash.mcp.types import CallbackExecutionError
from dash.types import CallbackExecutionResponse

if TYPE_CHECKING:
    from .callback_adapter import CallbackAdapter


def run_callback(
    callback: CallbackAdapter, kwargs: dict[str, Any]
) -> CallbackExecutionResponse:
    """Execute a callback via the framework.

    Must be called from inside an active request handler; the backend's
    request adapter reads cookies/headers/args from the current request.
    """
    body = callback.as_callback_body(kwargs)
    app = get_app()

    try:
        # pylint: disable=protected-access
        cb_ctx = app._initialize_context(body)
        func = app._prepare_callback(cb_ctx, body)
        args = app._inputs_to_vals(cb_ctx.inputs_list + cb_ctx.states_list)
        ctx = copy_context()
        partial_func = app._execute_callback(func, args, cb_ctx.outputs_list, cb_ctx)
        response_text = ctx.run(partial_func)
    except Exception as err:
        raise CallbackExecutionError(
            f"Callback {callback.output_id} failed: {err}"
        ) from err

    return json.loads(response_text)
