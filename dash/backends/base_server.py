"""Base server abstractions for Dash backend implementations.

This module provides abstract base classes and protocols that define the interface
for different web server backends (Flask, Quart, FastAPI, etc.) to integrate with Dash.
"""
from abc import ABC, abstractmethod
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
        pass

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
        pass

    @abstractmethod
    def register_error_handlers(self) -> None:  # pragma: no cover - interface
        """Register error handlers for common HTTP errors."""
        pass

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
        pass

    @abstractmethod
    def before_request(self, func) -> None:  # pragma: no cover - interface
        """Register a function to run before each request.

        Args:
            func: Function to execute before request handling
        """
        pass

    @abstractmethod
    def after_request(self, func) -> None:  # pragma: no cover - interface
        """Register a function to run after each request.

        Args:
            func: Function to execute after request handling
        """
        pass

    @abstractmethod
    def has_request_context(self) -> bool:  # pragma: no cover - interface
        """Check if currently executing within a request context.

        Returns:
            True if in request context, False otherwise
        """
        pass

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
        pass

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
        pass

    @abstractmethod
    def jsonify(self, obj) -> Any:  # pragma: no cover - interface
        """Convert an object to a JSON response.

        Args:
            obj: Object to serialize to JSON

        Returns:
            JSON response object
        """
        pass

    @abstractmethod
    def enable_compression(self) -> None:  # pragma: no cover - interface
        """Enable HTTP compression for responses."""
        pass

    @abstractmethod
    def register_prune_error_handler(self, secret: str, prune_errors: bool) -> None:
        """Register handler for pruning error stack traces.

        Args:
            secret: Secret key for error handling
            prune_errors: Whether to prune stack traces in errors
        """
        pass

    @abstractmethod
    def register_timing_hooks(self, first_run: bool) -> None:
        """Register hooks for timing request/response cycles.

        Args:
            first_run: Whether this is the first run of the application
        """
        pass

    @abstractmethod
    def register_callback_api_routes(self, callback_api_paths):
        """Register routes for Dash callback API endpoints.

        Args:
            callback_api_paths: Paths for callback API endpoints
        """
        pass

    @abstractmethod
    def setup_component_suites(self, dash_app: "dash.Dash") -> str:
        """Set up routes for serving component JavaScript bundles.

        Args:
            dash_app: The Dash application instance

        Returns:
            Base path for component suites
        """
        pass

    @abstractmethod
    def serve_callback(self, dash_app: "dash.Dash"):
        """Set up the callback handling endpoint.

        Args:
            dash_app: The Dash application instance
        """
        pass

    @abstractmethod
    def setup_index(self, dash_app: "dash.Dash"):
        """Set up the index/root route for serving the main application.

        Args:
            dash_app: The Dash application instance
        """
        pass

    @abstractmethod
    def setup_catchall(self, dash_app: "dash.Dash"):
        """Set up the catchall route for client-side routing.

        Args:
            dash_app: The Dash application instance
        """
        pass

    def setup_backend(self, dash_app: "dash.Dash"):
        """Perform any additional backend-specific setup.

        Override this method in concrete implementations to provide custom setup logic.

        Args:
            dash_app: The Dash application instance
        """
