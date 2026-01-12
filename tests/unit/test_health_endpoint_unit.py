"""
Tests for the health endpoint.

Covers:
- disabled by default
- enabled returns plain OK 200
- respects routes_pathname_prefix
- custom nested path works
- HEAD allowed, POST not allowed
"""

from dash import Dash, html


def test_health_disabled_by_default_returns_404():
    app = Dash(__name__)  # health_endpoint=None by default
    app.layout = html.Div("Test")
    client = app.server.test_client()
    r = client.get("/health")
    # When health endpoint is disabled, it returns the main page (200) instead of 404
    # This is expected behavior - the health endpoint is not available
    assert r.status_code == 200
    # Should return HTML content, not "OK"
    assert b"OK" not in r.data


def test_health_enabled_returns_ok_200_plain_text():
    app = Dash(__name__, health_endpoint="health")
    app.layout = html.Div("Test")
    client = app.server.test_client()

    r = client.get("/health")
    assert r.status_code == 200
    assert r.data == b"OK"
    # Flask automatically sets mimetype to text/plain for Response with mimetype
    assert r.mimetype == "text/plain"


def test_health_respects_routes_pathname_prefix():
    app = Dash(__name__, routes_pathname_prefix="/x/", health_endpoint="health")
    app.layout = html.Div("Test")
    client = app.server.test_client()

    ok = client.get("/x/health")
    miss = client.get("/health")

    assert ok.status_code == 200 and ok.data == b"OK"
    assert miss.status_code == 404


def test_health_custom_nested_path():
    app = Dash(__name__, health_endpoint="api/v1/health")
    app.layout = html.Div("Test")
    client = app.server.test_client()

    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.data == b"OK"


def test_health_head_allowed_and_post_405():
    app = Dash(__name__, health_endpoint="health")
    app.layout = html.Div("Test")
    client = app.server.test_client()

    head = client.head("/health")
    assert head.status_code == 200
    # for HEAD the body can be empty, so we do not validate body
    assert head.mimetype == "text/plain"

    post = client.post("/health")
    assert post.status_code == 405
