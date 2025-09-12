from abc import ABC, abstractmethod
from typing import Any


class BaseDashServer(ABC):
    def __call__(self, server, *args, **kwargs) -> Any:
        # Default: WSGI
        return server(*args, **kwargs)

    @abstractmethod
    def create_app(self, name: str = "__main__", config=None) -> Any:  # pragma: no cover - interface
        pass

    @abstractmethod
    def register_assets_blueprint(
        self, app, blueprint_name: str, assets_url_path: str, assets_folder: str
    ) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def register_error_handlers(self, app) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def add_url_rule(self, app, rule: str, view_func, endpoint=None, methods=None) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def before_request(self, app, func) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def after_request(self, app, func) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def run(self, app, host: str, port: int, debug: bool, **kwargs) -> None:  # pragma: no cover - interface
        pass

    @abstractmethod
    def make_response(self, data, mimetype=None, content_type=None) -> Any:  # pragma: no cover - interface
        pass

    @abstractmethod
    def jsonify(self, obj) -> Any:  # pragma: no cover - interface
        pass

    @abstractmethod
    def get_request_adapter(self) -> Any:  # pragma: no cover - interface
        pass
