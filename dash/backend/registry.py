import importlib

_backend_imports = {
    'flask': ('dash.backend.flask', 'FlaskDashServer'),
    'fastapi': ('dash.backend.fastapi', 'FastAPIDashServer'),
    'quart': ('dash.backend.quart', 'QuartDashServer'),
}

def register_backend(name, module_path, class_name):
    """Register a new backend by name."""
    _backend_imports[name.lower()] = (module_path, class_name)

def get_backend(name):
    try:
        module_name, class_name = _backend_imports[name.lower()]
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except KeyError as e:
        raise ValueError(f"Unknown backend: {name}") from e
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}' for backend '{name}': {e}") from e
    except AttributeError as e:
        raise AttributeError(f"Module '{module_name}' does not have class '{class_name}' for backend '{name}': {e}") from e

