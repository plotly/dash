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
    except KeyError:
        raise ValueError(f"Unknown backend: {name}")
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not import backend '{name}': {e}")

