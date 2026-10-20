import json
import re
import tempfile
import time

import pytest

from dash import Dash, DiskcacheManager, Input, Output, callback_context, dcc, html

diskcache = pytest.importorskip("diskcache")


def _end_id(client):
    index = client.get("/").get_data(as_text=True)
    config = re.search(r'id="_dash-config"[^>]*>(.*?)</script>', index, re.S)
    return json.loads(config.group(1))["end_id"]


def _body(name):
    return {
        "output": f"out-{name}.children",
        "outputs": {"id": f"out-{name}", "property": "children"},
        "inputs": [{"id": f"in-{name}", "property": "value", "value": "go"}],
        "changedPropIds": [f"in-{name}.value"],
        "state": [],
    }


def _start(client, end_id, body):
    return client.post(
        "/_dash-update-component", json=body, query_string={"endId": end_id}
    ).get_json()


def _poll(client, end_id, body, handles):
    query = {"endId": end_id, "cacheKey": handles["cacheKey"], "job": handles["job"]}
    r = client.post("/_dash-update-component", json=body, query_string=query)
    return r.get_data(as_text=True)


def _poll_until_done(client, end_id, body, handles):
    for _ in range(50):
        out = _poll(client, end_id, body, handles)
        if '"response"' in out:
            return out
        time.sleep(0.2)
    raise AssertionError("background callback never finished")


def test_bgiso001_equal_inputs_do_not_share_results():
    manager = DiskcacheManager(diskcache.Cache(tempfile.mkdtemp()))
    app = Dash(__name__, background_callback_manager=manager)
    app.layout = html.Div(
        [dcc.Input(id="in-report", value="go"), html.Div(id="out-report")]
    )

    @app.callback(
        Output("out-report", "children"),
        Input("in-report", "value"),
        background=True,
        prevent_initial_call=True,
    )
    def report(_value):
        return f"report for {callback_context.cookies.get('user')}"

    alice = app.server.test_client()
    alice.set_cookie("user", "alice")
    mallory = app.server.test_client()
    mallory.set_cookie("user", "mallory")
    alice_end, mallory_end = _end_id(alice), _end_id(mallory)
    body = _body("report")

    alice_handles = _start(alice, alice_end, body)
    time.sleep(1.5)

    mallory_handles = _start(mallory, mallory_end, body)
    assert mallory_handles["cacheKey"] != alice_handles["cacheKey"]
    assert "alice" not in _poll_until_done(mallory, mallory_end, body, mallory_handles)

    assert "report for alice" in _poll_until_done(alice, alice_end, body, alice_handles)


def test_bgiso002_callbacks_from_one_factory_do_not_share_results():
    manager = DiskcacheManager(
        diskcache.Cache(tempfile.mkdtemp()), cache_by=[lambda: "fixed"]
    )
    app = Dash(__name__, background_callback_manager=manager)
    tables = {"public": "public stats", "admin": "admin payroll"}
    app.layout = html.Div(
        [
            dcc.Input(id="in-public", value="go"),
            html.Div(id="out-public"),
            dcc.Input(id="in-admin", value="go"),
            html.Div(id="out-admin"),
        ]
    )

    def make(name):
        @app.callback(
            Output(f"out-{name}", "children"),
            Input(f"in-{name}", "value"),
            background=True,
            prevent_initial_call=True,
        )
        def render(_value):
            return tables[name]

    make("admin")
    make("public")

    client = app.server.test_client()
    end_id = _end_id(client)

    admin = _start(client, end_id, _body("admin"))
    assert "admin payroll" in _poll_until_done(client, end_id, _body("admin"), admin)

    public = _start(client, end_id, _body("public"))
    assert public["cacheKey"] != admin["cacheKey"]
    out = _poll_until_done(client, end_id, _body("public"), public)
    assert "public stats" in out
    assert "admin payroll" not in out
