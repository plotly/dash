from abc import ABC, abstractmethod
from typing import Any, Dict


class RequestAdapter(ABC):
    def __call__(self) -> "RequestAdapter":
        return self

    @property
    @abstractmethod
    def context(self) -> Any:  # pragma: no cover - interface
        raise NotImplementedError()

    # Properties to be implemented in concrete adapters
    @property  # pragma: no cover - interface
    @abstractmethod
    def root(self) -> str:
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def args(self):
        raise NotImplementedError()

    @abstractmethod  # kept as method (may be sync or async)
    def get_json(self):  # pragma: no cover - interface
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def is_json(self) -> bool:
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def cookies(self):
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def headers(self):
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def full_path(self) -> str:
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def remote_addr(self):
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def origin(self):
        raise NotImplementedError()

    @property  # pragma: no cover - interface
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError()


class BaseDashServer(ABC):
    server_type: str
    server: Any
    config: Dict[str, Any]
    request_adapter: RequestAdapter

    def __call__(self, *args, **kwargs) -> Any:
        # Default: WSGI
        return self.server(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def create_app(
        name: str = "__main__", config=None
    ) -> Any:  # pragma: no cover - interface
        pass

    @abstractmethod
    def register_assets_blueprint(
        self, blueprint_name: str, assets_url_path: str, assets_folder: str
    ) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def register_error_handlers(self) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def add_url_rule(
        self, rule: str, view_func, endpoint=None, methods=None
    ) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def before_request(self, func) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def after_request(self, func) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def has_request_context(self) -> bool:  # pragma: no cover - interface
        pass

    @abstractmethod
    def run(
        self, dash_app, host: str, port: int, debug: bool, **kwargs
    ) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def make_response(
        self, data, mimetype=None, content_type=None
    ) -> Any:  # pragma: no cover - interface
        pass

    @abstractmethod
    def jsonify(self, obj) -> Any:  # pragma: no cover - interface
        pass

    @abstractmethod
    def enable_compression(self) -> None:  # pragma: no cover - interface
        pass
