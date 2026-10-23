"""The MCP server caches tool descriptions and initial values. With
``cache_by`` keyed on the user, values computed for one user are not served to
another."""

import base64
import json

import flask
import pytest

from dash import Dash, Input, Output, dcc, html
from dash.mcp import configure_mcp_server

USERS = {"alice": "pw-a", "bob": "pw-b"}
SECRETS = {"alice": "alice-secret-111", "bob": "bob-secret-222"}


def _auth_header(user):
    token = base64.b64encode(f"{user}:{USERS[user]}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def _add_basic_auth(app):
    @app.server.before_request
    def basic_auth():
        auth = flask.request.authorization
        if not auth or USERS.get(auth.username) != auth.password:
            return flask.Response("auth required", 401)
        flask.g.user = auth.username
        return None


def _rpc(client, user, method, params=None):
    r = client.post(
        "/_mcp",
        headers=_auth_header(user),
        data=json.dumps(
            {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
        ),
    )
    assert r.status_code == 200
    return json.dumps(r.get_json())


def test_mcpi001_callback_initial_output_is_per_user():
    app = Dash(__name__, enable_mcp=True)
    configure_mcp_server(cache_by=lambda: flask.g.user)
    app.layout = html.Div(
        [
            dcc.Location(id="url"),
            html.Div(id="profile"),
            dcc.Input(id="note", value="hi"),
            html.Div(id="summary"),
        ]
    )
    _add_basic_auth(app)

    @app.callback(Output("profile", "children"), Input("url", "pathname"))
    def load_profile(_pathname):
        return f"record: {SECRETS[flask.g.user]}"

    @app.callback(
        Output("summary", "children"),
        Input("profile", "children"),
        Input("note", "value"),
    )
    def summarize(profile, note):
        return f"{profile} / {note}"

    client = app.server.test_client()
    get_profile = {
        "name": "get_dash_component",
        "arguments": {"component_id": "profile"},
    }

    alice = _rpc(client, "alice", "tools/call", get_profile)
    assert SECRETS["alice"] in alice

    bob = _rpc(client, "bob", "tools/call", get_profile)
    assert SECRETS["alice"] not in bob
    assert SECRETS["bob"] in bob

    bob_tools = _rpc(client, "bob", "tools/list")
    assert SECRETS["alice"] not in bob_tools


def test_mcpi002_layout_function_values_are_per_user():
    app = Dash(__name__, enable_mcp=True, suppress_callback_exceptions=True)
    configure_mcp_server(cache_by=[lambda: flask.g.user])

    def serve_layout():
        user = getattr(flask.g, "user", None) if flask.has_app_context() else None
        return html.Div(
            [dcc.Input(id="apikey", value=SECRETS.get(user, "")), html.Div(id="out")]
        )

    app.layout = serve_layout
    _add_basic_auth(app)

    @app.callback(Output("out", "children"), Input("apikey", "value"))
    def use_key(apikey):
        return "ok" if apikey else "no key"

    client = app.server.test_client()
    assert SECRETS["alice"] in _rpc(client, "alice", "tools/list")

    bob_tools = _rpc(client, "bob", "tools/list")
    assert SECRETS["alice"] not in bob_tools
    assert SECRETS["bob"] in bob_tools


def test_mcpi003_cache_is_reused_across_requests():
    app = Dash(__name__, enable_mcp=True)
    app.layout = html.Div([dcc.Input(id="in", value="x"), html.Div(id="out")])
    _add_basic_auth(app)
    runs = []

    @app.callback(Output("out", "children"), Input("in", "value"))
    def echo(value):
        runs.append(value)
        return value

    client = app.server.test_client()
    get_out = {"name": "get_dash_component", "arguments": {"component_id": "out"}}
    _rpc(client, "alice", "tools/call", get_out)
    _rpc(client, "bob", "tools/call", get_out)
    _rpc(client, "alice", "tools/list")
    assert len(runs) == 1


def test_mcpi004_failing_cache_by_returns_error():
    app = Dash(__name__, enable_mcp=True)
    app.layout = html.Div([dcc.Input(id="in", value="x"), html.Div(id="out")])
    _add_basic_auth(app)

    def broken():
        raise KeyError("no user")

    configure_mcp_server(cache_by=broken)

    @app.callback(Output("out", "children"), Input("in", "value"))
    def echo(value):
        return value

    body = json.loads(_rpc(app.server.test_client(), "alice", "tools/list"))
    assert body["error"]["code"] == -32603
    assert "result" not in body


@pytest.mark.parametrize("maxsize, expected_runs", [(1, 3), (None, 2)])
def test_mcpi005_cache_maxsize(maxsize, expected_runs):
    app = Dash(__name__, enable_mcp=True)
    app.layout = html.Div([dcc.Input(id="in", value="x"), html.Div(id="out")])
    _add_basic_auth(app)
    configure_mcp_server(cache_by=lambda: flask.g.user, cache_maxsize=maxsize)
    runs = []

    @app.callback(Output("out", "children"), Input("in", "value"))
    def echo(value):
        runs.append(value)
        return value

    client = app.server.test_client()
    get_out = {"name": "get_dash_component", "arguments": {"component_id": "out"}}
    for user in ("alice", "bob", "alice"):
        _rpc(client, user, "tools/call", get_out)
    assert len(runs) == expected_runs
