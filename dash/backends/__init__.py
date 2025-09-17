from .base_server import BaseDashServer, RequestAdapter

from typing import Literal, Any
import importlib


request_adapter: RequestAdapter
backend: BaseDashServer


_backend_imports = {
    "flask": ("dash.backends._flask", "FlaskDashServer", "FlaskRequestAdapter"),
    "fastapi": ("dash.backends._fastapi", "FastAPIDashServer", "FastAPIRequestAdapter"),
    "quart": ("dash.backends._quart", "QuartDashServer", "QuartRequestAdapter"),
}


request_adapter: RequestAdapter
backend: BaseDashServer


def get_backend(
    name: Literal["flask", "fastapi", "quart"] | str
) -> tuple[BaseDashServer, RequestAdapter]:
    module_name, server_class, request_class = _backend_imports[name.lower()]
    try:
        module = importlib.import_module(module_name)
        server = getattr(module, server_class)
        request_adapter = getattr(module, request_class)
        return server, request_adapter
    except KeyError as e:
        raise ValueError(f"Unknown backend: {name}") from e
    except ImportError as e:
        raise ImportError(
            f"Could not import module '{module_name}' for backend '{name}': {e}"
        ) from e
    except AttributeError as e:
        raise AttributeError(
            f"Module '{module_name}' does not have class '{server_class}' for backend '{name}': {e}"
        ) from e


def _is_flask_instance(obj):
    try:
        # pylint: disable=import-outside-toplevel
        from flask import Flask

        return isinstance(obj, Flask)
    except ImportError:
        return False


def _is_fastapi_instance(obj):
    try:
        # pylint: disable=import-outside-toplevel
        from fastapi import FastAPI

        return isinstance(obj, FastAPI)
    except ImportError:
        return False


def _is_quart_instance(obj):
    try:
        # pylint: disable=import-outside-toplevel
        from quart import Quart

        return isinstance(obj, Quart)
    except ImportError:
        return False


def get_server_type(server):
    if _is_flask_instance(server):
        return "flask"
    if _is_quart_instance(server):
        return "quart"
    if _is_fastapi_instance(server):
        return "fastapi"
    raise ValueError("Invalid backend argument")


__all__ = [
    "get_backend",
    "request_adapter",
    "backend",
    "get_server_type",
]
