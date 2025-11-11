# pylint: disable=C0413
# __plotly_dash is for the "make sure you don't have a dash.py" check
# must come before any other imports.
__plotly_dash = True

from .dependencies import (  # noqa: F401,E402
    Input,  # noqa: F401,E402
    Output,  # noqa: F401,E402
    State,  # noqa: F401,E402
    ClientsideFunction,  # noqa: F401,E402
    MATCH,  # noqa: F401,E402
    ALL,  # noqa: F401,E402
    ALLSMALLER,  # noqa: F401,E402
)  # noqa: F401,E402
from . import development  # noqa: F401,E402
from . import exceptions  # noqa: F401,E402
from . import resources  # noqa: F401,E402
from . import dcc  # noqa: F401,E402
from . import html  # noqa: F401,E402
from . import dash_table  # noqa: F401,E402
from .version import __version__  # noqa: F401,E402
from ._callback_context import callback_context, set_props  # noqa: F401,E402
from ._callback import callback, clientside_callback  # noqa: F401,E402
from ._get_app import get_app  # noqa: F401,E402
from ._get_paths import (  # noqa: F401,E402
    get_asset_url,
    get_relative_path,
    strip_relative_path,
)
from .long_callback import (  # noqa: F401,E402
    CeleryManager,
    DiskcacheManager,
)

from ._pages import register_page, PAGE_REGISTRY as page_registry  # noqa: F401,E402
from .dash import (  # noqa: F401,E402
    Dash,
    no_update,
    page_container,
)
from ._patch import Patch  # noqa: F401,E402
from ._jupyter import jupyter_dash  # noqa: F401,E402
from ._hooks import hooks  # noqa: F401,E402

ctx = callback_context

# ---------------------------------------------------------------------------
# Backwards-compatibility shim for `dash.dcc`
#
# Some code (including the tests) expects attributes like `_js_dist` on
# `dash.dcc`, and the `dash_core_components` package expects to be able
# to import `__version__` from `dash.dcc`.
#
# The `dash/dcc` package in this repo is just a namespace stub, so we
# populate it with the bits that the ecosystem expects.
# ---------------------------------------------------------------------------

try:
    # Alias the namespace package imported above so we can mutate it.
    _dcc_module = dcc

    # Ensure `dash.dcc.__version__` exists before `dash_core_components`
    # tries to import it.
    if not hasattr(_dcc_module, "__version__"):
        _dcc_module.__version__ = __version__  # type: ignore[attr-defined]

    try:
        # Import the actual component package and mirror a few attributes.
        import dash_core_components as _dcc_pkg  # type: ignore[import]

        if hasattr(_dcc_pkg, "_js_dist"):
            _dcc_module._js_dist = _dcc_pkg._js_dist  # type: ignore[attr-defined]
        if hasattr(_dcc_pkg, "_css_dist"):
            _dcc_module._css_dist = _dcc_pkg._css_dist  # type: ignore[attr-defined]
    except Exception:
        # If `dash_core_components` isn't available for some reason, we
        # don't want Dash itself to fail to import.
        pass
except Exception:
    # If the namespace package `dash.dcc` itself is missing, also fail
    # quietly so basic imports continue to work.
    pass


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "nbextension",
            "dest": "dash",
            "require": "dash/main",
        }
    ]


__all__ = [
    "Input",
    "Output",
    "State",
    "ClientsideFunction",
    "MATCH",
    "ALLSMALLER",
    "ALL",
    "development",
    "exceptions",
    "dcc",
    "html",
    "dash_table",
    "__version__",
    "callback_context",
    "set_props",
    "callback",
    "clientside_callback",
    "get_app",
    "get_asset_url",
    "get_relative_path",
    "strip_relative_path",
    "CeleryManager",
    "DiskcacheManager",
    "register_page",
    "page_registry",
    "Dash",
    "no_update",
    "page_container",
    "Patch",
    "jupyter_dash",
    "hooks",
    "ctx",
]
