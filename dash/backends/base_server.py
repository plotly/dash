"""Base server abstractions for Dash backend implementations.

This module provides abstract base classes and protocols that define the interface
for different web server backends (Flask, Quart, FastAPI, etc.) to integrate with Dash.
"""
from abc import ABC, abstractmethod
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import inspect
import json
import queue
import traceback
import uuid
from contextvars import copy_context
from typing import (
    Any,
    Callable,
    Dict,
    Type,
    TypeVar,
    Generic,
    Protocol,
    TYPE_CHECKING,
    cast,
)

import janus

from dash.exceptions import PreventUpdate
from dash._utils import to_json

if TYPE_CHECKING:
    import dash


class _ServerCallable(Protocol):  # pylint: disable=too-few-public-methods
    """Protocol for callable server instances.

    Defines the interface for server objects that can be called as WSGI/ASGI applications.
    """

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError


ServerType = TypeVar("ServerType", bound=_ServerCallable)


class RequestAdapter(ABC):
    """Abstract adapter for normalizing HTTP request objects across different server backends.

    This adapter provides a unified interface for accessing request data regardless of
    the underlying web framework (Flask, Quart, FastAPI, etc.). Concrete implementations
    wrap framework-specific request objects and expose their data through these properties.
    """

    def __call__(self) -> "RequestAdapter":
        return self

    @property
    @abstractmethod
    def context(self) -> Any:  # pragma: no cover - interface
        """Get the framework-specific request context object."""
        raise NotImplementedError()

    # Properties to be implemented in concrete adapters
    @property  # pragma: no cover - interface
    @abstractmethod
    def root(self) -> str:
        """Get the application root path."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def args(self):
        """Get the request query string arguments."""
        raise NotImplementedError()

    @abstractmethod  # kept as method (may be sync or async)
    def get_json(self):  # pragma: no cover - interface
        """Get the parsed JSON body of the request.

        May be synchronous or asynchronous depending on the backend.
        """
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def is_json(self) -> bool:
        """Check if the request has a JSON content type."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def cookies(self):
        """Get the request cookies."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def headers(self):
        """Get the request headers."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def full_path(self) -> str:
        """Get the full request path including query string."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def url(self) -> str:
        """Get the full request URL."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def remote_addr(self):
        """Get the remote client IP address."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def origin(self):
        """Get the Origin header value."""
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def path(self) -> str:
        """Get the request path without query string."""
        raise NotImplementedError()


class ResponseAdapter:
    """Adapter for server response objects to allow setting data."""

    def __init__(self):
        # Accept a pre-made response object
        self._headers = {}
        self._cookies = {}

    @property
    def callback_response(self):
        """Get the response object to be returned from a callback."""
        # This method should be overridden in concrete implementations to return the appropriate response object
        raise NotImplementedError()

    def set_cookie(self, key, value="", **kwargs):
        """Set a cookie in the response (like Flask's set_cookie)."""
        # Store as a tuple: (value, kwargs)
        self._cookies[key] = (value, kwargs)

    def append_header(self, key, value):
        """Add a header to the response (like Flask's headers.add)."""
        # Allow multiple values per header key
        if key in self._headers:
            if isinstance(self._headers[key], list):
                self._headers[key].append(value)
            else:
                self._headers[key] = [self._headers[key], value]
        else:
            self._headers[key] = value

    def set_header(self, key, value):
        """Set a header to the response."""
        self._headers[key] = [value]

    def set_response(self, **kwargs):
        """Set the response data if supported by the response object."""
        raise NotImplementedError()


class BaseDashServer(ABC, Generic[ServerType]):
    """Abstract base class for Dash server backend implementations.

    This class defines the interface that all server backends must implement to
    work with Dash. Concrete implementations exist for Flask, Quart, FastAPI, and
    other web frameworks.

    Attributes:
        server_type: String identifier for the server backend (e.g., 'flask', 'quart')
        server: The underlying server instance
        config: Configuration dictionary for the server
        request_adapter: RequestAdapter class for normalizing requests
    """

    server_type: str
    server: ServerType
    config: Dict[str, Any]
    request_adapter: Type[RequestAdapter]
    response_adapter: Type[ResponseAdapter]
    websocket_capability: bool = False

    def __init__(self, server: ServerType) -> None:
        """Initialize the server wrapper.

        Args:
            server: The underlying server instance to wrap
        """
        super().__init__()
        self.server = server
        self._callback_executor: ThreadPoolExecutor | None = None

    def get_callback_executor(
        self, max_workers: int | None = None
    ) -> ThreadPoolExecutor:
        """Get or create the thread pool executor for callback execution.

        Args:
            max_workers: Maximum number of worker threads. If None, uses default.

        Returns:
            ThreadPoolExecutor instance for running callbacks.
        """
        if self._callback_executor is None:
            self._callback_executor = ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="dash-callback-"
            )
        return self._callback_executor

    def shutdown_executor(self, wait: bool = True) -> None:
        """Shutdown the callback executor.

        Args:
            wait: If True, wait for pending tasks to complete.
        """
        if self._callback_executor is not None:
            self._callback_executor.shutdown(wait=wait)
            self._callback_executor = None

    def __call__(self, *args, **kwargs) -> Any:
        """Make the server wrapper callable as a WSGI/ASGI application.

        Delegates to the underlying server instance.
        """
        # Default: WSGI
        return self.server(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def create_app(
        name: str = "__main__", config=None
    ) -> Any:  # pragma: no cover - interface
        """Create a new server application instance.

        Args:
            name: Application name, defaults to '__main__'
            config: Configuration dictionary or object

        Returns:
            The server application instance
        """

    @abstractmethod
    def register_assets_blueprint(
        self, blueprint_name: str, assets_url_path: str, assets_folder: str
    ) -> None:  # pragma: no cover - interface
        """Register a blueprint/router for serving static assets.

        Args:
            blueprint_name: Name for the assets blueprint
            assets_url_path: URL path prefix for assets
            assets_folder: Filesystem path to the assets folder
        """

    @abstractmethod
    def register_error_handlers(self) -> None:  # pragma: no cover - interface
        """Register error handlers for common HTTP errors."""

    @abstractmethod
    def add_url_rule(
        self, rule: str, view_func, endpoint=None, methods=None
    ) -> None:  # pragma: no cover - interface
        """Add a URL routing rule.

        Args:
            rule: URL pattern/route
            view_func: View function to handle the route
            endpoint: Optional endpoint name
            methods: Optional list of HTTP methods (e.g., ['GET', 'POST'])
        """

    @abstractmethod
    def before_request(self, func) -> None:  # pragma: no cover - interface
        """Register a function to run before each request.

        Args:
            func: Function to execute before request handling
        """

    @abstractmethod
    def after_request(self, func) -> None:  # pragma: no cover - interface
        """Register a function to run after each request.

        Args:
            func: Function to execute after request handling
        """

    @abstractmethod
    def has_request_context(self) -> bool:  # pragma: no cover - interface
        """Check if currently executing within a request context.

        Returns:
            True if in request context, False otherwise
        """

    @abstractmethod
    def run(
        self, dash_app, host: str, port: int, debug: bool, **kwargs
    ) -> None:  # pragma: no cover - interface
        """Start the development server.

        Args:
            dash_app: The Dash application instance
            host: Hostname to bind to
            port: Port number to bind to
            debug: Enable debug mode
            **kwargs: Additional server-specific arguments
        """

    @abstractmethod
    def make_response(
        self,
        data,
        mimetype=None,
        content_type=None,
        status=None,
    ) -> Any:  # pragma: no cover - interface
        """Create an HTTP response object.

        Args:
            data: Response body data
            mimetype: MIME type of the response
            content_type: Content-Type header value
            status: HTTP status code

        Returns:
            Server-specific response object
        """

    @abstractmethod
    def jsonify(self, obj) -> Any:  # pragma: no cover - interface
        """Convert an object to a JSON response.

        Args:
            obj: Object to serialize to JSON

        Returns:
            JSON response object
        """

    @abstractmethod
    def enable_compression(self) -> None:  # pragma: no cover - interface
        """Enable HTTP compression for responses."""

    @abstractmethod
    def register_prune_error_handler(self, secret: str, prune_errors: bool) -> None:
        """Register handler for pruning error stack traces.

        Args:
            secret: Secret key for error handling
            prune_errors: Whether to prune stack traces in errors
        """

    @abstractmethod
    def register_timing_hooks(self, first_run: bool) -> None:
        """Register hooks for timing request/response cycles.

        Args:
            first_run: Whether this is the first run of the application
        """

    @abstractmethod
    def register_callback_api_routes(self, callback_api_paths):
        """Register routes for Dash callback API endpoints.

        Args:
            callback_api_paths: Paths for callback API endpoints
        """

    @abstractmethod
    def setup_component_suites(self, dash_app: "dash.Dash") -> str:
        """Set up routes for serving component JavaScript bundles.

        Args:
            dash_app: The Dash application instance

        Returns:
            Base path for component suites
        """

    @abstractmethod
    def serve_callback(self, dash_app: "dash.Dash"):
        """Set up the callback handling endpoint.

        Args:
            dash_app: The Dash application instance
        """

    @abstractmethod
    def setup_index(self, dash_app: "dash.Dash"):
        """Set up the index/root route for serving the main application.

        Args:
            dash_app: The Dash application instance
        """

    @abstractmethod
    def setup_catchall(self, dash_app: "dash.Dash"):
        """Set up the catchall route for client-side routing.

        Args:
            dash_app: The Dash application instance
        """

    def setup_backend(self, dash_app: "dash.Dash"):
        """Perform any additional backend-specific setup.

        Override this method in concrete implementations to provide custom setup logic.

        Args:
            dash_app: The Dash application instance
        """

    def serve_websocket_callback(self, dash_app: "dash.Dash"):
        """Set up the WebSocket endpoint for callback handling.

        Override this method in backends that support WebSocket callbacks.

        Args:
            dash_app: The Dash application instance
        """


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
    ):
        """Initialize the WebSocket callback interface.

        Args:
            pending_get_props: Dict to track pending get_props requests.
                Values are queue.Queue instances for blocking response retrieval.
            renderer_id: The renderer ID for routing messages back to the correct client
            outbound_queue: janus.Queue for thread-safe outbound messaging.
        """
        self._pending_get_props = pending_get_props
        self._renderer_id = renderer_id
        self._outbound_queue = outbound_queue

    def _queue_message(self, msg: dict) -> None:
        """Serialize and queue message for sending (thread-safe, non-blocking).

        Uses to_json for proper serialization of Dash components.
        """
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
        """
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
    payload: dict,
    response_adapter: ResponseAdapter,
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


SHUTDOWN_SIGNAL = "__shutdown__"


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
) -> Callable[[concurrent.futures.Future], None]:
    """Create a done callback handler for executor futures.

    This factory creates a callback that sends the result back through
    the WebSocket when an executor future completes.

    Args:
        outbound_queue: janus.Queue for sending responses
        pending_callbacks: Dict tracking pending callbacks for cleanup
        request_id: The request ID for the callback response
        renderer_id: The renderer ID for routing the response

    Returns:
        A callback function suitable for Future.add_done_callback()
    """

    def on_done(f: concurrent.futures.Future) -> None:
        try:
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
    payload: dict,
    ws_callback: DashWebsocketCallback,
    response_adapter: ResponseAdapter,
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    return executor.submit(execute)
