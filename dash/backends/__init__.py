import importlib
from .base_server import BaseDashServer


backend: BaseDashServer


_backend_imports = {
    "flask": ("dash.backends._flask", "FlaskDashServer"),
    "fastapi": ("dash.backends._fastapi", "FastAPIDashServer"),
    "quart": ("dash.backends._quart", "QuartDashServer"),
}


def get_backend(name: str) -> BaseDashServer:
    module_name, server_class = _backend_imports[name.lower()]
    try:
        module = importlib.import_module(module_name)
        server = getattr(module, server_class)
        return server
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
    "backend",
    "get_server_type",
]
