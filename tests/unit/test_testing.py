import warnings

import pluggy
import pytest

from dash.testing import ignore_register_page, plugin
from dash import register_page


def test_tst001_ignore_register_page():
    with ignore_register_page():
        register_page("/")


def test_tst002_pytest_addhooks_uses_hookimpl():
    opts = pluggy.PluginManager("pytest").parse_hookimpl_opts(plugin, "pytest_addhooks")
    assert opts is not None and opts.get("tryfirst") is True

    pm = pytest.PytestPluginManager()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pm.register(plugin, name="dash_testing_hookimpl_check")
    pm.unregister(name="dash_testing_hookimpl_check")

    hook_warnings = [w for w in caught if "pytest_addhooks" in str(w.message)]
    assert hook_warnings == []
