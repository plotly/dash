"""WebSocket callback support for Dash backend implementations.

This module provides the WebSocket callback infrastructure for real-time
bidirectional communication between Dash backends and the renderer.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import inspect
import json
import queue
import threading
import traceback
import uuid
from contextvars import copy_context
from typing import Any, Callable, Dict, TYPE_CHECKING, cast

import janus

from dash.exceptions import PreventUpdate, WebsocketDisconnected
from dash.types import CallbackExecutionBody
from dash._utils import to_json

if TYPE_CHECKING:
    import dash
    from .base_server import ResponseAdapter


SHUTDOWN_SIGNAL = "__shutdown__"
DISCONNECTED = "__disconnected__"


class DashWebsocketCallback:
    """WebSocket callback communication via queues.

    Provides methods for real-time bidirectional communication between
    the server and renderer during callback execution.

    Uses janus.Queue for outbound messages (serialized with to_json) and
    queue.Queue for get_props responses, enabling thread-safe communication
    between worker threads and the main event loop.
    """

    def __init__(
        self,
        pending_get_props: Dict[str, queue.Queue[Any]],
        renderer_id: str,
        outbound_queue: janus.Queue[str],
        shutdown_event: "threading.Event",
    ):
        """Initialize the WebSocket callback interface.

        Args:
            pending_get_props: Dict to track pending get_props requests.
                Values are queue.Queue instances for blocking response retrieval.
            renderer_id: The renderer ID for routing messages back to the correct client
            outbound_queue: janus.Queue for thread-safe outbound messaging.
            shutdown_event: Event signaling the websocket connection has closed.
        """
        self._pending_get_props = pending_get_props
        self._renderer_id = renderer_id
        self._outbound_queue = outbound_queue
        self._shutdown_event = shutdown_event

    @property
    def is_shutdown(self) -> bool:
        """Check if the websocket connection has been shut down."""
        return self._shutdown_event.is_set()

    def _queue_message(self, msg: dict) -> None:
        """Serialize and queue message for sending (thread-safe, non-blocking).

        Uses to_json for proper serialization of Dash components.
        Does nothing if the connection has been shut down.
        """
        if self._shutdown_event.is_set():
            return
        self._outbound_queue.sync_q.put_nowait(cast(str, to_json(msg)))

    async def set_prop(self, component_id: str, prop_name: str, value: Any) -> None:
        """Send immediate prop update to the client via WebSocket.

        Queues the message for the sender coroutine to send.

        Args:
            component_id: The component ID (string or stringified dict)
            prop_name: The property name to update
            value: The new value to set
        """
        msg = {
            "type": "set_props",
            "rendererId": self._renderer_id,
            "payload": {"componentId": component_id, "props": {prop_name: value}},
        }
        self._queue_message(msg)

    async def get_prop(
        self, component_id: str, prop_name: str, timeout: float = 30.0
    ) -> Any:
        """Request current prop value from the client.

        Uses queue.Queue for blocking wait in worker thread.

        Args:
            component_id: The component ID (string or stringified dict)
            prop_name: The property name to retrieve
            timeout: Timeout in seconds for waiting for response

        Returns:
            The current value of the property from the client's state

        Raises:
            WebsocketDisconnected: If the websocket connection has been closed.
            TimeoutError: If the response doesn't arrive within the timeout.
        """
        if self._shutdown_event.is_set():
            raise WebsocketDisconnected()

        request_id = str(uuid.uuid4())
        msg = {
            "type": "get_props_request",
            "rendererId": self._renderer_id,
            "requestId": request_id,
            "payload": {"componentId": component_id, "properties": [prop_name]},
        }

        # Use standard queue.Queue for response
        response_queue: queue.Queue = queue.Queue()
        self._pending_get_props[request_id] = response_queue

        # Queue the outbound request via janus sync interface
        self._queue_message(msg)

        # Wait for response (blocking is OK in worker thread)
        try:
            result = response_queue.get(timeout=timeout)
            if result == DISCONNECTED:
                raise WebsocketDisconnected()
            if result and prop_name in result:
                return result[prop_name]
            return None
        except queue.Empty as exc:
            raise TimeoutError(
                f"Timeout waiting for {component_id}.{prop_name}"
            ) from exc
        finally:
            self._pending_get_props.pop(request_id, None)


def create_ws_context(
    payload: CallbackExecutionBody,
    response_adapter: "ResponseAdapter",
    websocket_callback: DashWebsocketCallback,
):
    """Create callback context from WebSocket message.

    Args:
        payload: The callback payload
        response_adapter: The response adapter instance for the backend
        websocket_callback: The websocket callback instance for the backend

    Returns:
        AttributeDict with callback context
    """
    # pylint: disable=import-outside-toplevel
    from dash._utils import AttributeDict, inputs_to_dict

    g = AttributeDict({})
    g.inputs_list = payload.get("inputs", [])
    g.states_list = payload.get("state", [])
    g.outputs_list = payload.get("outputs", [])
    g.input_values = inputs_to_dict(g.inputs_list)
    g.state_values = inputs_to_dict(g.states_list)
    g.triggered_inputs = [
        {"prop_id": x, "value": g.input_values.get(x)}
        for x in payload.get("changedPropIds", [])
    ]
    g.dash_response = response_adapter
    g.updated_props = {}
    g.dash_websocket = websocket_callback

    return g


async def run_ws_sender(
    send_text: Callable[[str], Any], outbound_queue: janus.Queue[str]
) -> None:
    """Sender coroutine - drains queue and sends to WebSocket.

    This coroutine runs in the main event loop and handles sending
    messages that are queued by worker threads via janus.Queue.

    Messages are pre-serialized strings (using to_json).

    Args:
        send_text: Async function to send text data over WebSocket
        outbound_queue: janus.Queue instance for receiving messages (strings)
    """
    try:
        while True:
            msg = await outbound_queue.async_q.get()
            if msg == SHUTDOWN_SIGNAL:
                break
            await send_text(msg)
    except asyncio.CancelledError:
        pass


def make_callback_done_handler(
    outbound_queue: janus.Queue[str],
    pending_callbacks: Dict[str, concurrent.futures.Future],
    request_id: str,
    renderer_id: str,
    shutdown_event: threading.Event,
) -> Callable[[concurrent.futures.Future], None]:
    """Create a done callback handler for executor futures.

    This factory creates a callback that sends the result back through
    the WebSocket when an executor future completes.

    Args:
        outbound_queue: janus.Queue for sending responses
        pending_callbacks: Dict tracking pending callbacks for cleanup
        request_id: The request ID for the callback response
        renderer_id: The renderer ID for routing the response
        shutdown_event: Event signaling the websocket connection has closed.

    Returns:
        A callback function suitable for Future.add_done_callback()
    """

    def on_done(f: concurrent.futures.Future) -> None:
        try:
            if shutdown_event.is_set():
                return
            result = f.result()
            outbound_queue.sync_q.put_nowait(
                cast(
                    str,
                    to_json(
                        {
                            "type": "callback_response",
                            "rendererId": renderer_id,
                            "requestId": request_id,
                            "payload": result,
                        }
                    ),
                )
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            if shutdown_event.is_set():
                return
            outbound_queue.sync_q.put_nowait(
                cast(
                    str,
                    to_json(
                        {
                            "type": "callback_response",
                            "rendererId": renderer_id,
                            "requestId": request_id,
                            "payload": {
                                "status": "error",
                                "message": str(e),
                            },
                        }
                    ),
                )
            )
        finally:
            pending_callbacks.pop(request_id, None)

    return on_done


def run_callback_in_executor(
    executor: ThreadPoolExecutor,
    dash_app: "dash.Dash",
    payload: CallbackExecutionBody,
    ws_callback: DashWebsocketCallback,
    response_adapter: "ResponseAdapter",
) -> concurrent.futures.Future:
    """Submit callback to executor for thread pool execution.

    This function creates a callback execution context and runs it
    in a separate thread. Both sync and async callbacks are supported.

    Args:
        executor: ThreadPoolExecutor to submit the task to
        dash_app: The Dash application instance
        payload: The callback payload from WebSocket message
        ws_callback: WebSocket callback instance for set_prop/get_prop
        response_adapter: Response adapter for the backend

    Returns:
        Future representing the pending callback execution
    """

    def execute() -> dict:
        try:
            cb_ctx = create_ws_context(payload, response_adapter, ws_callback)
            # pylint: disable=protected-access
            func = dash_app._prepare_callback(cb_ctx, payload)
            args = dash_app._inputs_to_vals(  # pylint: disable=protected-access
                cb_ctx.inputs_list + cb_ctx.states_list
            )

            ctx = copy_context()
            partial_func = (
                dash_app._execute_callback(  # pylint: disable=protected-access
                    func, args, cb_ctx.outputs_list, cb_ctx
                )
            )

            # Run in new event loop (handles both sync and async callbacks)
            def run_callback():
                result = partial_func()
                if inspect.iscoroutine(result):
                    return asyncio.run(result)
                return result

            response_data = ctx.run(run_callback)
            return {"status": "ok", "data": json.loads(response_data)}

        except PreventUpdate:
            return {"status": "prevent_update"}
        except WebsocketDisconnected:
            return {"status": "prevent_update"}
        except Exception as e:  # pylint: disable=broad-exception-caught
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    return executor.submit(execute)
