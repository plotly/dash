import time

import dash
from dash import Dash, html


def _make_app():
    app = Dash(__name__, use_pages=True, pages_folder="")
    dash.register_page("home", path="/", layout=html.Div("home"))
    dash.register_page(
        "asset",
        path_template="/asset/<asset_id>/view",
        layout=lambda asset_id=None, **_: html.Div(f"asset:{asset_id}", id="asset-out"),
    )
    dash.register_page(
        "cmp",
        path_template="/cmp/<a>/<b>/<c>/view",
        layout=lambda a=None, b=None, c=None, **_: html.Div(f"cmp:{a},{b},{c}"),
    )
    app.layout = html.Div(dash.page_container)
    return app


def _route(client, pathname):
    body = {
        "output": ".._pages_content.children..._pages_store.data..",
        "outputs": [
            {"id": "_pages_content", "property": "children"},
            {"id": "_pages_store", "property": "data"},
        ],
        "inputs": [
            {"id": "_pages_location", "property": "pathname", "value": pathname},
            {"id": "_pages_location", "property": "search", "value": ""},
        ],
        "changedPropIds": ["_pages_location.pathname"],
        "state": [],
    }
    start = time.time()
    r = client.post("/_dash-update-component", json=body)
    return r, time.time() - start


def test_pgpt001_path_template_variables(dash_duo):
    app = _make_app()
    dash_duo.start_server(app)
    dash_duo.wait_for_page(f"{dash_duo.server_url}/asset/a1/view")
    dash_duo.wait_for_text_to_equal("#asset-out", "asset:a1")
    assert dash_duo.get_logs() == []


def test_pgpt002_newline_pathname_is_rejected_fast():
    app = _make_app()
    client = app.server.test_client()
    client.get("/")

    r, _ = _route(client, "/asset/a\nb/view")
    assert r.status_code == 200

    r, elapsed = _route(client, "/cmp/" + "/" * 2000 + "\n/view")
    assert r.status_code == 200
    assert elapsed < 1

    r, _ = _route(client, "/cmp/x/y/z/view")
    assert "cmp:x,y,z" in r.get_data(as_text=True)
