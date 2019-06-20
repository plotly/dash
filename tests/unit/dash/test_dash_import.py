import importlib
import types


def test_dddi001_dash_import_is_correct():
    imported = importlib.import_module("dash")
    assert isinstance(imported, types.ModuleType), "dash can be imported"

    with open("./dash/version.py") as fp:
        assert imported.__version__ in fp.read(), "version is consistent"

    assert (
        getattr(imported, "Dash").__name__ == "Dash"
    ), "access to main Dash class is valid"
