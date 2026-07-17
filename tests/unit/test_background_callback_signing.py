"""Unit tests for background-callback handle signing.

Covers both the low-level signing helpers and the end-to-end request handling
that closes two vulnerabilities in the DiskcacheManager background-callback flow:

1. Arbitrary process termination via a client-supplied ``job``/``oldJob``/
   ``cancelJob`` PID.
2. Arbitrary result-cache read/delete via a client-supplied ``cacheKey``.
"""
import re
import subprocess
import sys
import tempfile
import time

import pytest

from dash import _callback_signing as signing

diskcache = pytest.importorskip("diskcache")
psutil = pytest.importorskip("psutil")


# --------------------------------------------------------------------------- #
# Low-level signing helpers
# --------------------------------------------------------------------------- #
def test_sign_roundtrips():
    secret = b"s3cr3t"
    scope = signing.job_scope("renderer-1")
    signed = signing.sign(secret, scope, "4242")
    assert signed != "4242"
    assert signing.unsign(secret, scope, signed) == "4242"


def test_unsign_rejects_forged_value():
    secret = b"s3cr3t"
    scope = signing.job_scope("renderer-1")
    # A raw pid with no signature, and a made-up signature, both fail.
    assert signing.unsign(secret, scope, "9999") is None
    assert signing.unsign(secret, scope, "9999~deadbeef") is None


def test_unsign_rejects_wrong_scope_or_secret():
    secret = b"s3cr3t"
    signed = signing.sign(secret, signing.job_scope("renderer-1"), "4242")
    # Same value, different page load (end_id).
    assert signing.unsign(secret, signing.job_scope("renderer-2"), signed) is None
    # Same value, different field scope.
    assert signing.unsign(secret, signing.cache_scope("renderer-1"), signed) is None
    # Different secret.
    assert signing.unsign(b"other", signing.job_scope("renderer-1"), signed) is None


def test_unsign_handles_missing_token():
    secret = b"s3cr3t"
    scope = signing.job_scope(None)
    assert signing.unsign(secret, scope, None) is None
    assert signing.unsign(secret, scope, "") is None


# --------------------------------------------------------------------------- #
# End-to-end request handling
# --------------------------------------------------------------------------- #
def _make_app(cache_dir=None):
    from dash import Dash, DiskcacheManager, html, Input, Output

    manager = DiskcacheManager(diskcache.Cache(cache_dir or tempfile.mkdtemp()))
    app = Dash(__name__, background_callback_manager=manager)
    app.layout = html.Div([html.Button(id="btn"), html.Div(id="out")])

    @app.callback(
        Output("out", "children"),
        Input("btn", "n_clicks"),
        background=True,
        prevent_initial_call=True,
    )
    def slow(_n):
        return "done"

    return app, manager


_BODY = {
    "output": "out.children",
    "outputs": {"id": "out", "property": "children"},
    "inputs": [{"id": "btn", "property": "n_clicks", "value": 1}],
    "state": [],
    "changedPropIds": ["btn.n_clicks"],
}


def test_forged_oldjob_does_not_kill_process():
    app, _ = _make_app()
    client = app.server.test_client()
    client.get("/")

    victim = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        time.sleep(0.2)
        assert psutil.pid_exists(victim.pid)

        resp = client.post(f"/_dash-update-component?oldJob={victim.pid}", json=_BODY)
        assert resp.status_code in (200, 204)
        time.sleep(0.3)

        assert psutil.pid_exists(victim.pid)
        assert psutil.Process(victim.pid).status() != psutil.STATUS_ZOMBIE
    finally:
        victim.kill()


def test_forged_cachekey_is_not_read_or_deleted():
    app, manager = _make_app()
    client = app.server.test_client()
    client.get("/")

    manager.handle.set("operator-secret-key", {"secret": "topsecret"})
    resp = client.post(
        "/_dash-update-component?cacheKey=operator-secret-key&job=0", json=_BODY
    )
    body = resp.get_data(as_text=True)
    assert "topsecret" not in body
    assert manager.handle.get("operator-secret-key") == {"secret": "topsecret"}


def test_signed_handles_roundtrip_for_legit_client():
    app, _ = _make_app()
    client = app.server.test_client()

    index = client.get("/").get_data(as_text=True)
    cfg_match = re.search(r'id="_dash-config"[^>]*>(.*?)</script>', index, re.S)
    assert cfg_match, "config not found in index"
    import json

    end_id = json.loads(cfg_match.group(1)).get("end_id")
    assert end_id and signing._SEP in end_id

    setup = client.post(
        f"/_dash-update-component?endId={end_id}", json=_BODY
    ).get_json()
    signed_cache = setup["cacheKey"]
    signed_job = setup["job"]
    # Handles handed to the browser are signed, not raw.
    assert signing._SEP in signed_cache
    assert signing._SEP in signed_job

    result = None
    for _ in range(50):
        poll = client.post(
            f"/_dash-update-component?endId={end_id}"
            f"&cacheKey={signed_cache}&job={signed_job}",
            json=_BODY,
        ).get_json()
        response = (poll or {}).get("response") or {}
        if response.get("out", {}).get("children") == "done":
            result = "done"
            break
        time.sleep(0.2)

    assert result == "done"


# --------------------------------------------------------------------------- #
# Signing secret resolution
# --------------------------------------------------------------------------- #
def test_secret_key_takes_precedence():
    app, _ = _make_app()
    app.server.secret_key = "configured-secret"
    assert app._get_signing_secret() == b"configured-secret"


def test_secret_is_shared_across_workers_via_cache():
    # Two apps standing in for two workers, backed by the SAME diskcache dir and
    # neither with a secret_key, must derive the same signing secret.
    shared_dir = tempfile.mkdtemp()
    app_a, _ = _make_app(cache_dir=shared_dir)
    app_b, _ = _make_app(cache_dir=shared_dir)
    assert not app_a.server.secret_key
    assert not app_b.server.secret_key

    secret_a = app_a._get_signing_secret()
    secret_b = app_b._get_signing_secret()
    assert secret_a == secret_b
    assert isinstance(secret_a, bytes) and len(secret_a) >= 32


def test_secret_differs_for_unshared_caches():
    app_a, _ = _make_app()
    app_b, _ = _make_app()
    assert app_a._get_signing_secret() != app_b._get_signing_secret()


# --------------------------------------------------------------------------- #
# MCP tasks/* surface (same job/cacheKey round-trip, no end_id)
# --------------------------------------------------------------------------- #
def test_mcp_parse_task_id_accepts_signed_handles():
    from dash.mcp.tasks.tasks import parse_task_id

    app, _ = _make_app()
    secret = app._get_signing_secret()
    # MCP dispatch has no end_id, so handles are signed with a None scope.
    signed_job = signing.sign(secret, signing.job_scope(None), "4242")
    signed_cache = signing.sign(secret, signing.cache_scope(None), "abc123")
    task_id = f"mytool:{signed_job}:{signed_cache}:0"

    tool_name, job_id, cache_key, _created = parse_task_id(task_id)
    assert tool_name == "mytool"
    assert job_id == "4242"
    assert cache_key == "abc123"


def test_mcp_parse_task_id_rejects_forged_handles():
    from dash.mcp.tasks.tasks import parse_task_id
    from dash.mcp.types import MCPError

    _make_app()
    # A raw pid + cache key with no valid signature (what an attacker sends).
    with pytest.raises(MCPError):
        parse_task_id("mytool:9999:operator-secret-key:0")
