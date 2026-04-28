"""Base server abstractions for Dash backend implementations.

This module provides abstract base classes and protocols that define the interface
for different web server backends (Flask, Quart, FastAPI, etc.) to integrate with Dash.
"""
from abc import ABC, abstractmethod
import asyncio
import json
import uuid
from typing import Any, Dict, Type, TypeVar, Generic, Protocol, TYPE_CHECKING


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


class DashWebsocketCallback(ABC):
    """Abstract base for WebSocket-based callback communication.

    Provides methods for real-time bidirectional communication between
    the server and renderer during callback execution.

    Subclasses must implement _send and _close_websocket for their
    specific WebSocket implementation.
    """

    def __init__(
        self,
        pending_get_props: Dict[str, asyncio.Future],
        renderer_id: str = "",
    ):
        """Initialize the WebSocket callback interface.

        Args:
            pending_get_props: Dict to track pending get_props requests
            renderer_id: The renderer ID for routing messages back to the correct client
        """
        self._pending_get_props = pending_get_props
        self._renderer_id = renderer_id

    @abstractmethod
    async def _send(self, data: str) -> None:
        """Send string data over the WebSocket. Must be implemented by subclasses."""

    @abstractmethod
    async def _close_websocket(self, code: int, reason: str) -> None:
        """Close the WebSocket connection. Must be implemented by subclasses."""

    async def _send_plotly_json(self, value: Any) -> None:
        """Serialize and send value to client using plotly JSON serialization.

        Uses to_json for full compatibility with all supported prop types,
        then sends the string directly to avoid double serialization.
        """
        # pylint: disable=import-outside-toplevel
        from dash._utils import to_json

        serialized = to_json(value)
        await self._send(serialized)

    async def _send_json(self, data: dict) -> None:
        """Send JSON dict over the WebSocket."""
        await self._send(json.dumps(data))

    async def set_prop(self, component_id: str, prop_name: str, value: Any) -> None:
        """Send immediate prop update to the client via WebSocket.

        Args:
            component_id: The component ID (string or stringified dict)
            prop_name: The property name to update
            value: The new value to set
        """
        payload = {
            "type": "set_props",
            "rendererId": self._renderer_id,
            "payload": {"componentId": component_id, "props": {prop_name: value}},
        }
        await self._send_plotly_json(payload)

    async def get_prop(self, component_id: str, prop_name: str) -> Any:
        """Request current prop value from the client.

        Args:
            component_id: The component ID (string or stringified dict)
            prop_name: The property name to retrieve

        Returns:
            The current value of the property from the client's state
        """
        request_id = str(uuid.uuid4())

        # Create a future to wait for the response
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending_get_props[request_id] = future

        # Send the request
        await self._send_json(
            {
                "type": "get_props_request",
                "rendererId": self._renderer_id,
                "requestId": request_id,
                "payload": {"componentId": component_id, "properties": [prop_name]},
            }
        )

        # Wait for the response with timeout
        try:
            result = await asyncio.wait_for(future, timeout=30.0)
            if result and prop_name in result:
                return result[prop_name]
            return None
        except asyncio.TimeoutError as exc:
            self._pending_get_props.pop(request_id, None)
            raise TimeoutError(
                f"Timeout waiting for get_prop response for {component_id}.{prop_name}"
            ) from exc

    async def close(self, code: int = 1000, reason: str = "Connection closed") -> None:
        """Close the WebSocket connection.

        Args:
            code: WebSocket close code (default 1000 for normal closure)
            reason: Human-readable reason for closing
        """
        await self._close_websocket(code, reason)


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
