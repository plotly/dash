"""Regression tests for https://github.com/plotly/dash/issues/3818.

When the app module runs as ``__main__``/``__mp_main__`` (e.g. in the worker
process of uvicorn's reloader, which multiprocessing spawn re-executes as
``__mp_main__``), the server's import string ("app:server") imports the same
file a second time under its real name. Both executions run the module-level
``@callback`` decorators, duplicating every spec in GLOBAL_CALLBACK_LIST and
producing `Duplicate callback outputs` errors in the renderer.

``Dash.__init__`` now pre-registers the running main module in ``sys.modules``
under its canonical import name so the second import resolves to the module
already executed instead of re-executing the file.
"""
import importlib
import sys
import types

APP_SOURCE = """
from dash import Dash, html, dcc, callback, Output, Input

app = Dash(__name__)
app.layout = html.Div([
    dcc.Input(id="alias-in", value="hello"),
    html.Div(id="alias-out"),
])


@callback(Output("alias-out", "children"), Input("alias-in", "value"))
def update(value):
    return value


server = app.server
"""

MODULE_NAME = "dash_test_alias_app"


def _run_as(app_file, run_name):
    """Execute the app file the way multiprocessing spawn runs the main module."""
    module = types.ModuleType(run_name)
    module.__file__ = str(app_file)
    sys.modules[run_name] = module
    code = compile(app_file.read_text(), str(app_file), "exec")
    exec(code, module.__dict__)  # pylint: disable=exec-used
    return module


def test_main_module_alias_prevents_double_registration(tmp_path, monkeypatch):
    from dash import _callback

    app_file = tmp_path / f"{MODULE_NAME}.py"
    app_file.write_text(APP_SOURCE)
    monkeypatch.syspath_prepend(str(tmp_path))

    try:
        main_module = _run_as(app_file, "__mp_main__")

        # The import string import ("dash_test_alias_app:server") must resolve
        # to the module that already executed, not re-execute the file.
        imported = importlib.import_module(MODULE_NAME)
        assert imported is main_module

        specs = [
            spec
            for spec in _callback.GLOBAL_CALLBACK_LIST
            if spec["output"] == "alias-out.children"
        ]
        assert len(specs) == 1
        assert "alias-out.children" in _callback.GLOBAL_CALLBACK_MAP
    finally:
        sys.modules.pop("__mp_main__", None)
        sys.modules.pop(MODULE_NAME, None)
        _callback.GLOBAL_CALLBACK_MAP.pop("alias-out.children", None)
        _callback.GLOBAL_CALLBACK_LIST[:] = [
            spec
            for spec in _callback.GLOBAL_CALLBACK_LIST
            if spec["output"] != "alias-out.children"
        ]


PKG_APP_SOURCE = """
from dash import Dash, html, dcc, callback, Output, Input

app = Dash(__name__)
app.layout = html.Div([
    dcc.Input(id="pkg-alias-in", value="hello"),
    html.Div(id="pkg-alias-out"),
])


@callback(Output("pkg-alias-out", "children"), Input("pkg-alias-in", "value"))
def update(value):
    return value


server = app.server
"""

PKG_NAME = "dash_test_alias_pkg"


def test_main_module_alias_prevents_double_registration_nested(tmp_path, monkeypatch):
    """A main module nested in a package (``package/app.py``) is re-imported by
    its dotted import string (``package.app:server``), not its basename. The
    alias must be registered under the dotted name so that import resolves to
    the already-executed module instead of re-running the file."""
    from dash import _callback

    pkg_dir = tmp_path / PKG_NAME
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("")
    app_file = pkg_dir / "app.py"
    app_file.write_text(PKG_APP_SOURCE)

    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.chdir(tmp_path)

    import_string = f"{PKG_NAME}.app"

    try:
        main_module = _run_as(app_file, "__mp_main__")

        # The deployment import string ("dash_test_alias_pkg.app:server") must
        # resolve to the module that already executed, not re-execute the file.
        imported = importlib.import_module(import_string)
        assert imported is main_module

        specs = [
            spec
            for spec in _callback.GLOBAL_CALLBACK_LIST
            if spec["output"] == "pkg-alias-out.children"
        ]
        assert len(specs) == 1
        assert "pkg-alias-out.children" in _callback.GLOBAL_CALLBACK_MAP
    finally:
        sys.modules.pop("__mp_main__", None)
        sys.modules.pop(import_string, None)
        sys.modules.pop(PKG_NAME, None)
        _callback.GLOBAL_CALLBACK_MAP.pop("pkg-alias-out.children", None)
        _callback.GLOBAL_CALLBACK_LIST[:] = [
            spec
            for spec in _callback.GLOBAL_CALLBACK_LIST
            if spec["output"] != "pkg-alias-out.children"
        ]


def test_no_alias_when_names_collide(tmp_path, monkeypatch):
    """A main module whose basename matches an already-imported module must
    not clobber the existing sys.modules entry (e.g. a script named dash.py)."""
    app_file = tmp_path / "dash.py"
    app_file.write_text(APP_SOURCE)
    monkeypatch.syspath_prepend(str(tmp_path))

    import dash as real_dash
    from dash import _callback

    try:
        _run_as(app_file, "__mp_main__")
        assert sys.modules["dash"] is real_dash
    finally:
        sys.modules.pop("__mp_main__", None)
        _callback.GLOBAL_CALLBACK_MAP.pop("alias-out.children", None)
        _callback.GLOBAL_CALLBACK_LIST[:] = [
            spec
            for spec in _callback.GLOBAL_CALLBACK_LIST
            if spec["output"] != "alias-out.children"
        ]
