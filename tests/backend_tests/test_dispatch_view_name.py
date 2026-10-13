"""Regression tests for the callback dispatch view function identity.

Integrations such as Flask-WTF's ``CSRFProtect`` exempt views by their
fully-qualified name (``f"{view.__module__}.{view.__name__}"``). Prior to the
backend refactor the dispatch view was ``dash.dash.Dash.dispatch``, so users
exempt it with ``csrf._exempt_views.add("dash.dash.dispatch")``. The refactor
must keep exposing that same name so those exemptions keep working.

See https://github.com/plotly/dash/issues/3827
"""
import pytest
from dash import Dash, html


def _dispatch_view_dest(app):
    view = app.server.view_functions["/_dash-update-component"]
    return f"{view.__module__}.{view.__name__}"


def test_flask_dispatch_view_name():
    app = Dash(__name__)
    app.layout = html.Div()
    assert _dispatch_view_dest(app) == "dash.dash.dispatch"


def test_quart_dispatch_view_name():
    pytest.importorskip("quart")
    app = Dash(__name__, backend="quart")
    app.layout = html.Div()
    view = app.server.view_functions["/_dash-update-component"]
    assert f"{view.__module__}.{view.__name__}" == "dash.dash.dispatch"
